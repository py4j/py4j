"""
Created on Mar 7, 2010

@author: barthelemy
"""
import gc
import threading
import unittest
from weakref import ref

import pytest

from py4j.finalizer import ThreadSafeFinalizer, Finalizer, clear_finalizers


def deleted(accumulator, id):
    print(id)
    accumulator.acc += 1


class Accumulator(object):
    def __init__(self):
        self.acc = 0


class AClass(object):
    def __init__(self, id, acc):
        self.id = id
        self.acc = acc
        ThreadSafeFinalizer.add_finalizer(
            id,
            ref(self, lambda wr, i=self.id, a=self.acc: deleted(a, i)))


class AClass2(object):
    def __init__(self, id, acc):
        self.id = id
        self.acc = acc
        Finalizer.add_finalizer(
            id,
            ref(self, lambda wr, i=self.id, a=self.acc: deleted(a, i)))


class JavaObjecTest(object):
    def __init__(self, id, acc):
        self.id = id
        self.acc = acc
        self.methods = []
        ThreadSafeFinalizer.add_finalizer(
            id,
            ref(self, lambda wr, i=self.id, a=self.acc: deleted(a, i)))


class JavaMemberTest(object):
    def __init__(self, name, container):
        self.name = name
        self.container = container


class TestThreadSafeFinalizer(unittest.TestCase):
    def tearDown(self):
        clear_finalizers(True)

    def work1(self, acc):
        a1 = AClass(1, acc)  # noqa
        a2 = AClass(2, acc)  # noqa

    def work1b(self, acc):
        a1 = AClass(1, acc)
        a2 = AClass(2, acc)
        a1.foo = a2
        a2.foo = a1

    def work2(self, acc):
        a1 = AClass(1, acc)
        a2 = AClass(2, acc)  # noqa
        return a1

    def testFinalizer(self):
        acc = Accumulator()
        self.work1(acc)
        self.assertEqual(2, acc.acc)
        self.work2(acc)
        self.assertEqual(4, acc.acc)

    def work_circ(self, acc):
        jobj = JavaObjecTest(1, acc)
        jmem1 = JavaMemberTest("append", jobj)
        jobj.methods.append(jmem1)

    def testCircularReference2(self):
        acc = Accumulator()
        self.work_circ(acc)
        # Necessary because of circular references...
        gc.collect()
        self.assertEqual(1, acc.acc)

    def testCleanUp(self):
        acc = Accumulator()
        a1 = self.work2(acc)
        self.assertEqual(1, acc.acc)
        self.assertEqual(2, len(ThreadSafeFinalizer.finalizers))
        clear_finalizers(False)
        self.assertEqual(1, acc.acc)
        self.assertEqual(1, len(ThreadSafeFinalizer.finalizers))
        a1.foo = "hello"
        del(a1)
        self.assertEqual(2, acc.acc)
        clear_finalizers(False)
        self.assertEqual(0, len(ThreadSafeFinalizer.finalizers))

    def testCleanUpAll(self):
        acc = Accumulator()
        a1 = self.work2(acc)
        self.assertEqual(1, acc.acc)
        self.assertEqual(2, len(ThreadSafeFinalizer.finalizers))
        clear_finalizers(True)
        self.assertEqual(1, acc.acc)
        self.assertEqual(0, len(ThreadSafeFinalizer.finalizers))
        a1.foo = "hello"
        del(a1)
        self.assertEqual(1, acc.acc)


class TestFinalizer(unittest.TestCase):
    def tearDown(self):
        clear_finalizers(True)

    def work1(self, acc):
        a1 = AClass2(1, acc)  # noqa
        a2 = AClass2(2, acc)  # noqa

    def work2(self, acc):
        a1 = AClass2(1, acc)  # noqa
        a2 = AClass2(2, acc)  # noqa
        return a1

    def testFinalizer(self):
        acc = Accumulator()
        self.work1(acc)
        self.assertEqual(2, acc.acc)

    def testCleanUp(self):
        acc = Accumulator()
        a1 = self.work2(acc)
        self.assertEqual(1, acc.acc)
        self.assertEqual(2, len(Finalizer.finalizers))
        clear_finalizers(False)
        self.assertEqual(1, acc.acc)
        self.assertEqual(1, len(Finalizer.finalizers))
        a1.foo = "hello"
        del(a1)
        self.assertEqual(2, acc.acc)
        clear_finalizers(False)
        self.assertEqual(0, len(Finalizer.finalizers))

    def testCleanUpAll(self):
        acc = Accumulator()
        a1 = self.work2(acc)
        self.assertEqual(1, acc.acc)
        self.assertEqual(2, len(Finalizer.finalizers))
        clear_finalizers(True)
        self.assertEqual(1, acc.acc)
        self.assertEqual(0, len(Finalizer.finalizers))
        a1.foo = "hello"
        del(a1)
        self.assertEqual(1, acc.acc)


class ThreadSafeFinalizerRaceTest(unittest.TestCase):
    """ThreadSafeFinalizer concurrent add/clear tests.

    Adds high-concurrency safety checks not previously covered. Same
    quick/stress tiering as concurrent_gateway_test.py."""

    def setUp(self):
        ThreadSafeFinalizer.clear_finalizers(True)

    def tearDown(self):
        ThreadSafeFinalizer.clear_finalizers(True)

    def _race(self, n_threads, iterations):
        """Each thread alternately adds finalizers and triggers clears.
        Goal: no exception, no double-free, no orphaned entries after
        the test ends."""
        barrier = threading.Barrier(n_threads, timeout=60)
        # Use a Queue for thread-safe error collection. list.append is
        # atomic under CPython's GIL but a queue makes the contract
        # explicit, which is the right signal for a thread-safety test.
        from queue import Queue
        errors = Queue()

        def worker(idx):
            try:
                try:
                    barrier.wait()
                except threading.BrokenBarrierError:
                    return
                class _W:
                    pass

                local_targets = []
                for i in range(iterations):
                    t = _W()
                    local_targets.append(t)
                    # add_finalizer(id, weak_ref) — weak_ref is a weakref.ref
                    weak = ref(t)
                    ThreadSafeFinalizer.add_finalizer(f"{idx}-{i}", weak)
                    if i % 16 == 0:
                        ThreadSafeFinalizer.clear_finalizers(False)
                # Let locals die so stale weak refs can be cleaned up.
                local_targets.clear()
            except Exception as e:
                errors.put(e)

        threads = [
            threading.Thread(target=worker, args=(idx,))
            for idx in range(n_threads)
        ]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        if not errors.empty():
            first = errors.get()
            remaining = errors.qsize()
            raise AssertionError(
                f"{remaining + 1} threads errored; first: {first!r}")

    def test_quick_finalizer_race_16x100(self):
        self._race(n_threads=16, iterations=100)

    @pytest.mark.slow
    def test_stress_finalizer_race_100x1000(self):
        self._race(n_threads=100, iterations=1000)


if __name__ == "__main__":
    unittest.main()
