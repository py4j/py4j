# -*- coding: UTF-8 -*-
"""Module that implements a different threading model between
a Java Virtual Machine a Python interpreter.

In this model, Java and Python can exchange resquests and responses in the same
thread. For example, if a request is started in a Java UI thread and the Python
code calls some Java code, the Java code will be executed in the UI thread.
"""

from __future__ import unicode_literals, absolute_import

import logging
import socket
from threading import local, Thread

from py4j.java_gateway import (
    quiet_close, quiet_shutdown, GatewayClient, JavaGateway,
    CallbackServerParameters, GatewayParameters, CallbackServer,
    GatewayConnectionGuard, DEFAULT_ADDRESS, DEFAULT_PORT,
    DEFAULT_PYTHON_PROXY_PORT)
from py4j import protocol as proto
from py4j.protocol import (
    Py4JError, Py4JNetworkError, smart_decode, get_command_part,
    get_return_value)


logger = logging.getLogger("py4j.clientserver")

thread_connection = local()


class JavaParameters(GatewayParameters):
    """Wrapper class that contains all parameters that can be passed to
    configure a `ClientServer`.`
    """
    def __init__(
            self, address=DEFAULT_ADDRESS, port=DEFAULT_PORT, auto_field=False,
            auto_close=True, auto_convert=False, eager_load=False,
            ssl_context=None):
        """
        :param address: the address to which the client will request a
         connection. If you're assing a `SSLContext` with `check_hostname=True`
         then this address must match (one of) the hostname(s) in the
         certificate the gateway server presents.

        :param port: the port to which the client will request a connection.
         Default is 25333.

        :param auto_field: if `False`, each object accessed through this
         gateway won"t try to lookup fields (they will be accessible only by
         calling get_field). If `True`, fields will be automatically looked
         up, possibly hiding methods of the same name and making method calls
         less efficient.

        :param auto_close: if `True`, the connections created by the client
         close the socket when they are garbage collected.

        :param auto_convert: if `True`, try to automatically convert Python
         objects like sequences and maps to Java Objects. Default value is
         `False` to improve performance and because it is still possible to
         explicitly perform this conversion.

        :param eager_load: if `True`, the gateway tries to connect to the JVM
         by calling System.currentTimeMillis. If the gateway cannot connect to
         the JVM, it shuts down itself and raises an exception.

        :param ssl_context: if not None, SSL connections will be made using
         this SSLContext
        """
        super(JavaParameters, self).__init__(
            address, port, auto_field, auto_close, auto_convert, eager_load,
            ssl_context)


class PythonParameters(CallbackServerParameters):
    """Wrapper class that contains all parameters that can be passed to
    configure a `ClientServer`
    """

    def __init__(
            self, address=DEFAULT_ADDRESS, port=DEFAULT_PYTHON_PROXY_PORT,
            daemonize=False, daemonize_connections=False, eager_load=True,
            ssl_context=None):
        """
        :param address: the address to which the client will request a
            connection

        :param port: the port to which the client will request a connection.
            Default is 25333.

        :param daemonize: If `True`, will set the daemon property of the server
            thread to True. The callback server will exit automatically if all
            the other threads exit.

        :param daemonize_connections: If `True`, callback server connections
            are executed in daemonized threads and will not block the exit of a
            program if non daemonized threads are finished.

        :param eager_load: If `True`, the callback server is automatically
            started when the JavaGateway is created.

        :param ssl_context: if not None, the SSLContext's certificate will be
         presented to callback connections.
        """
        super(PythonParameters, self).__init__(
            address, port, daemonize, daemonize_connections, eager_load,
            ssl_context)


class JavaClient(GatewayClient):
    """Responsible for managing requests from Python to Java.

    This implementation is thread-safe because it always use only one
    ClientServerConnection per thread.
    """

    def __init__(
            self, java_parameters, python_parameters, gateway_property=None):
        """
        :param java_parameters: collection of parameters and flags used to
            configure the JavaGateway (Java client)

        :param python_parameters: collection of parameters and flags used to
            configure the CallbackServer (Python server)

        :param gateway_property: used to keep gateway preferences without a
            cycle with the JavaGateway
        """
        super(JavaClient, self).__init__(
            address=java_parameters.address,
            port=java_parameters.port,
            auto_close=java_parameters.auto_close,
            gateway_property=gateway_property,
            ssl_context=java_parameters.ssl_context)
        self.java_parameters = java_parameters
        self.python_parameters = python_parameters

    def _get_connection(self):
        try:
            connection = thread_connection.connection
            if connection.socket is None:
                connection = self._create_new_connection()
        except AttributeError:
            connection = self._create_new_connection()
        return connection

    def _create_new_connection(self):
        connection = ClientServerConnection(
            self.java_parameters, self.python_parameters,
            self.gateway_property, self)
        connection.connect_to_java_server()
        thread_connection.connection = connection
        self.deque.append(connection)
        return connection

    def _give_back_connection(self, connection):
        # Nothing to do for now
        pass

    def _should_retry(self, retry, connection):
        # Only retry if Python was driving the communication.
        return retry and connection and connection.initiated_from_client

    def _create_connection_guard(self, connection):
        return ClientServerConnectionGuard(self, connection)


class ClientServerConnectionGuard(GatewayConnectionGuard):
    """Connection guard that does nothing on exit because there is no need to
    close or give back a connection.
    """

    def __exit__(self, type, value, traceback):
        pass


class PythonServer(CallbackServer):
    """Responsible for managing requests from Java to Python.
    """

    def __init__(
            self, java_client, java_parameters, python_parameters,
            gateway_property):
        """
        :param java_client: the gateway client used to call Java objects.

        :param java_parameters: collection of parameters and flags used to
            configure the JavaGateway (Java client)

        :param python_parameters: collection of parameters and flags used to
            configure the CallbackServer (Python server)

        :param gateway_property: used to keep gateway preferences.
        """
        super(PythonServer, self).__init__(
            pool=gateway_property.pool,
            gateway_client=java_client,
            callback_server_parameters=python_parameters)
        self.java_parameters = java_parameters
        self.python_parameters = python_parameters
        self.gateway_property = gateway_property

    def _create_connection(self, socket, stream):
        connection = ClientServerConnection(
            self.java_parameters, self.python_parameters,
            self.gateway_property, self.gateway_client)
        connection.init_socket_from_python_server(socket, stream)
        return connection


class ClientServerConnection(object):
    """Default connection for a ClientServer instance
    (socket-based, one per thread) responsible for communicating
    with the Java Virtual Machine.
    """

    def __init__(
            self, java_parameters, python_parameters, gateway_property,
            java_client):
        """
        :param java_parameters: collection of parameters and flags used to
            configure the JavaGateway (Java client)

        :param python_parameters: collection of parameters and flags used to
            configure the CallbackServer (Python server)

        :param gateway_property: used to keep gateway preferences.

        :param java_client: the gateway client used to call Java objects.
        """
        self.java_parameters = java_parameters
        self.python_parameters = python_parameters

        # For backward compatibility
        self.address = self.java_parameters.address
        self.port = self.java_parameters.port

        self.java_address = self.java_parameters.address
        self.java_port = self.java_parameters.port

        self.python_address = self.python_parameters.address
        self.python_port = self.python_parameters.port

        self.ssl_context = self.java_parameters.ssl_context
        self.socket = None
        self.stream = None
        self.gateway_property = gateway_property
        self.pool = gateway_property.pool
        self._listening_address = self._listening_port = None
        self.is_connected = False

        self.java_client = java_client
        self.initiated_from_client = False

    def connect_to_java_server(self):
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            if self.ssl_context:
                self.socket = self.ssl_context.wrap_socket(
                    self.socket, server_hostname=self.java_address)
            self.socket.connect((self.java_address, self.java_port))
            self.stream = self.socket.makefile("rb")
            self.is_connected = True
            self.initiated_from_client = True
        except Exception:
            quiet_close(self.socket)
            quiet_close(self.stream)
            self.socket = None
            self.stream = None
            self.is_connected = False
            raise

    def init_socket_from_python_server(self, socket, stream):
        self.socket = socket
        self.stream = stream
        self.is_connected = True

    def shutdown_gateway(self):
        """Sends a shutdown command to the Java side.

        This will close the ClientServer on the Java side: all active
        connections will be closed. This may be useful if the lifecycle
        of the Java program must be tied to the Python program.
        """
        if not self.is_connected:
            raise Py4JError("Gateway must be connected to send shutdown cmd.")

        try:
            quiet_close(self.stream)
            self.socket.sendall(
                proto.SHUTDOWN_GATEWAY_COMMAND_NAME.encode("utf-8"))
            self.close()
        except Exception:
            # Do nothing! Exceptions might occur anyway.
            logger.debug("Exception occurred while shutting down gateway",
                         exc_info=True)

    def start(self):
        t = Thread(target=self.run)
        t.daemon = self.python_parameters.daemonize_connections
        t.start()

    def run(self):
        thread_connection.connection = self
        self.wait_for_commands()

    def send_command(self, command):
        # TODO At some point extract common code from wait_for_commands
        logger.debug("Command to send: {0}".format(command))
        try:
            self.socket.sendall(command.encode("utf-8"))
            while True:
                answer = smart_decode(self.stream.readline()[:-1])
                logger.debug("Answer received: {0}".format(answer))
                # Happens when a the other end is dead. There might be an empty
                # answer before the socket raises an error.
                if answer.strip() == "":
                    self.close()
                    raise Py4JError("Answer from Java side is empty")
                if answer.startswith(proto.RETURN_MESSAGE):
                    return answer[1:]
                else:
                    command = answer
                    obj_id = smart_decode(self.stream.readline())[:-1]

                    if command == proto.CALL_PROXY_COMMAND_NAME:
                        return_message = self._call_proxy(obj_id, self.stream)
                        self.socket.sendall(return_message.encode("utf-8"))
                    elif command == proto.GARBAGE_COLLECT_PROXY_COMMAND_NAME:
                        self.stream.readline()
                        del(self.pool[obj_id])
                        self.socket.sendall(
                            proto.SUCCESS_RETURN_MESSAGE.encode("utf-8"))
                    else:
                        logger.error("Unknown command {0}".format(command))
                        # We're sending something to prevent blocking,
                        # but at this point, the protocol is broken.
                        self.socket.sendall(
                            proto.ERROR_RETURN_MESSAGE.encode("utf-8"))
        except Exception as e:
            logger.exception("Error while sending or receiving.")
            raise Py4JNetworkError("Error while sending or receiving", e)

    def close(self):
        logger.info("Closing down client")
        quiet_close(self.stream)
        quiet_shutdown(self.socket)
        quiet_close(self.socket)
        self.socket = None
        self.stream = None

    def wait_for_commands(self):
        logger.info("Python Server ready to receive messages")
        try:
            while True:
                command = smart_decode(self.stream.readline())[:-1]
                obj_id = smart_decode(self.stream.readline())[:-1]
                logger.info(
                    "Received command {0} on object id {1}".
                    format(command, obj_id))
                if obj_id is None or len(obj_id.strip()) == 0:
                    break
                if command == proto.CALL_PROXY_COMMAND_NAME:
                    return_message = self._call_proxy(obj_id, self.stream)
                    self.socket.sendall(return_message.encode("utf-8"))
                elif command == proto.GARBAGE_COLLECT_PROXY_COMMAND_NAME:
                    self.stream.readline()
                    del(self.pool[obj_id])
                    self.socket.sendall(
                        proto.SUCCESS_RETURN_MESSAGE.encode("utf-8"))
                else:
                    logger.error("Unknown command {0}".format(command))
                    # We're sending something to prevent blocking, but at this
                    # point, the protocol is broken.
                    self.socket.sendall(
                        proto.ERROR_RETURN_MESSAGE.encode("utf-8"))
        except Exception:
            # This is a normal exception...
            logger.info(
                "Error while python server was waiting for"
                "a message", exc_info=True)

        self.close()

    def _call_proxy(self, obj_id, input):
        return_message = proto.ERROR_RETURN_MESSAGE
        if obj_id in self.pool:
            try:
                method = smart_decode(input.readline())[:-1]
                params = self._get_params(input)
                return_value = getattr(self.pool[obj_id], method)(*params)
                return_message = proto.RETURN_MESSAGE + proto.SUCCESS +\
                    get_command_part(return_value, self.pool)
            except Exception:
                logger.exception("There was an exception while executing the "
                                 "Python Proxy on the Python Side.")
        return return_message

    def _get_params(self, input):
        params = []
        temp = smart_decode(input.readline())[:-1]
        while temp != proto.END:
            param = get_return_value("y" + temp, self.java_client)
            params.append(param)
            temp = smart_decode(input.readline())[:-1]
        return params


class ClientServer(JavaGateway):
    """Subclass of JavaGateway that implements a different threading model: a
    thread always use the same connection to the other side so callbacks are
    executed in the calling thread.

    For example, if Python thread 1 calls Java, and Java calls Python, the
    callback (from Java to Python) will be executed in Python thread 1.
    """

    def __init__(
            self, java_parameters, python_parameters,
            python_server_entry_point=None):
        """
        :param java_parameters: collection of parameters and flags used to
            configure the JavaGateway (Java client)

        :param python_parameters: collection of parameters and flags used to
            configure the CallbackServer (Python server)

        :param python_server_entry_point: can be requested by the Java side if
            Java is driving the communication.
        """
        self.java_parameters = java_parameters
        self.python_parameters = python_parameters
        self.python_server_entry_point = python_server_entry_point
        super(ClientServer, self).__init__(
            gateway_parameters=java_parameters,
            callback_server_parameters=python_parameters
        )

    def _create_gateway_client(self):
        java_client = JavaClient(self.java_parameters, self.python_parameters)
        return java_client

    def _create_gateway_property(self):
        gateway_property = super(ClientServer, self)._create_gateway_property()
        if self.python_server_entry_point:
            gateway_property.pool.put(
                self.python_server_entry_point, proto.ENTRY_POINT_OBJECT_ID)
        return gateway_property

    def _create_callback_server(self, callback_server_parameters):
        callback_server = PythonServer(
            self._gateway_client, self.java_parameters, self.python_parameters,
            self.gateway_property)
        return callback_server
