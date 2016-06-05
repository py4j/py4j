from contextlib import contextmanager
import gc
from multiprocessing import Process
import subprocess
import threading
import unittest

from py4j.clientserver import (
    ClientServer, JavaParameters, PythonParameters)
from py4j.java_gateway import GatewayConnectionGuard, is_instance_of, \
    GatewayParameters, DEFAULT_PORT, DEFAULT_PYTHON_PROXY_PORT
from py4j.protocol import Py4JJavaError, smart_decode
from py4j.tests.java_callback_test import IHelloImpl
from py4j.tests.java_gateway_test import (
    PY4J_JAVA_PATH, check_connection, sleep)
from py4j.tests.py4j_callback_recursive_example import (
    PythonPing, HelloState)


def start_clientserver_example_server():
    subprocess.call([
        "java", "-Xmx512m", "-cp", PY4J_JAVA_PATH,
        "py4j.examples.SingleThreadApplication"])


def start_java_clientserver_example_server():
    subprocess.call([
        "java", "-Xmx512m", "-cp", PY4J_JAVA_PATH,
        "py4j.examples.SingleThreadClientApplication"])


def start_clientserver_example_app_process(start_java_client=False):
    # XXX DO NOT FORGET TO KILL THE PROCESS IF THE TEST DOES NOT SUCCEED
    if not start_java_client:
        p = Process(target=start_clientserver_example_server)
    else:
        p = Process(target=start_java_clientserver_example_server)
    p.start()
    sleep()
    check_connection()
    return p


@contextmanager
def clientserver_example_app_process(start_java_client=False):
    p = start_clientserver_example_app_process(start_java_client)
    try:
        yield p
    finally:
        p.join()


def start_java_multi_client_server_app():
    subprocess.call([
        "java", "-Xmx512m", "-cp", PY4J_JAVA_PATH,
        "py4j.examples.MultiClientServer"])


def start_java_multi_client_server_app_process():
    # XXX DO NOT FORGET TO KILL THE PROCESS IF THE TEST DOES NOT SUCCEED
    p = Process(target=start_java_multi_client_server_app)
    p.start()
    sleep()
    # test both gateways...
    check_connection(
        gateway_parameters=GatewayParameters(port=DEFAULT_PORT))
    check_connection(
        gateway_parameters=GatewayParameters(port=DEFAULT_PORT + 2))
    return p


@contextmanager
def java_multi_client_server_app_process():
    p = start_java_multi_client_server_app_process()
    try:
        yield p
    finally:
        p.join()


class IntegrationTest(unittest.TestCase):

    def testJavaClientPythonServer(self):
        hello_state = HelloState()
        client_server = ClientServer(
            JavaParameters(), PythonParameters(), hello_state)

        with clientserver_example_app_process(True):
            client_server.shutdown()

        # Check that Java correctly called Python
        self.assertEqual(2, len(hello_state.calls))
        self.assertEqual((None, None), hello_state.calls[0])
        self.assertEqual((2, "Hello World"), hello_state.calls[1])

    def testBasicJVM(self):
        with clientserver_example_app_process():
            client_server = ClientServer(
                JavaParameters(), PythonParameters())
            ms = client_server.jvm.System.currentTimeMillis()
            self.assertTrue(ms > 0)
            client_server.shutdown()

    def testStream(self):
        with clientserver_example_app_process():
            client_server = ClientServer(
                JavaParameters(), PythonParameters())
            e = client_server.entry_point.getNewExample()

            # not binary - just get the Java object
            v1 = e.getStream()
            self.assertTrue(
                is_instance_of(
                    client_server, v1,
                    "java.nio.channels.ReadableByteChannel"))

            # pull it as a binary stream
            with e.getStream.stream() as conn:
                self.assertTrue(isinstance(conn, GatewayConnectionGuard))
                expected =\
                    u"Lorem ipsum dolor sit amet, consectetur adipiscing elit."
                self.assertEqual(
                    expected, smart_decode(conn.read(len(expected))))
            client_server.shutdown()

    def testRecursionWithAutoGC(self):
        with clientserver_example_app_process():
            client_server = ClientServer(
                JavaParameters(auto_gc=True), PythonParameters(auto_gc=True))
            pingpong = client_server.jvm.py4j.examples.PingPong()
            ping = PythonPing()
            self.assertEqual(2, pingpong.start(ping))

            pingpong = client_server.jvm.py4j.examples.PingPong(True)

            try:
                pingpong.start(ping)
                self.fail()
            except Py4JJavaError:
                # TODO Make sure error are recursively propagated
                # Also a problem with old threading model.
                self.assertTrue(True)

            ping = PythonPing(True)
            pingpong = client_server.jvm.py4j.examples.PingPong(False)

            try:
                pingpong.start(ping)
                self.fail()
            except Py4JJavaError:
                # TODO Make sure error are recursively propagated
                # Also a problem with old threading model.
                self.assertTrue(True)

            client_server.shutdown()

    def testJavaGC(self):
        # This will only work with some JVM.
        with clientserver_example_app_process():
            client_server = ClientServer(
                JavaParameters(), PythonParameters())
            example = client_server.entry_point.getNewExample()
            impl = IHelloImpl()
            self.assertEqual("This is Hello!", example.callHello(impl))
            self.assertEqual(
                "This is Hello;\n10MyMy!\n;",
                example.callHello2(impl))
            self.assertEqual(2, len(client_server.gateway_property.pool))

            # Make sure that finalizers do not block by calling the Java
            # finalizer again
            impl2 = IHelloImpl()
            self.assertEqual("This is Hello!", example.callHello(impl2))
            self.assertEqual(3, len(client_server.gateway_property.pool))

            # The two PythonProxies should be evicted on the Java side
            # Java should tell python to release the references.
            client_server.jvm.java.lang.System.gc()

            # Leave time for sotimeout
            sleep(3)
            self.assertTrue(len(client_server.gateway_property.pool) < 2)
            client_server.shutdown()

    def testPythonGC(self):
        def internal_function(client_server):
            example = client_server.entry_point.getNewExample()
            in_middle = len(
                client_server.java_gateway_server.getGateway().getBindings())
            self.assertEqual(1, example.method1())

            # After this method is executed, Python no longer need
            # a reference to example and it should tell Java to release
            # the reference too
            return in_middle

        with clientserver_example_app_process():
            # This will only work with some JVM.
            client_server = ClientServer(
                JavaParameters(), PythonParameters())
            before = len(
                client_server.java_gateway_server.getGateway().getBindings())
            in_middle = internal_function(client_server)

            # Force Python to run garbage collection in case it did
            # not run yet.
            sleep()
            gc.collect()
            sleep()

            after = len(
                client_server.java_gateway_server.getGateway().getBindings())

            # Number of references on the Java side should be the same before
            # and after
            self.assertEqual(before, after)

            # Number of references when we created a JavaObject should be
            # higher than at the beginning.
            self.assertTrue(in_middle > before)
            client_server.shutdown()

    def testMultiClientServerWithSharedJavaThread(self):
        with java_multi_client_server_app_process():
            client_server0 = ClientServer(
                JavaParameters(), PythonParameters())
            client_server1 = ClientServer(
                JavaParameters(port=DEFAULT_PORT + 2),
                PythonParameters(port=DEFAULT_PYTHON_PROXY_PORT + 2))

            entry0 = client_server0.entry_point
            entry1 = client_server1.entry_point

            # set up the ability for Java to get the Python thread ids
            threadIdGetter0 = PythonGetThreadId(client_server0)
            threadIdGetter1 = PythonGetThreadId(client_server1)
            entry0.setPythonThreadIdGetter(threadIdGetter0)
            entry1.setPythonThreadIdGetter(threadIdGetter1)
            thisThreadId = threading.current_thread().ident

            # ## Preconditions

            # Make sure we are talking to two different Entry points on
            # Java side
            self.assertEqual(0, entry0.getEntryId())
            self.assertEqual(1, entry1.getEntryId())

            # ## 1 Hop to Shared Java Thread

            # Check that the shared Java thread is the same thread
            # for both ClientServers
            sharedJavaThreadId = entry0.getSharedJavaThreadId()
            self.assertEqual(sharedJavaThreadId,
                             entry1.getSharedJavaThreadId())
            # And that it is distinct from either corresponding to
            # this Python thread
            self.assertNotEqual(sharedJavaThreadId, entry0.getJavaThreadId())
            self.assertNotEqual(sharedJavaThreadId, entry1.getJavaThreadId())

            # ## 2 Hops via Shared Java Thread to Python Thread

            # Check that the shared thread ends up as different threads
            # in the Python side. This part may not be obvious as the
            # top-level idea seems to be for Python thread to be pinned
            # to Java thread. Consider that this case is a simplification
            # of the real case. In the real case there are two
            # ClientServers running in same JVM, but in Python side each
            # ClientServer is in its own process. In that case it makes
            # it obvious that the shared Java thread should indeed
            # end up in different Python threads.
            sharedPythonThreadId0 = entry0.getSharedPythonThreadId()
            sharedPythonThreadId1 = entry1.getSharedPythonThreadId()
            # three way assert to make sure all three python
            # threads are distinct
            self.assertNotEqual(thisThreadId, sharedPythonThreadId0)
            self.assertNotEqual(thisThreadId, sharedPythonThreadId1)
            self.assertNotEqual(sharedPythonThreadId0, sharedPythonThreadId1)
            # Check that the Python thread id does not change between
            # invocations
            self.assertEquals(sharedPythonThreadId0,
                              entry0.getSharedPythonThreadId())
            self.assertEquals(sharedPythonThreadId1,
                              entry1.getSharedPythonThreadId())

            # ## 3 Hops to Shared Java Thread

            # Check that the thread above after 2 hops calls back
            # into the Java shared thread
            self.assertEqual(sharedJavaThreadId,
                             entry0.getSharedViaPythonJavaThreadId())
            self.assertEqual(sharedJavaThreadId,
                             entry1.getSharedViaPythonJavaThreadId())

            client_server0.shutdown()
            client_server1.shutdown()

    def testMultiClientServer(self):
        with java_multi_client_server_app_process():
            client_server0 = ClientServer(
                JavaParameters(), PythonParameters())
            client_server1 = ClientServer(
                JavaParameters(port=DEFAULT_PORT + 2),
                PythonParameters(port=DEFAULT_PYTHON_PROXY_PORT + 2))

            entry0 = client_server0.entry_point
            entry1 = client_server1.entry_point

            # set up the ability for Java to get the Python thread ids
            threadIdGetter0 = PythonGetThreadId(client_server0)
            threadIdGetter1 = PythonGetThreadId(client_server1)
            entry0.setPythonThreadIdGetter(threadIdGetter0)
            entry1.setPythonThreadIdGetter(threadIdGetter1)
            thisThreadId = threading.current_thread().ident

            # Make sure we are talking to two different Entry points on
            # Java side
            self.assertEqual(0, entry0.getEntryId())
            self.assertEqual(1, entry1.getEntryId())

            # ## 0 Hops to Thread ID

            # Check that the two thread getters get the same thread
            self.assertEquals(thisThreadId,
                              int(threadIdGetter0.getThreadId()))
            self.assertEquals(thisThreadId,
                              int(threadIdGetter1.getThreadId()))

            # ## 1 Hop to Thread ID

            # Check that ClientServers on Java side are on different threads
            javaThreadId0 = entry0.getJavaThreadId()
            javaThreadId1 = entry1.getJavaThreadId()
            self.assertNotEqual(javaThreadId0, javaThreadId1)
            # Check that ClientServers on Java side stay on same thread
            # on subsequent calls to them
            self.assertEqual(javaThreadId0, entry0.getJavaThreadId())
            self.assertEqual(javaThreadId1, entry1.getJavaThreadId())
            # Check alternate way of getting thread ids and that they match
            self.assertEqual(javaThreadId0,
                             int(threadIdGetter0.getJavaThreadId()))
            self.assertEqual(javaThreadId1,
                             int(threadIdGetter1.getJavaThreadId()))

            # ## 2 Hops to Thread ID

            # Check that round trips from Python to Java and Python
            # end up back on this thread, regardless of which
            # client server we use for the round trip
            self.assertEqual(thisThreadId,
                             entry0.getPythonThreadId())
            self.assertEqual(thisThreadId,
                             entry1.getPythonThreadId())

            # ## 3 Hops to Thread ID

            # Check that round trips from Python to Java to Python to Java
            # end up on the same thread as 1 hop
            self.assertEqual(javaThreadId0,
                             entry0.getViaPythonJavaThreadId())
            self.assertEqual(javaThreadId1,
                             entry1.getViaPythonJavaThreadId())

            client_server0.shutdown()
            client_server1.shutdown()


class PythonGetThreadId(object):
    def __init__(self, gateway):
        self.gateway = gateway

    def getThreadId(self):
        # Return as a string because python3 doesn't have a long type anymore
        # and as a result when using python3 and the value is 32-bits this
        # arrives at Java as an Integer which fails to be converted to a Long
        return str(threading.current_thread().ident)

    def getJavaThreadId(self):
        # see comment above for why a string.
        return str(self.gateway.jvm.java.lang.Thread.currentThread().getId())

    class Java:
        implements = ["py4j.examples.MultiClientServerGetThreadId"]
