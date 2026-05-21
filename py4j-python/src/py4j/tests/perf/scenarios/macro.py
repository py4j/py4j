"""Macro scenarios X1-X6: aggregate throughput and concurrency workloads.

Each scenario is a ``MacroScenario`` subclass. The runner (``perf.runner``)
calls ``setup`` once per fresh JVM and ``measure`` per round.

Scenario IDs with size/concurrency variants are split so the report shows
scaling curves: ``X1-1, X1-4, X1-16`` instead of a single ``X1``.
"""

import threading

from py4j.tests.perf.runner import MacroScenario


# ===================================================================== X1
# Concurrent calls: measure connection-pool scaling efficiency. Total
# work (10,000 calls) is held constant across thread counts so the
# delta between N=1 and N=16 reflects pool contention, not raw throughput.

class _X1ConcurrentBase(MacroScenario):
    total_calls = 10_000
    n_threads = 1

    @property
    def iterations_per_round(self):
        return self.total_calls

    def measure(self, gateway):
        calls_per_thread = self.total_calls // self.n_threads
        # currentTimeMillis() bound method is cached once so the reflection
        # cost isn't included in every-thread setup.
        fn = gateway.jvm.java.lang.System.currentTimeMillis

        def worker():
            for _ in range(calls_per_thread):
                fn()

        threads = [threading.Thread(target=worker)
                   for _ in range(self.n_threads)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()


class X1_1Thread(_X1ConcurrentBase):
    id = "X1-1"
    name = "concurrent_1_thread"
    n_threads = 1


class X1_4Thread(_X1ConcurrentBase):
    id = "X1-4"
    name = "concurrent_4_threads"
    n_threads = 4


class X1_16Thread(_X1ConcurrentBase):
    id = "X1-16"
    name = "concurrent_16_threads"
    n_threads = 16


# ===================================================================== X2
# JavaList iteration: the classic O(N) round-trip pattern. Iterating
# a JavaList calls JavaIterator.next() once per element, so cost scales
# linearly with list size. This scenario is the direct target of the
# bulk-fetch optimization listed in the perf analysis.

class _X2IterateBase(MacroScenario):
    size = 1_000
    # Approximate per-iteration wire bytes for a single list-element
    # fetch over the py4j socket protocol: a few-tens-of-bytes request
    # ("c\n<obj-id>\nget\ni<idx>\ne\n") + a small response ("yi<val>\n").
    # Used to derive bandwidth (bytes/sec) in the report — useful for
    # comparing TCP-level optimizations (TCP_NODELAY, batched calls,
    # protocol-overhead reductions). Exact byte count varies with
    # object-id length and value width; 50 is a defensible mid-range
    # estimate. Tune per-scenario if you instrument the actual byte
    # count later.
    bytes_per_iteration = 50

    @property
    def iterations_per_round(self):
        return self.size

    def setup(self, gateway):
        # Build the list once per JVM. Using ArrayList of ints.
        self._list = gateway.jvm.java.util.ArrayList()
        for i in range(self.size):
            self._list.append(i)

    def measure(self, gateway):
        acc = 0
        for x in self._list:
            acc ^= x
        # acc touched so the optimizer doesn't elide the loop.
        self._acc = acc


class X2_1k(_X2IterateBase):
    id = "X2-1k"
    name = "iterate_javalist_1k"
    size = 1_000
    # 1k iteration is ~38 ms - too short for scheduler jitter to average
    # out within a single timed sample. 10 repeats per round -> ~380 ms
    # timed sample, brings noise into single-digit %.
    repeats_per_round = 10


class X2_10k(_X2IterateBase):
    id = "X2-10k"
    name = "iterate_javalist_10k"
    size = 10_000


class X2_100k(_X2IterateBase):
    id = "X2-100k"
    name = "iterate_javalist_100k"
    size = 100_000


# ===================================================================== X3
# ListConverter.convert: converting a Python list -> Java ArrayList.
# Currently one add() RPC per element. A bulk constructor or addAll
# call would collapse N round-trips to 1.

class _X3ConvertBase(MacroScenario):
    size = 100
    # Approximate per-iteration wire bytes for one add() call against
    # a remote ArrayList: request "c\n<list-id>\nadd\ni<val>\ne\n" plus
    # acknowledgement "yv\n". Tighter than X2 because the response is
    # a void/null marker rather than a value, but the request includes
    # the longer list-object id. 45 is a defensible mid-range estimate.
    bytes_per_iteration = 45

    @property
    def iterations_per_round(self):
        return self.size

    def setup(self, gateway):
        from py4j.java_collections import ListConverter
        self._converter = ListConverter()
        self._client = gateway._gateway_client
        self._data = list(range(self.size))

    def measure(self, gateway):
        self._converter.convert(self._data, self._client)


class X3_100(_X3ConvertBase):
    id = "X3-100"
    name = "listconverter_100"
    size = 100
    # 100-element conversion is ~8 ms - 20 repeats -> ~160 ms timed
    # sample, well above scheduler granularity.
    repeats_per_round = 20


class X3_1k(_X3ConvertBase):
    id = "X3-1k"
    name = "listconverter_1k"
    size = 1_000
    # 1k conversion is ~40 ms - 10 repeats -> ~400 ms.
    repeats_per_round = 10


class X3_10k(_X3ConvertBase):
    id = "X3-10k"
    name = "listconverter_10k"
    size = 10_000


# ===================================================================== X4
# Callback throughput: Collections.sort on a list of Python objects
# that implement java.lang.Comparable. Each compare triggers a Java->
# Python callback. Sorting N items triggers ~N log N callbacks.

class ComparablePython(object):
    """Python object exposing java.lang.Comparable via Py4j proxy."""

    def __init__(self, value):
        self.value = value

    def compareTo(self, other):
        if other is None:
            return self.value
        return self.value - other.compareTo(None)

    class Java:
        implements = ["java.lang.Comparable"]


class X4_Callbacks(MacroScenario):
    id = "X4"
    name = "callback_sort_100_items"
    enable_callbacks = True
    list_size = 100
    iterations_per_round = 100  # one sort per round; size * log2 size
                                # callbacks roughly
    # One sort is ~22 ms - 10 repeats -> ~220 ms timed round,
    # noise drops below 5%.
    repeats_per_round = 10

    def setup(self, gateway):
        # Build a fresh list each round inside measure(); setup only
        # captures bound method references for speed.
        self._ArrayList = gateway.jvm.java.util.ArrayList
        self._sort = gateway.jvm.java.util.Collections.sort

    def measure(self, gateway):
        # Fresh list per round: sort is in-place and subsequent sorts
        # on an already-sorted list would take a different code path.
        items = [ComparablePython(i)
                 for i in range(self.list_size, 0, -1)]
        al = self._ArrayList()
        for item in items:
            al.append(item)
        self._sort(al)


# ===================================================================== X5
# Error-path latency: measure the cost of handling a Java exception.
# The ExampleApplication entry point exposes `divideBy(0)` via the
# default entry-point class which throws ArithmeticException.

from py4j.protocol import Py4JJavaError


class X5_ErrorPath(MacroScenario):
    id = "X5"
    name = "error_path_latency"
    iterations_per_round = 1_000

    def setup(self, gateway):
        # Use ArrayList.get(-1) to trigger IndexOutOfBoundsException cheaply.
        self._list = gateway.jvm.java.util.ArrayList()

    def measure(self, gateway):
        lst = self._list
        for _ in range(self.iterations_per_round):
            try:
                lst.get(-1)
            except Py4JJavaError:
                pass


# ===================================================================== X6
# Pool saturation: high-concurrency tail-latency measurement. The
# design doc called for a "pool sized 4" constraint; py4j's default
# GatewayClient grows its pool on demand so we rely on 50 concurrent
# threads creating contention naturally. Per-call latencies are
# collected so the report shows p95/p99 under load.

class X6_PoolSaturation(MacroScenario):
    id = "X6"
    name = "pool_saturation_50_threads"
    n_threads = 50
    calls_per_thread = 20
    iterations_per_round = n_threads * calls_per_thread
    # 50-thread burst is ~20 ms - 5 repeats -> ~100 ms timed round.
    repeats_per_round = 5

    def measure(self, gateway):
        fn = gateway.jvm.java.lang.System.currentTimeMillis

        def worker():
            for _ in range(self.calls_per_thread):
                fn()

        threads = [threading.Thread(target=worker)
                   for _ in range(self.n_threads)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()


# ===================================================================== X7
# Bytes round-trip RECV: exercises decode_bytearray on the recv path.
# Java returns a byte[]; py4j routes it through OUTPUT_CONVERTER[BYTES_TYPE]
# → decode_bytearray, which base64-decodes the ASCII wire payload back
# to bytes. Without this scenario, decode_bytearray improvements (e.g.
# issue #570's ~7.5x speedup on 256KB payloads) are invisible to
# CodSpeed — every prior macro returns int / list / void / callback.

class _X7BytesRoundtripBase(MacroScenario):
    size = 1_024  # bytes per call
    iterations_per_round = 100
    bytes_per_iteration = property(lambda self: self.size)

    def setup(self, gateway):
        # Allocate a ByteBuffer once. It stays as a JavaObject because
        # ByteBuffer has no Python equivalent (unlike byte[]/String,
        # which py4j auto-converts on return). Each .array() call below
        # round-trips the backing byte[] over the wire — py4j returns
        # it via BYTES_TYPE and decodes via decode_bytearray, exactly
        # the recv-side path optimized in issue #570.
        self._buf = gateway.jvm.java.nio.ByteBuffer.allocate(self.size)

    def measure(self, gateway):
        buf = self._buf
        for _ in range(self.iterations_per_round):
            buf.array()


class X7_1k(_X7BytesRoundtripBase):
    id = "X7-1k"
    name = "bytes_roundtrip_1k"
    size = 1_024


class X7_16k(_X7BytesRoundtripBase):
    id = "X7-16k"
    name = "bytes_roundtrip_16k"
    size = 16 * 1_024


class X7_256k(_X7BytesRoundtripBase):
    id = "X7-256k"
    name = "bytes_roundtrip_256k"
    size = 256 * 1_024
    # Larger payloads → fewer iterations to keep the round bounded.
    iterations_per_round = 25


# ===================================================================== X8
# Bytes SEND: Python -> Java byte[] payload throughput. Complements X7
# (bytes recv). Each iteration sends `size` bytes via
# ByteArrayOutputStream.write(byte[], int, int). py4j encodes Python
# bytes as BYTES_TYPE on the wire; Java decodes and writes into the
# BAOS. The BAOS is reset between iterations so memory stays bounded.
#
# Exercises the Python-side encode_bytearray path (mirror of X7's
# Java-side encode + Python-side decode_bytearray exercised in X7).
# Same Nagle write-write-read sensitivity at sizes that exceed the
# BufferedWriter buffer.

class _X8BytesSendBase(MacroScenario):
    size = 1_024  # bytes per call
    iterations_per_round = 100
    bytes_per_iteration = property(lambda self: self.size)

    def setup(self, gateway):
        # ByteArrayOutputStream is a JavaObject (not auto-converted
        # because it's not a known Python type). reset() between
        # iterations keeps it from growing unboundedly.
        self._baos = gateway.jvm.java.io.ByteArrayOutputStream(self.size)
        # Build the payload once Python-side; setup is not timed.
        self._payload = b"x" * self.size

    def measure(self, gateway):
        baos = self._baos
        payload = self._payload
        length = self.size
        for _ in range(self.iterations_per_round):
            baos.reset()
            # Force the write(byte[], int, int) overload by passing
            # the explicit offset/length triple — avoids any chance
            # of py4j picking write(int) for a 1-arg call.
            baos.write(payload, 0, length)


class X8_1k(_X8BytesSendBase):
    id = "X8-1k"
    name = "bytes_send_1k"
    size = 1_024


class X8_16k(_X8BytesSendBase):
    id = "X8-16k"
    name = "bytes_send_16k"
    size = 16 * 1_024


class X8_256k(_X8BytesSendBase):
    id = "X8-256k"
    name = "bytes_send_256k"
    size = 256 * 1_024
    iterations_per_round = 25


ALL_MACRO_CLASSES = [
    X1_1Thread, X1_4Thread, X1_16Thread,
    X2_1k, X2_10k, X2_100k,
    X3_100, X3_1k, X3_10k,
    X4_Callbacks,
    X5_ErrorPath,
    X6_PoolSaturation,
    X7_1k, X7_16k, X7_256k,
    X8_1k, X8_16k, X8_256k,
]
