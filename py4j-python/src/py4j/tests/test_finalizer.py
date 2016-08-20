# -*- coding: UTF-8 -*-
from __future__ import unicode_literals, absolute_import

import gc
from weakref import ref

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


class JavaObjecMock(object):
    def __init__(self, id, acc):
        self.id = id
        self.acc = acc
        self.methods = []
        ThreadSafeFinalizer.add_finalizer(
            id,
            ref(self, lambda wr, i=self.id, a=self.acc: deleted(a, i)))


class JavaMemberMock(object):
    def __init__(self, name, container):
        self.name = name
        self.container = container


def work1(acc):
    a1 = AClass(1, acc)  # noqa
    a2 = AClass(2, acc)  # noqa


def work1b(acc):
    a1 = AClass(1, acc)
    a2 = AClass(2, acc)
    a1.foo = a2
    a2.foo = a1


def work2(acc):
    a1 = AClass(1, acc)
    a2 = AClass(2, acc)  # noqa
    return a1


def work_circ(acc):
    jobj = JavaObjecMock(1, acc)
    jmem1 = JavaMemberMock("append", jobj)
    jobj.methods.append(jmem1)


def work3(acc):
    a1 = AClass2(1, acc)  # noqa
    a2 = AClass2(2, acc)  # noqa


def work4(acc):
    a1 = AClass2(1, acc)  # noqa
    a2 = AClass2(2, acc)  # noqa
    return a1


def teardown_function(function):
    """Pytest teardown
    """
    clear_finalizers(True)


def test_tsafe_finalizer():
    acc = Accumulator()
    work1(acc)
    assert 2 == acc.acc
    work2(acc)
    assert 4 == acc.acc


def test_tsafe_circular_reference():
    acc = Accumulator()
    work_circ(acc)
    # Necessary because of circular references...
    gc.collect()
    assert 1 == acc.acc


def test_tsafe_cleanup():
    acc = Accumulator()
    a1 = work2(acc)
    assert 1 == acc.acc
    assert 2 == len(ThreadSafeFinalizer.finalizers)
    clear_finalizers(False)
    assert 1 == acc.acc
    assert 1 == len(ThreadSafeFinalizer.finalizers)
    a1.foo = "hello"
    del(a1)
    assert 2 == acc.acc
    clear_finalizers(False)
    assert 0 == len(ThreadSafeFinalizer.finalizers)


def test_tsafe_cleanup_all():
    acc = Accumulator()
    a1 = work2(acc)
    assert 1 == acc.acc
    assert 2 == len(ThreadSafeFinalizer.finalizers)
    clear_finalizers(True)
    assert 1 == acc.acc
    assert 0 == len(ThreadSafeFinalizer.finalizers)
    a1.foo = "hello"
    del(a1)
    assert 1 == acc.acc


def test_finalizer():
    acc = Accumulator()
    work3(acc)
    assert 2 == acc.acc


def test_cleanup():
    acc = Accumulator()
    a1 = work4(acc)
    assert 1 == acc.acc
    assert 2 == len(Finalizer.finalizers)
    clear_finalizers(False)
    assert 1 == acc.acc
    assert 1 == len(Finalizer.finalizers)
    a1.foo = "hello"
    del(a1)
    assert 2 == acc.acc
    clear_finalizers(False)
    assert 0 == len(Finalizer.finalizers)


def test_cleanup_all():
    acc = Accumulator()
    a1 = work4(acc)
    assert 1 == acc.acc
    assert 2 == len(Finalizer.finalizers)
    clear_finalizers(True)
    assert 1 == acc.acc
    assert 0 == len(Finalizer.finalizers)
    a1.foo = "hello"
    del(a1)
    assert 1 == acc.acc
