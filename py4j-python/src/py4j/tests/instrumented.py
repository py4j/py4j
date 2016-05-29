from collections import deque
import weakref

import py4j.protocol as proto
from py4j.clientserver import (
    ClientServerConnection, ClientServer, JavaClient, PythonServer)
from py4j.java_gateway import (
    CallbackServer, JavaGateway, GatewayClient, GatewayProperty,
    PythonProxyPool, GatewayConnection, CallbackConnection, DEFAULT_PORT,
    DEFAULT_PYTHON_PROXY_PORT, DEFAULT_ADDRESS)
from py4j.tests.py4j_callback_recursive_example import PythonPing

# Use deque to be thread-safe
MEMORY_HOOKS = deque()
CREATED = deque()
FINALIZED = deque()


def register_creation(obj):
    obj_str = str(obj)
    CREATED.append(obj_str)
    MEMORY_HOOKS.append(weakref.ref(
        obj,
        lambda wr: FINALIZED.append(obj_str)
    ))


class InstrumentedPythonPing(PythonPing):

    def __init__(self, fail=False):
        super(InstrumentedPythonPing, self).__init__(fail)
        register_creation(self)


class InstrJavaGateway(JavaGateway):
    def __init__(
            self, gateway_client=None, auto_field=False,
            python_proxy_port=DEFAULT_PYTHON_PROXY_PORT,
            start_callback_server=False, auto_convert=False, eager_load=False,
            gateway_parameters=None, callback_server_parameters=None,
            python_server_entry_point=None):
        super(InstrJavaGateway, self). __init__(
            gateway_client, auto_field,
            python_proxy_port,
            start_callback_server, auto_convert, eager_load,
            gateway_parameters, callback_server_parameters,
            python_server_entry_point)
        register_creation(self)

    def _create_gateway_client(self):
        gateway_client = InstrGatewayClient(
            address=self.gateway_parameters.address,
            port=self.gateway_parameters.port,
            auto_close=self.gateway_parameters.auto_close,
            ssl_context=self.gateway_parameters.ssl_context)
        return gateway_client

    def _create_callback_server(self, callback_server_parameters):
        callback_server = InstrCallbackServer(
            self.gateway_property.pool, self._gateway_client,
            callback_server_parameters=callback_server_parameters)
        return callback_server

    def _create_gateway_property(self):
        gateway_property = InstrGatewayProperty(
            self.gateway_parameters.auto_field, PythonProxyPool(),
            self.gateway_parameters.enable_memory_management)
        if self.python_server_entry_point:
            gateway_property.pool.put(
                self.python_server_entry_point, proto.ENTRY_POINT_OBJECT_ID)
        return gateway_property


class InstrGatewayClient(GatewayClient):

    def __init__(self, address=DEFAULT_ADDRESS, port=DEFAULT_PORT,
                 auto_close=True, gateway_property=None, ssl_context=None):
        super(InstrGatewayClient, self).__init__(
            address, port, auto_close, gateway_property, ssl_context)
        register_creation(self)

    def _create_connection(self):
        connection = InstrGatewayConnection(
            self.address, self.port, self.auto_close, self.gateway_property,
            self.ssl_context)
        connection.start()
        return connection


class InstrGatewayProperty(GatewayProperty):
    """Object shared by callbackserver, gateway, and connections.
    """
    def __init__(self, auto_field, pool, enable_memory_management=True):
        super(InstrGatewayProperty, self).__init__(
            auto_field, pool, enable_memory_management)
        register_creation(self)


class InstrGatewayConnection(GatewayConnection):

    def __init__(self, address=DEFAULT_ADDRESS, port=DEFAULT_PORT,
                 auto_close=True, gateway_property=None, ssl_context=None):
        super(InstrGatewayConnection, self).__init__(
            address, port, auto_close, gateway_property, ssl_context)
        register_creation(self)


class InstrCallbackServer(CallbackServer):
    def __init__(
            self, pool, gateway_client, port=DEFAULT_PYTHON_PROXY_PORT,
            address=DEFAULT_ADDRESS, callback_server_parameters=None):
        super(InstrCallbackServer, self).__init__(
            pool, gateway_client, port,
            address, callback_server_parameters)
        register_creation(self)

    def _create_connection(self, socket_instance, stream):
        connection = InstrCallbackConnection(
            self.pool, stream, socket_instance, self.gateway_client,
            self.callback_server_parameters)
        return connection


class InstrCallbackConnection(CallbackConnection):

    def __init__(
            self, pool, input, socket_instance, gateway_client,
            callback_server_parameters):
        super(InstrCallbackConnection, self).__init__(
            pool, input, socket_instance, gateway_client,
            callback_server_parameters)
        register_creation(self)


class InstrClientServerConnection(ClientServerConnection):
    def __init__(
            self, java_parameters, python_parameters, gateway_property,
            java_client):
        super(InstrClientServerConnection, self).__init__(
            java_parameters, python_parameters, gateway_property,
            java_client)
        register_creation(self)


class InstrPythonServer(PythonServer):
    def __init__(
            self, java_client, java_parameters, python_parameters,
            gateway_property):
        super(InstrPythonServer, self).__init__(
            java_client, java_parameters, python_parameters, gateway_property)
        register_creation(self)

    def _create_connection(self, socket, stream):
        connection = InstrClientServerConnection(
            self.java_parameters, self.python_parameters,
            self.gateway_property, self.gateway_client)
        connection.init_socket_from_python_server(socket, stream)
        return connection


class InstrJavaClient(JavaClient):

    def __init__(
            self, java_parameters, python_parameters, gateway_property=None):
        super(InstrJavaClient, self).__init__(
            java_parameters, python_parameters, gateway_property)
        register_creation(self)

    def _create_new_connection(self):
        connection = InstrClientServerConnection(
            self.java_parameters, self.python_parameters,
            self.gateway_property, self)
        connection.connect_to_java_server()
        self.set_thread_connection(connection)
        self.deque.append(connection)
        return connection


class InstrClientServer(ClientServer):

    def __init__(
            self, java_parameters=None, python_parameters=None,
            python_server_entry_point=None):
        super(InstrClientServer, self).__init__(
            java_parameters, python_parameters,
            python_server_entry_point)
        register_creation(self)

    def _create_gateway_client(self):
        java_client = InstrJavaClient(
            self.java_parameters, self.python_parameters)
        return java_client

    def _create_callback_server(self, callback_server_parameters):
        callback_server = InstrPythonServer(
            self._gateway_client, self.java_parameters, self.python_parameters,
            self.gateway_property)
        return callback_server

    def _create_gateway_property(self):
        gateway_property = InstrGatewayProperty(
            self.java_parameters.auto_field, PythonProxyPool(),
            self.java_parameters.enable_memory_management)
        if self.python_server_entry_point:
            gateway_property.pool.put(
                self.python_server_entry_point, proto.ENTRY_POINT_OBJECT_ID)
        return gateway_property
