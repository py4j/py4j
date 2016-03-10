from contextlib import contextmanager
import gc
from multiprocessing import Process
import subprocess
import unittest

from py4j.java_gateway import GatewayConnectionGuard, is_instance_of
from py4j.clientserver import (
    ClientServer, JavaParameters, PythonParameters)
from py4j.protocol import Py4JJavaError, smart_decode

from py4j.tests.java_callback_test import IHelloImpl
from py4j.tests.java_gateway_test import (
    PY4J_JAVA_PATH, test_gateway_connection, sleep)
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
    test_gateway_connection()
    return p


@contextmanager
def clientserver_example_app_process(start_java_client=False):
    p = start_clientserver_example_app_process(start_java_client)
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
            pass

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

    def testRecursion(self):
        with clientserver_example_app_process():
            client_server = ClientServer(
                JavaParameters(), PythonParameters())
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
