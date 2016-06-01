from contextlib import contextmanager
import gc
from multiprocessing import Process
import subprocess
import unittest

from py4j.java_gateway import (
    JavaGateway, GatewayParameters, CallbackServerParameters, DEFAULT_PORT,
    DEFAULT_PYTHON_PROXY_PORT)
# TODO rename test_gateway_connection because it is executed as a test
from py4j.tests.java_gateway_test import (
    PY4J_JAVA_PATH, test_gateway_connection, sleep)
from py4j.tests.py4j_callback_recursive_example import (
    PythonPing, HelloState)


def start_instrumented_gateway_server():
    subprocess.call([
        "java", "-Xmx512m", "-cp", PY4J_JAVA_PATH,
        "py4j.instrumented.InstrumentedApplication"])


def start_gateway_server_example_app_process():
    # XXX DO NOT FORGET TO KILL THE PROCESS IF THE TEST DOES NOT SUCCEED
    p = Process(target=start_instrumented_gateway_server)
    p.start()
    sleep()
    test_gateway_connection()
    return p


@contextmanager
def gateway_server_example_app_process():
    p = start_gateway_server_example_app_process()
    try:
        yield p
    finally:
        p.join()


class HelloState2(HelloState):
    def __init__(self, run_gc=True):
        self.gateway = None
        self.run_gc = run_gc
        super(HelloState2, self).__init__()

    def _play_with_jvm(self):
        al = self.gateway.jvm.java.util.ArrayList()
        al.append("Hello World")
        obj = self.gateway.jvm.py4j.\
            instrumented.InstrumentedObject("test")
        al.append(obj)
        return str(al)

    def sayHello(self, int_value=None, string_value=None):
        self._play_with_jvm()
        if self.run_gc:
            gc.collect()
        return super(HelloState2, self).sayHello(
            int_value, string_value)

    class Java:
        implements = ["py4j.examples.IHello"]


class GatewayServerTest(unittest.TestCase):

    def testPythonToJava(self):
        def work_with_object(gateway):
            obj = gateway.jvm.py4j.\
                instrumented.InstrumentedObject("test")
            return str(obj)

        def internal_work():
            gateway2 = JavaGateway(gateway_parameters=GatewayParameters(
                port=DEFAULT_PORT+5))
            sleep()
            work_with_object(gateway2)
            gc.collect()
            sleep()
            gateway2.shutdown()

        with gateway_server_example_app_process():
            gateway = JavaGateway()
            gateway.entry_point.startServer2()
            internal_work()
            gateway.jvm.py4j.instrumented.MetricRegistry.forceFinalization()
            sleep()
            createdSet = gateway.jvm.py4j.instrumented.MetricRegistry.\
                getCreatedObjectsKeySet()
            finalizedSet = gateway.jvm.py4j.instrumented.MetricRegistry.\
                getFinalizedObjectsKeySet()

            # 4 objects: GatewayServer, GatewayConnection, CallbackClient,
            # InstrumentedObject
            self.assertEqual(4, len(createdSet))
            self.assertEqual(4, len(finalizedSet))
            self.assertEqual(createdSet, finalizedSet)
            gateway.shutdown()

    def testPythonToJavaToPython(self):
        def play_with_ping(gateway):
            ping = PythonPing()
            pingpong = gateway.jvm.py4j.examples.PingPong()
            total = pingpong.start(ping)
            return total

        def internal_work():
            gateway2 = JavaGateway(
                gateway_parameters=GatewayParameters(
                    port=DEFAULT_PORT+5),
                callback_server_parameters=CallbackServerParameters(
                    port=DEFAULT_PYTHON_PROXY_PORT+5))
            sleep()
            play_with_ping(gateway2)
            gc.collect()
            sleep()
            gateway2.shutdown()

        with gateway_server_example_app_process():
            gateway = JavaGateway()
            gateway.entry_point.startServer2()
            internal_work()
            gateway.jvm.py4j.instrumented.MetricRegistry.forceFinalization()
            sleep()
            createdSet = gateway.jvm.py4j.instrumented.MetricRegistry.\
                getCreatedObjectsKeySet()
            finalizedSet = gateway.jvm.py4j.instrumented.MetricRegistry.\
                getFinalizedObjectsKeySet()

            # 9 objects: GatewayServer, X GatewayConnection, CallbackClient,
            # X CallbackConnection, TODO
            self.assertEqual(9, len(createdSet))
            self.assertEqual(9, len(finalizedSet))
            self.assertEqual(createdSet, finalizedSet)
            gateway.shutdown()

    def testJavaToPythonToJavaCleanGC(self):
        def internal_work(gateway):
            hello_state = HelloState2()
            gateway2 = JavaGateway(
                gateway_parameters=GatewayParameters(
                    port=DEFAULT_PORT+5),
                callback_server_parameters=CallbackServerParameters(
                    port=DEFAULT_PYTHON_PROXY_PORT+5),
                python_server_entry_point=hello_state)
            hello_state.gateway = gateway2
            sleep()

            gateway.entry_point.startServerWithPythonEntry(True)
            sleep()
            gateway2.shutdown()

            # Check that Java correctly called Python
            self.assertEqual(2, len(hello_state.calls))
            self.assertEqual((None, None), hello_state.calls[0])
            self.assertEqual((2, "Hello World"), hello_state.calls[1])

        with gateway_server_example_app_process():
            gateway = JavaGateway()
            internal_work(gateway)
            gateway.jvm.py4j.instrumented.MetricRegistry.forceFinalization()
            sleep()
            createdSet = gateway.jvm.py4j.instrumented.MetricRegistry.\
                getCreatedObjectsKeySet()
            finalizedSet = gateway.jvm.py4j.instrumented.MetricRegistry.\
                getFinalizedObjectsKeySet()
            # 6 objects: 2 InstrumentedObject (sayHello called twice), 1
            # InstrGatewayServer, 1 CallbackClient, 1 CallbackConnection, 1
            # GatewayConnection
            self.assertEqual(6, len(createdSet))
            self.assertEqual(6, len(finalizedSet))
            self.assertEqual(createdSet, finalizedSet)
            gateway.shutdown()

    def testJavaToPythonToJavaNoGC(self):
        def internal_work(gateway):
            hello_state = HelloState2(run_gc=False)
            gateway2 = JavaGateway(
                gateway_parameters=GatewayParameters(
                    port=DEFAULT_PORT+5),
                callback_server_parameters=CallbackServerParameters(
                    port=DEFAULT_PYTHON_PROXY_PORT+5),
                python_server_entry_point=hello_state)
            hello_state.gateway = gateway2
            sleep()

            gateway.entry_point.startServerWithPythonEntry(True)
            sleep()
            gateway2.shutdown()

            # Check that Java correctly called Python
            self.assertEqual(2, len(hello_state.calls))
            self.assertEqual((None, None), hello_state.calls[0])
            self.assertEqual((2, "Hello World"), hello_state.calls[1])

        with gateway_server_example_app_process():
            gateway = JavaGateway()
            # We disable gc to test whether a shut down on one side will
            # garbage collect everything.
            gc.disable()
            internal_work(gateway)
            gc.enable()
            gateway.jvm.py4j.instrumented.MetricRegistry.forceFinalization()
            sleep()
            createdSet = gateway.jvm.py4j.instrumented.MetricRegistry.\
                getCreatedObjectsKeySet()
            finalizedSet = gateway.jvm.py4j.instrumented.MetricRegistry.\
                getFinalizedObjectsKeySet()
            # 6 objects: 2 InstrumentedObject (sayHello called twice), 1
            # InstrGatewayServer, 1 CallbackClient, 1 CallbackConnection, 1
            # GatewayConnection
            self.assertEqual(6, len(createdSet))
            self.assertEqual(6, len(finalizedSet))
            self.assertEqual(createdSet, finalizedSet)
            gateway.shutdown()

    def testJavaToPythonToJavaCleanGCNoShutdown(self):
        def internal_work(gateway):
            hello_state = HelloState2()
            gateway2 = JavaGateway(
                gateway_parameters=GatewayParameters(
                    port=DEFAULT_PORT+5),
                callback_server_parameters=CallbackServerParameters(
                    port=DEFAULT_PYTHON_PROXY_PORT+5),
                python_server_entry_point=hello_state)
            hello_state.gateway = gateway2
            sleep()

            gateway.entry_point.startServerWithPythonEntry(False)
            sleep()
            gateway2.shutdown()

            # Check that Java correctly called Python
            self.assertEqual(2, len(hello_state.calls))
            self.assertEqual((None, None), hello_state.calls[0])
            self.assertEqual((2, "Hello World"), hello_state.calls[1])

        with gateway_server_example_app_process():
            gateway = JavaGateway()
            internal_work(gateway)
            gateway.jvm.py4j.instrumented.MetricRegistry.forceFinalization()
            sleep()
            createdSet = gateway.jvm.py4j.instrumented.MetricRegistry.\
                getCreatedObjectsKeySet()
            finalizedSet = gateway.jvm.py4j.instrumented.MetricRegistry.\
                getFinalizedObjectsKeySet()
            # 6 objects: 2 InstrumentedObject (sayHello called twice), 1
            # InstrGatewayServer, 1 CallbackClient, 1 CallbackConnection, 1
            # GatewayConnection
            self.assertEqual(6, len(createdSet))
            self.assertEqual(6, len(finalizedSet))
            self.assertEqual(createdSet, finalizedSet)
            gateway.shutdown()

    def testJavaToPythonToJavaNoGCNoShutdown(self):
        def internal_work(gateway):
            hello_state = HelloState2(run_gc=False)
            gateway2 = JavaGateway(
                gateway_parameters=GatewayParameters(
                    port=DEFAULT_PORT+5),
                callback_server_parameters=CallbackServerParameters(
                    port=DEFAULT_PYTHON_PROXY_PORT+5),
                python_server_entry_point=hello_state)
            hello_state.gateway = gateway2
            sleep()

            gateway.entry_point.startServerWithPythonEntry(False)
            sleep()
            gateway2.shutdown()

            # Check that Java correctly called Python
            self.assertEqual(2, len(hello_state.calls))
            self.assertEqual((None, None), hello_state.calls[0])
            self.assertEqual((2, "Hello World"), hello_state.calls[1])

        with gateway_server_example_app_process():
            gateway = JavaGateway()
            # We disable gc to test whether a shut down on one side will
            # garbage collect everything.
            gc.disable()
            internal_work(gateway)
            gc.enable()
            gateway.jvm.py4j.instrumented.MetricRegistry.forceFinalization()
            sleep()
            createdSet = gateway.jvm.py4j.instrumented.MetricRegistry.\
                getCreatedObjectsKeySet()
            finalizedSet = gateway.jvm.py4j.instrumented.MetricRegistry.\
                getFinalizedObjectsKeySet()
            # 6 objects: 2 InstrumentedObject (sayHello called twice), 1
            # InstrGatewayServer, 1 CallbackClient, 1 CallbackConnection, 1
            # GatewayConnection
            self.assertEqual(6, len(createdSet))
            self.assertEqual(6, len(finalizedSet))
            self.assertEqual(createdSet, finalizedSet)
            gateway.shutdown()
