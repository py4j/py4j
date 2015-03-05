from __future__ import unicode_literals, absolute_import


from py4j.java_gateway import JavaGateway, GatewayParameters, java_import,\
    UserHelpAutoCompletion
from py4j.tests.java_gateway_test import (
    start_example_app_process)
from contextlib import contextmanager
from nose.tools import eq_

ExampleClassFields = sorted([
                      "field10",
                      "field11",
                      "field20",
                      "field21",
                      "static_field"
                      ])

ExampleClassMethods = sorted([
                      # From ExampleClass
                      "method1",
                      "method2",
                      "method3",
                      "method4",
                      "method5",
                      "method6",
                      "method7", # overloaded
                      "method8",
                      "method9",
                      "method10", # overloaded
                      "method11",
                      "getList",
                      "getField1",
                      "setField1",
                      "getStringArray",
                      "getIntArray",
                      "callHello",
                      "callHello2",
                      "static_method",

                      # From Object
                      "getClass",
                      "hashCode",
                      "equals",
                      "toString",
                      "notify",
                      "notifyAll",
                      "wait"
                      ])

ExampleClassStatics = sorted([
                              "StaticClass",
                              "static_field",
                              "static_method"
                              ])

@contextmanager
def example_app_process():
    p = start_example_app_process()
    try:
        yield p
    finally:
        p.join()

@contextmanager
def gateway(*args, **kwargs):
    g = JavaGateway(
        gateway_parameters=GatewayParameters(*args, auto_convert=True, **kwargs))
    lineSep = g.jvm.System.lineSeparator()
    try:
        yield g
        # Call a dummy method to make sure we haven't corrupted the streams
        eq_(lineSep, g.jvm.System.lineSeparator())
    finally:
        g.shutdown()

def test_dir_object():
    with example_app_process():
        with gateway() as g:
            ex = g.getNewExample()
            eq_(sorted(dir(ex)), ExampleClassMethods)

def test_dir_object_fields():
    with example_app_process():
        with gateway(auto_field=True) as g:
            ex = g.getNewExample()
            eq_(sorted(dir(ex)), sorted(ExampleClassMethods + ExampleClassFields))

def test_dir_object_shows_manually_called_after_dir():
    with example_app_process():
        with gateway() as g:
            ex = g.getNewExample()
            eq_(sorted(dir(ex)), ExampleClassMethods)
            try:
                ex.does_not_exist_in_example()
                raise AssertionError("Method should not have succeeded")
            except:
                pass
            # Make sure the manually called method now shows up
            eq_(sorted(dir(ex)), sorted(ExampleClassMethods + ['does_not_exist_in_example']))

def test_dir_object_shows_manually_called_before_dir():
    with example_app_process():
        with gateway() as g:
            ex = g.getNewExample()
            try:
                ex.does_not_exist_in_example()
                raise AssertionError("Method should not have succeeded")
            except:
                pass
            # Make sure the manually called method now shows up
            eq_(sorted(dir(ex)), sorted(ExampleClassMethods + ['does_not_exist_in_example']))

def test_dir_class():
    with example_app_process():
        with gateway() as g:
            exclass = g.jvm.py4j.examples.ExampleClass
            eq_(sorted(dir(exclass)), ExampleClassStatics)

def helper_dir_jvmview(view):
    eq_(sorted(dir(view)), [UserHelpAutoCompletion.KEY])

    java_import(view, "com.example.Class1")
    java_import(view, "com.another.Class2")
    eq_(sorted(dir(view)), [UserHelpAutoCompletion.KEY, "Class1", "Class2"])
    eq_(sorted(dir(view)), [UserHelpAutoCompletion.KEY, "Class1", "Class2"])

    java_import(view, "com.third.Class3")
    eq_(sorted(dir(view)), [UserHelpAutoCompletion.KEY, "Class1", "Class2", "Class3"])

def test_dir_jvmview_default():
    with example_app_process():
        with gateway() as g:
            helper_dir_jvmview(g.jvm)

def test_dir_jvmview_new():
    with example_app_process():
        with gateway() as g:
            view = g.new_jvm_view()
            helper_dir_jvmview(view)

def test_dir_jvmview_two():
    with example_app_process():
        with gateway() as g:
            view1 = g.new_jvm_view()
            view2 = g.new_jvm_view()
            helper_dir_jvmview(view1)
            helper_dir_jvmview(view2)

            # now give them different contents
            java_import(view1, "com.fourth.Class4")
            java_import(view2, "com.fiftg.Class5")

            eq_(sorted(dir(view1)), [UserHelpAutoCompletion.KEY, "Class1", "Class2", "Class3", "Class4"])
            eq_(sorted(dir(view2)), [UserHelpAutoCompletion.KEY, "Class1", "Class2", "Class3", "Class5"])

def test_dir_package():
    with example_app_process():
        with gateway() as g:
            eq_(sorted(dir(g.jvm)), [UserHelpAutoCompletion.KEY])
            eq_(sorted(dir(g.jvm.java)), [UserHelpAutoCompletion.KEY])
            eq_(sorted(dir(g.jvm.java.util)), [UserHelpAutoCompletion.KEY])
