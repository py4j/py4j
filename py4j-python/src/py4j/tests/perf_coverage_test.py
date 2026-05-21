"""Comprehensive bandwidth / latency / cold-start coverage.

These tests are unit tests in form (run by `pytest`) but their primary
value is *measurement reporting*: each test prints throughput / latency
numbers that engineers use when investigating perf regressions and
when validating optimization PRs.

Existing perf coverage:
* The CodSpeed scenarios (`tests/perf/scenarios/codspeed_macros.py`)
  give continuous tracking on master commits — wall-time deltas per
  named scenario, published to the CodSpeed dashboard.
* The local perf framework (`py4j.tests.perf`) runs a richer set of
  M-micro and X-macro scenarios with structured comparison reports.

What this file adds:
* **Full cold-start latency** — wall time from `java` subprocess
  spawn through first JVM call returning. Issue #557 reported ~3 s
  on Python 3.11 / OpenJDK 17 / Ubuntu — JVM class loading dominates,
  but py4j's handshake contribution is part of the timed window too,
  so a regression in connect / auth / pool init shows up here.
* **py4j-handshake-only latency** — same as above minus the JVM
  spawn (which py4j cannot control). Time from `JavaGateway()`
  constructor to first call against an already-listening JVM.
  Isolates py4j's own contribution; <100 ms is normal.
* **First-call-vs-warm ratio** — same gateway, first call timing vs
  median of 100 subsequent calls. Catches regressions in the warm
  path's protocol-cache lookups, etc.
* **String-arg latency curve** — per-call latency at 16 / 256 / 4K /
  16K / 64K byte string arguments. Fills the gap between M2b (~5 B
  arg) and X7-style large-payload scenarios; surfaces the latency
  knee around the BufferedWriter buffer boundary.
* **Bandwidth summary (recv + send)** — MB/s at 1K / 16K / 256K for
  both directions (Java->Python byte[] return, Python->Java byte[]
  argument). Confirms the throughput numbers reported in the perf
  framework reports.

Tests print results and assert generous bounds — they catch dramatic
regressions (>10x) without being CI-flaky on hardware-dependent
absolute numbers. Run locally for investigation:

    cd py4j-python
    pytest src/py4j/tests/perf_coverage_test.py -v -s

The `-s` flag is important — without it pytest captures the prints.
"""
import os
import statistics
import time
import unittest

from py4j.java_gateway import JavaGateway, GatewayParameters
from py4j.tests.java_gateway_test import (
    PY4J_JAVA_PATH, PY4J_JAVA_PATHS,
    start_example_app_process, safe_shutdown, safe_join,
    safe_terminate_process)


def _time_calls(fn, n):
    """Return (samples_us, median_us) over n calls of fn()."""
    samples = []
    for _ in range(n):
        t0 = time.perf_counter()
        fn()
        samples.append((time.perf_counter() - t0) * 1e6)
    return samples, statistics.median(samples)


class ColdStartLatencyTest(unittest.TestCase):
    """Cold-start measurement — issue #557.

    Three measurements with progressively more of the cold path
    excluded so a regression can be localized to its cause:

    1. ``test_full_cold_start`` — fresh `java` subprocess + listening-
       socket wait + py4j handshake + first call. Includes JVM class
       loading (~2-3 s typical), which dominates the wall time. Issue
       #557's reported ~3 s scenario.

    2. ``test_py4j_handshake_under_500ms`` — JVM is already running
       and listening; only `JavaGateway()` + first call is timed.
       Isolates py4j's own contribution from JVM init.

    3. ``test_first_vs_warm_call_ratio`` — same gateway, first call
       vs median warm call. Catches regressions in the protocol-cache
       fill on the first call."""

    def test_full_cold_start(self):
        # End-to-end cold start: subprocess spawn -> JVM init ->
        # GatewayServer listening -> JavaGateway() -> first call.
        # JVM init is the dominant cost; this test exists so a regression
        # in py4j's spawn/handshake contribution is visible against the
        # JVM-dominated baseline. Issue #557 reported ~3 s here; this
        # test caps at 30 s to catch a catastrophic regression without
        # flaking on slow CI hardware.
        t0 = time.perf_counter()
        p = start_example_app_process()  # spawn + wait for listening
        gateway = None
        try:
            gateway = JavaGateway()
            gateway.jvm.java.lang.System.currentTimeMillis()
            cold_start_s = time.perf_counter() - t0
        finally:
            if gateway is not None:
                try:
                    gateway.shutdown()
                except Exception:
                    pass
            safe_join(p)

        print("\n  [full-cold-start] subprocess.Popen -> first call: "
              "{:.2f} s".format(cold_start_s))
        # 30 s is the catastrophic-regression threshold. Issue #557
        # reported 3 s as the user's lived experience; healthy CI
        # machines see 1-5 s depending on warm gradle cache, JVM
        # version, and OS scheduling.
        self.assertLess(
            cold_start_s, 30.0,
            "full cold start took {:.1f}s — catastrophic regression "
            "vs issue #557 baseline".format(cold_start_s))

    def test_py4j_handshake_under_500ms(self):
        # JVM is already listening; only py4j's contribution is timed.
        # This is the part py4j actually controls: socket connect + auth
        # handshake (if any) + first-call protocol exchange. Should be
        # well under 500 ms on any reasonable setup; tighter than the
        # full-cold-start test so a py4j-side handshake regression is
        # caught without being masked by JVM-warmup noise.
        p = start_example_app_process()
        gateway = None
        try:
            t0 = time.perf_counter()
            gateway = JavaGateway()
            gateway.jvm.java.lang.System.currentTimeMillis()
            handshake_ms = (time.perf_counter() - t0) * 1000
        finally:
            if gateway is not None:
                try:
                    gateway.shutdown()
                except Exception:
                    pass
            safe_join(p)

        print("\n  [py4j-handshake-only] gateway+first-call: "
              "{:.1f} ms".format(handshake_ms))
        self.assertLess(
            handshake_ms, 500,
            "py4j handshake-only cold path {:.0f}ms — regression in "
            "connect/auth/pool init".format(handshake_ms))

    def test_first_vs_warm_call_ratio(self):
        # Same gateway: time the very first call (cold protocol path),
        # then 100 subsequent calls (warm). Catches regressions in the
        # first-call cache fill vs warm path.
        p = start_example_app_process()
        gateway = None
        try:
            gateway = JavaGateway()
            fn = gateway.jvm.java.lang.System.currentTimeMillis

            t0 = time.perf_counter()
            fn()  # first call (cold)
            first_us = (time.perf_counter() - t0) * 1e6

            # Skip 5 more for warmup, then measure 100.
            for _ in range(5):
                fn()
            _, warm_median_us = _time_calls(fn, 100)
            ratio = first_us / warm_median_us if warm_median_us > 0 else 0
        finally:
            if gateway is not None:
                try:
                    gateway.shutdown()
                except Exception:
                    pass
            safe_join(p)

        print("\n  [first-vs-warm] first: {:.0f}us  warm-median: "
              "{:.1f}us  ratio: {:.1f}x".format(
                  first_us, warm_median_us, ratio))
        # 100x is a soft cap. Issue #557 reported ratios of multi-
        # thousand-x in their environment, dominated by JVM JIT
        # warmup we can't control. A regression in py4j itself would
        # blow well past 100x.
        self.assertLess(
            ratio, 100,
            "first/warm call ratio is {:.1f}x — possible regression "
            "in py4j cold path (issue #557)".format(ratio))


class StringArgLatencyCurveTest(unittest.TestCase):
    """Per-call latency as the string argument grows from M2b's tiny
    payload to X7-class large payloads. Surfaces the latency knee
    around the BufferedWriter buffer boundary (~8 KB) where Nagle's
    write-write-read pattern can hit on Linux.

    Method under test: a held `StringBuilder.append(str)`. py4j sends
    the string as STRING_TYPE; the return is the StringBuilder itself
    (a JavaObject reference — cheap), so this isolates the send-side
    encode cost from the recv-side decode cost."""

    def setUp(self):
        self.p = start_example_app_process()
        self.gateway = JavaGateway()
        self.sb = self.gateway.jvm.java.lang.StringBuilder()

    def tearDown(self):
        try:
            safe_shutdown(self)
        except Exception:
            pass
        safe_join(self.p)

    def test_latency_curve_across_payload_sizes(self):
        # Sizes spanning M2b's tiny case to just past the BufferedWriter
        # boundary, where Nagle effects start showing on Linux. Each
        # size gets 30 calls; median is reported.
        sizes = [16, 256, 4 * 1024, 16 * 1024, 64 * 1024]
        sb = self.sb
        results = []
        for size in sizes:
            payload = "x" * size
            sb.setLength(0)  # keep memory bounded between sizes
            # Warmup
            for _ in range(5):
                sb.append(payload)
                sb.setLength(0)

            def call_once(p=payload, _sb=sb):
                _sb.append(p)
                _sb.setLength(0)

            _, median_us = _time_calls(call_once, 30)
            results.append((size, median_us))

        print("\n  [string-arg latency curve]")
        for size, median_us in results:
            print("    {:>7} B arg: {:>8.1f} µs/call".format(
                size, median_us))

        # Sanity bound: even at 64 KB on a slow CI runner, a single call
        # should be well under 500 ms. Catches catastrophic regressions
        # (e.g. accidentally O(N^2) protocol code).
        worst = max(median_us for _, median_us in results)
        self.assertLess(
            worst, 500_000,
            "worst median latency {:.0f}us across sizes — "
            "catastrophic regression?".format(worst))


class BandwidthSummaryTest(unittest.TestCase):
    """End-to-end bytes-throughput summary, both directions.

    Reports MB/s at 1 K / 16 K / 256 K payloads for:
    * recv (Java->Python): java.nio.ByteBuffer.allocate(N).array()
    * send (Python->Java): byte[] argument to BAOS.write(byte[], int, int)

    Useful for sanity-checking #5 (decode_bytearray fix) and #6 (Nagle
    fix) deltas, and as a regression guard if a future refactor slows
    the byte codec."""

    def setUp(self):
        self.p = start_example_app_process()
        self.gateway = JavaGateway()

    def tearDown(self):
        try:
            safe_shutdown(self)
        except Exception:
            pass
        safe_join(self.p)

    def _bench_recv(self, size, iterations):
        buf = self.gateway.jvm.java.nio.ByteBuffer.allocate(size)
        for _ in range(5):  # warmup
            buf.array()
        t0 = time.perf_counter()
        for _ in range(iterations):
            buf.array()
        elapsed = time.perf_counter() - t0
        bytes_moved = size * iterations
        return bytes_moved / elapsed / (1024 * 1024)  # MB/s

    def _bench_send(self, size, iterations):
        baos = self.gateway.jvm.java.io.ByteArrayOutputStream(size)
        payload = b"x" * size
        for _ in range(5):  # warmup
            baos.reset()
            baos.write(payload, 0, size)
        t0 = time.perf_counter()
        for _ in range(iterations):
            baos.reset()
            baos.write(payload, 0, size)
        elapsed = time.perf_counter() - t0
        bytes_moved = size * iterations
        return bytes_moved / elapsed / (1024 * 1024)  # MB/s

    def test_bandwidth_summary(self):
        # Iterations scale inversely with size so per-direction wall
        # time stays under ~1 s on commodity hardware.
        sizes_iters = [
            (1 * 1024, 200),
            (16 * 1024, 50),
            (256 * 1024, 10),
        ]
        recv = []
        send = []
        for size, iters in sizes_iters:
            recv.append((size, self._bench_recv(size, iters)))
            send.append((size, self._bench_send(size, iters)))

        print("\n  [bandwidth summary]")
        print("    {:>9} {:>12} {:>12}".format("size", "recv MB/s", "send MB/s"))
        for (size, mbs_r), (_, mbs_s) in zip(recv, send):
            print("    {:>9} {:>12.1f} {:>12.1f}".format(
                "{}B".format(size), mbs_r, mbs_s))

        # Sanity bound: even on a slow CI runner with Nagle on, the
        # bandwidth at 256K should be > 0.1 MB/s (4.4s for 100x ~16K =
        # ~0.36 MB/s on the Nagle-hit case). 0.1 MB/s catches a real
        # protocol-layer regression but is loose enough to not flake.
        worst_recv = min(mbs for _, mbs in recv)
        worst_send = min(mbs for _, mbs in send)
        self.assertGreater(
            worst_recv, 0.1,
            "recv bandwidth floor {:.2f} MB/s — protocol regression?".format(
                worst_recv))
        self.assertGreater(
            worst_send, 0.1,
            "send bandwidth floor {:.2f} MB/s — protocol regression?".format(
                worst_send))
