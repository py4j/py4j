from contextlib import contextmanager
import gc
from multiprocessing import Process
import subprocess
import unittest

from py4j.java_gateway import (
    JavaGateway, GatewayParameters, CallbackServerParameters,
    DEFAULT_PORT, DEFAULT_PYTHON_PROXY_PORT)
# TODO rename test_gateway_connection because it is executed as a test
from py4j.tests.java_gateway_test import (
    PY4J_JAVA_PATH, test_gateway_connection, sleep)
from py4j.tests.py4j_callback_recursive_example import HelloState
from py4j.tests.instrumented import (
    InstrJavaGateway, InstrumentedPythonPing, register_creation,
    CREATED, FINALIZED, MEMORY_HOOKS)


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
        register_creation(self)

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


def assert_python_memory(test, size):
    test.assertEqual(size, len(CREATED))
    test.assertEqual(size, len(FINALIZED))
    test.assertEqual(set(CREATED), set(FINALIZED))


class GatewayServerTest(unittest.TestCase):

    def tearDown(self):
        MEMORY_HOOKS.clear()
        CREATED.clear()
        FINALIZED.clear()

    def testPythonToJava(self):
        def work_with_object(gateway):
            obj = gateway.jvm.py4j.\
                instrumented.InstrumentedObject("test")
            return str(obj)

        def internal_work():
            gateway2 = InstrJavaGateway(gateway_parameters=GatewayParameters(
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
            gc.collect()
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

            # 4 objects: JavaGateway, GatewayClient, GatewayProperty,
            # GatewayConnection
            assert_python_memory(self, 4)

    def testPythonToJavaToPython(self):
        def play_with_ping(gateway):
            ping = InstrumentedPythonPing()
            pingpong = gateway.jvm.py4j.examples.PingPong()
            total = pingpong.start(ping)
            return total

        def internal_work():
            gateway2 = InstrJavaGateway(
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
            gc.collect()
            gateway.jvm.py4j.instrumented.MetricRegistry.forceFinalization()
            sleep()
            createdSet = gateway.jvm.py4j.instrumented.MetricRegistry.\
                getCreatedObjectsKeySet()
            finalizedSet = gateway.jvm.py4j.instrumented.MetricRegistry.\
                getFinalizedObjectsKeySet()

            # 9 objects: GatewayServer, 4 GatewayConnection, CallbackClient,
            # 3 CallbackConnection
            self.assertEqual(9, len(createdSet))
            self.assertEqual(9, len(finalizedSet))
            self.assertEqual(createdSet, finalizedSet)
            gateway.shutdown()

            # 11 objects: JavaGateway, CallbackSerer, GatewayClient,
            # GatewayProperty, PythonPing, 4 GatewayConnection,
            # 3 CallbackConnection. Notice the symmetry
            assert_python_memory(self, 12)

    def testJavaToPythonToJavaCleanGC(self):
        def internal_work(gateway):
            hello_state = HelloState2()
            gateway2 = InstrJavaGateway(
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
            gc.collect()
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

            # 7 objects: JavaGateway, GatewayClient, CallbackServer,
            # GatewayProperty, HelloState, GatewayConnection,
            # CallbackConnection
            assert_python_memory(self, 7)

    def testJavaToPythonToJavaNoGC(self):
        def internal_work(gateway):
            hello_state = HelloState2(run_gc=False)
            gateway2 = InstrJavaGateway(
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
            gc.collect()
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

            # 7 objects: JavaGateway, GatewayClient, CallbackServer,
            # GatewayProperty, HelloState, GatewayConnection,
            # CallbackConnection
            assert_python_memory(self, 7)

    def testJavaToPythonToJavaCleanGCNoShutdown(self):
        def internal_work(gateway):
            hello_state = HelloState2()
            gateway2 = InstrJavaGateway(
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
            gc.collect()
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

            # 7 objects: JavaGateway, GatewayClient, CallbackServer,
            # GatewayProperty, HelloState, GatewayConnection,
            # CallbackConnection
            assert_python_memory(self, 7)

    def testJavaToPythonToJavaNoGCNoShutdown(self):
        def internal_work(gateway):
            hello_state = HelloState2(run_gc=False)
            gateway2 = InstrJavaGateway(
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
            gc.collect()
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

            # 7 objects: JavaGateway, GatewayClient, CallbackServer,
            # GatewayProperty, HelloState, GatewayConnection,
            # CallbackConnection
            assert_python_memory(self, 7)
