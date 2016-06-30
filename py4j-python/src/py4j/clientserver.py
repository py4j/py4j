# -*- coding: UTF-8 -*-
"""Module that implements a different threading model between
a Java Virtual Machine a Python interpreter.

In this model, Java and Python can exchange resquests and responses in the same
thread. For example, if a request is started in a Java UI thread and the Python
code calls some Java code, the Java code will be executed in the UI thread.
"""

from __future__ import unicode_literals, absolute_import

import gc
import logging
import socket
from threading import local, Thread
import weakref

from py4j.java_gateway import (
    quiet_close, quiet_shutdown,
    set_linger, GatewayClient, JavaGateway,
    CallbackServerParameters, GatewayParameters, CallbackServer,
    GatewayConnectionGuard, DEFAULT_ADDRESS, DEFAULT_PORT,
    DEFAULT_PYTHON_PROXY_PORT, DEFAULT_ACCEPT_TIMEOUT_PLACEHOLDER)
from py4j import protocol as proto
from py4j.protocol import (
    Py4JError, Py4JNetworkError, smart_decode, get_command_part,
    get_return_value)


logger = logging.getLogger("py4j.clientserver")


class JavaParameters(GatewayParameters):
    """Wrapper class that contains all parameters that can be passed to
    configure a `ClientServer`.`
    """
    def __init__(
            self, address=DEFAULT_ADDRESS, port=DEFAULT_PORT, auto_field=False,
            auto_close=True, auto_convert=False, eager_load=False,
            ssl_context=None, enable_memory_management=True, auto_gc=False,
            read_timeout=None):
        """

        :param address: the address to which the client will request a
            connection. If you're assing a `SSLContext` with
            `check_hostname=True` then this address must match
            (one of) the hostname(s) in the certificate the gateway
            server presents.

        :param port: the port to which the client will request a connection.
            Default is 25333.

        :param auto_field: if `False`, each object accessed through this
            gateway won"t try to lookup fields (they will be accessible only by
            calling get_field). If `True`, fields will be automatically looked
            up, possibly hiding methods of the same name and making method
            calls less efficient.

        :param auto_close: if `True`, the connections created by the client
            close the socket when they are garbage collected.

        :param auto_convert: if `True`, try to automatically convert Python
            objects like sequences and maps to Java Objects. Default value is
            `False` to improve performance and because it is still possible to
            explicitly perform this conversion.

        :param eager_load: if `True`, the gateway tries to connect to the JVM
            by calling System.currentTimeMillis. If the gateway cannot connect
            to the JVM, it shuts down itself and raises an exception.

        :param ssl_context: if not None, SSL connections will be made using
            this SSLContext

        :param enable_memory_management: if True, tells the Java side when a
            JavaObject (reference to an object on the Java side) is garbage
            collected on the Python side.

        :param auto_gc: if True, call gc.collect() before sending a command to
            the Java side. This should prevent the gc from running between
            sending the command and waiting for an anwser. False by default
            because this case is extremely unlikely.

        :param read_timeout: if > 0, sets a timeout in seconds after
            which the socket stops waiting for a response from the Java side.
        """
        super(JavaParameters, self).__init__(
            address, port, auto_field, auto_close, auto_convert, eager_load,
            ssl_context, enable_memory_management, read_timeout)
        self.auto_gc = auto_gc


class PythonParameters(CallbackServerParameters):
    """Wrapper class that contains all parameters that can be passed to
    configure a `ClientServer`
    """

    def __init__(
            self, address=DEFAULT_ADDRESS, port=DEFAULT_PYTHON_PROXY_PORT,
            daemonize=False, daemonize_connections=False, eager_load=True,
            ssl_context=None, auto_gc=False,
            accept_timeout=DEFAULT_ACCEPT_TIMEOUT_PLACEHOLDER,
            read_timeout=None,):
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

        :param auto_gc: if True, call gc.collect() before returning a response
            to the Java side. This should prevent the gc from running between
            sending the response and waiting for a new command. False by
            default because this case is extremely unlikely but could break
            communication.

        :param accept_timeout: if > 0, sets a timeout in seconds after which
            the callbackserver stops waiting for a connection, sees if the
            callback server should shut down, and if not, wait again for a
            connection. The default is 5 seconds: this roughly means that
            if can take up to 5 seconds to shut down the callback server.

        :param read_timeout: if > 0, sets a timeout in seconds after
            which the socket stops waiting for a call or command from the
            Java side.
        """
        super(PythonParameters, self).__init__(
            address, port, daemonize, daemonize_connections, eager_load,
            ssl_context, accept_timeout, read_timeout)
        self.auto_gc = auto_gc


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
            java_parameters,
            gateway_property=gateway_property)
        self.java_parameters = java_parameters
        self.python_parameters = python_parameters
        self.thread_connection = local()

    def set_thread_connection(self, connection):
        """Associates a ClientServerConnection with the current thread.

        :param connection: The ClientServerConnection to associate with the
            current thread.
        """
        self.thread_connection.connection = weakref.ref(connection)

    def get_thread_connection(self):
        """Returns the ClientServerConnection associated with this thread. Can
        be None.
        """
        connection = None
        try:
            connection_wr = self.thread_connection.connection
            if connection_wr:
                connection = connection_wr()
        except AttributeError:
            pass
        return connection

    def _get_connection(self):
        connection = self.get_thread_connection()

        try:
            if connection is not None:
                # Remove the strong reference to the connection
                # It will be re-added after the command is sent.
                self.deque.remove(connection)
        except ValueError:
            # Should never reach this point
            pass

        if connection is None or connection.socket is None:
            connection = self._create_new_connection()
        return connection

    def _create_new_connection(self):
        connection = ClientServerConnection(
            self.java_parameters, self.python_parameters,
            self.gateway_property, self)
        connection.connect_to_java_server()
        self.set_thread_connection(connection)
        return connection

    def _should_retry(self, retry, connection, pne=None):
        # Only retry if Python was driving the communication.
        parent_retry = super(JavaClient, self)._should_retry(
            retry, connection, pne)
        return parent_retry and retry and connection and\
            connection.initiated_from_client

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

    def _auto_gc(self, from_client=False):
        if from_client and self.java_parameters.auto_gc:
            gc.collect()
        elif not from_client and self.python_parameters.auto_gc:
            gc.collect()

    def connect_to_java_server(self):
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            if self.java_parameters.read_timeout:
                self.socket.settimeout(self.java_parameters.read_timeout)
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
        self.java_client.set_thread_connection(self)
        self.wait_for_commands()

    def send_command(self, command):
        # TODO At some point extract common code from wait_for_commands
        logger.debug("Command to send: {0}".format(command))
        try:
            self._auto_gc(True)
            self.socket.sendall(command.encode("utf-8"))
        except Exception as e:
            logger.info("Error while sending or receiving.", exc_info=True)
            raise Py4JNetworkError(
                "Error while sending", e, proto.ERROR_ON_SEND)

        try:
            while True:
                answer = smart_decode(self.stream.readline()[:-1])
                logger.debug("Answer received: {0}".format(answer))
                # Happens when a the other end is dead. There might be an empty
                # answer before the socket raises an error.
                if answer.strip() == "":
                    raise Py4JNetworkError("Answer from Java side is empty")
                if answer.startswith(proto.RETURN_MESSAGE):
                    return answer[1:]
                else:
                    command = answer
                    obj_id = smart_decode(self.stream.readline())[:-1]

                    if command == proto.CALL_PROXY_COMMAND_NAME:
                        return_message = self._call_proxy(obj_id, self.stream)
                        self._auto_gc(True)
                        self.socket.sendall(return_message.encode("utf-8"))
                    elif command == proto.GARBAGE_COLLECT_PROXY_COMMAND_NAME:
                        self.stream.readline()
                        del(self.pool[obj_id])
                        self._auto_gc(True)
                        self.socket.sendall(
                            proto.SUCCESS_RETURN_MESSAGE.encode("utf-8"))
                    else:
                        logger.error("Unknown command {0}".format(command))
                        # We're sending something to prevent blocking,
                        # but at this point, the protocol is broken.
                        self.socket.sendall(
                            proto.ERROR_RETURN_MESSAGE.encode("utf-8"))
        except Exception as e:
            logger.info("Error while receiving.", exc_info=True)
            raise Py4JNetworkError(
                "Error while sending or receiving", e, proto.ERROR_ON_RECEIVE)

    def close(self, reset=False):
        logger.info("Closing down clientserver connection")
        if reset:
            set_linger(self.socket)
        quiet_close(self.stream)
        if not reset:
            quiet_shutdown(self.socket)
        quiet_close(self.socket)
        self.socket = None
        self.stream = None

    def wait_for_commands(self):
        logger.info("Python Server ready to receive messages")
        reset = False
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
                    self._auto_gc()
                    self.socket.sendall(return_message.encode("utf-8"))
                elif command == proto.GARBAGE_COLLECT_PROXY_COMMAND_NAME:
                    self.stream.readline()
                    del(self.pool[obj_id])
                    self._auto_gc()
                    self.socket.sendall(
                        proto.SUCCESS_RETURN_MESSAGE.encode("utf-8"))
                else:
                    logger.error("Unknown command {0}".format(command))
                    # We're sending something to prevent blocking, but at this
                    # point, the protocol is broken.
                    self.socket.sendall(
                        proto.ERROR_RETURN_MESSAGE.encode("utf-8"))
        except socket.timeout:
            reset = True
            logger.info(
                "Timeout while python server was waiting for"
                "a message", exc_info=True)
        except Exception:
            # This is a normal exception...
            logger.info(
                "Error while python server was waiting for"
                "a message", exc_info=True)
        self.close(reset)

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
            self, java_parameters=None, python_parameters=None,
            python_server_entry_point=None):
        """
        :param java_parameters: collection of parameters and flags used to
            configure the JavaGateway (Java client)

        :param python_parameters: collection of parameters and flags used to
            configure the CallbackServer (Python server)

        :param python_server_entry_point: can be requested by the Java side if
            Java is driving the communication.
        """
        if not java_parameters:
            java_parameters = JavaParameters()
        if not python_parameters:
            python_parameters = PythonParameters()
        self.java_parameters = java_parameters
        self.python_parameters = python_parameters
        super(ClientServer, self).__init__(
            gateway_parameters=java_parameters,
            callback_server_parameters=python_parameters,
            python_server_entry_point=python_server_entry_point
        )

    def _create_gateway_client(self):
        java_client = JavaClient(self.java_parameters, self.python_parameters)
        return java_client

    def _create_callback_server(self, callback_server_parameters):
        callback_server = PythonServer(
            self._gateway_client, self.java_parameters, self.python_parameters,
            self.gateway_property)
        return callback_server
