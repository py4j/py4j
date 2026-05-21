"""Concurrent-gateway contention tests, tiered for CI cost.

QUICK variants (16 threads, 50 iterations) run on every CI cell and
catch obvious deadlocks / use-after-close races.

STRESS variants (100 threads, 1000 iterations) are gated behind
@pytest.mark.slow and run only on workflow_dispatch or weekly cron.
Both use threading.Barrier to start in lockstep — no time.sleep,
no flaky timing dependency.
"""
import threading
import unittest

import pytest

from py4j.java_gateway import JavaGateway
from py4j.tests.java_gateway_test import (
    start_example_app_process,
    safe_shutdown,
    safe_join,
)


def _hammer_gateway(gateway, iterations, barrier):
    """Worker function — wait at barrier, then call into JVM N times."""
    try:
        barrier.wait()
    except threading.BrokenBarrierError:
        return  # another thread errored before reaching the barrier
    for _ in range(iterations):
        gateway.jvm.java.lang.System.currentTimeMillis()


class ConcurrentGatewayTest(unittest.TestCase):

    def setUp(self):
        self.p = start_example_app_process()
        self.gateway = JavaGateway()

    def tearDown(self):
        safe_shutdown(self)
        safe_join(self.p)

    def _run_concurrent(self, n_threads, iterations):
        barrier = threading.Barrier(n_threads, timeout=60)
        errors = []

        def worker():
            try:
                _hammer_gateway(self.gateway, iterations, barrier)
            except Exception as e:
                errors.append(e)

        threads = [threading.Thread(target=worker) for _ in range(n_threads)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        if errors:
            raise AssertionError(
                f"{len(errors)} threads errored; first: {errors[0]!r}")

    def test_quick_concurrent_16x50(self):
        """16 threads x 50 calls = 800 calls. Default CI tier."""
        self._run_concurrent(n_threads=16, iterations=50)

    @pytest.mark.slow
    def test_stress_concurrent_100x1000(self):
        """100 threads x 1000 calls = 100,000 calls. workflow_dispatch only."""
        self._run_concurrent(n_threads=100, iterations=1000)
