# -*- coding: UTF-8 -*-

from __future__ import unicode_literals, absolute_import

import logging
import select
import socket

from py4j.java_gateway import (
    DEFAULT_ADDRESS, DEFAULT_PORT, DEFAULT_PYTHON_PROXY_PORT,
    DEFAULT_CALLBACK_SERVER_ACCEPT_TIMEOUT, JavaObject,
    JVMView, GatewayProperty, PythonProxyPool, quiet_close, quiet_shutdown)
from py4j import protocol as proto
from py4j.protocol import (
    Py4JError, Py4JNetworkError, smart_decode, get_command_part,
    get_return_value)


logger = logging.getLogger("py4j.clientserver")


class JavaParameters(object):
    """Wrapper class that contains all parameters that can be passed to
    configure the communication with a Java server.
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

        :param port: the port to which the Python client will request a
            connection on the Java server. Default is 25333.

        :param auto_field: if `False`, each object accessed through this
         gateway won't try to lookup fields (they will be accessible only by
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
        this this SSLContext
        """
        self.address = address
        self.port = port
        self.auto_field = auto_field
        self.auto_close = auto_close
        self.auto_convert = auto_convert
        self.eager_load = eager_load
        self.ssl_context = ssl_context


class PythonParameters(object):
    """Wrapper class that contains all parameters that can be passed to
    configure a Python server.
    """

    def __init__(
            self, address=DEFAULT_ADDRESS, port=DEFAULT_PYTHON_PROXY_PORT,
            daemonize_connections=False, eager_load=True, ssl_context=None):
        """
        :param address: the address to which the client will request a
            connection

        :param port: the port to which the Python server will listen to.
            Default is 25334.

        :param daemonize_connections: If `True`, callback server connections
            are executed in daemonized threads and will not block the exit of a
            program if non daemonized threads are finished.

        :param eager_load: If `True`, the Python server is automatically
            started when the ClientServer is created.

        :param ssl_context: if not None, the SSLContext's certificate will be
         presented to callback connections.
        """
        self.address = address
        self.port = port
        # TODO when we will be able to accept more than one connection.
        self.daemonize_connections = daemonize_connections
        self.eager_load = eager_load
        self.ssl_context = ssl_context


class ClientServerConnection(object):
    def __init__(self, java_parameters, python_parameters):
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
        self.server_socket = None
        self.socket = None
        self.stream = None
        self.pool = PythonProxyPool()
        self.gateway_property = GatewayProperty(
            self.java_parameters.auto_field, self.pool)
        self._listening_address = self._listening_port = None
        self.is_shutdown = False

    def connect_to_java_server(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        if self.ssl_context:
            self.socket = self.ssl_context.wrap_socket(
                self.java_socket, server_hostname=self.java_address)
        self.socket.connect((self.java_address, self.java_port))
        self.stream = self.socket.makefile("rb", 0)

    def start_server(self, entry_point):
        if entry_point:
            self.pool.put(entry_point, proto.ENTRY_POINT_OBJECT_ID)
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(
            socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            self.server_socket.bind((self.python_address, self.python_port))
            self._listening_address, self._listening_port =\
                self.server_socket.getsockname()
        except Exception as e:
            msg = "An error occurred while trying to start the callback "\
                  "server ({0}:{1})".format(
                      self.python_address, self.python_port)
            logger.exception(msg)
            raise Py4JNetworkError(msg, e)

        try:
            logger.info("Python Server Starting")
            self.server_socket.listen(5)
            logger.info(
                "Socket listening on {0}".
                format(smart_decode(self.server_socket.getsockname())))

            read_list = [self.server_socket]
            accepted_socket = False
            while not accepted_socket:
                readable, writable, errored = select.select(
                    read_list, [], [], DEFAULT_CALLBACK_SERVER_ACCEPT_TIMEOUT)

                for s in readable:
                    self.socket, _ = self.server_socket.accept()
                    if self.ssl_context:
                        self.socket = self.ssl_context.wrap_socket(
                            self.socket, server_side=True)
                    self.stream = self.socket.makefile("rb", 0)
                    accepted_socket = True
                    break
        except Exception:
            logger.exception("Error while waiting for a connection.")

        self.wait_for_commands()
        self.close_server()

    def send_command(self, command):
        if not self.socket:
            self.connect_to_java_server()

        logger.debug("Command to send: {0}".format(command))
        try:
            self.socket.sendall(command.encode("utf-8"))
            while True:
                answer = smart_decode(self.stream.readline()[:-1])
                logger.debug("Answer received: {0}".format(answer))
                # Happens when a the other end is dead. There might be an empty
                # answer before the socket raises an error.
                if answer.strip() == "":
                    self.close_client()
                    raise Py4JError("Answer from Java side is empty")
                if answer.startswith(proto.RETURN_MESSAGE):
                    return answer[1:]
                else:
                    # TODO COMPLETE THIS BY COPYING CALLBACKCONNECTION
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
        """For backward compatibility.

        :return:
        """
        self.close_client

    def close_client(self):
        logger.info("Closing down client")
        quiet_close(self.stream)
        quiet_shutdown(self.socket)
        quiet_close(self.socket)

    def close_server(self):
        quiet_shutdown(self.server_socket)
        quiet_close(self.server_socket)

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

        self.close_client()

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
            param = get_return_value("y" + temp, self)
            params.append(param)
            temp = smart_decode(input.readline())[:-1]
        return params


class ClientServer(object):

    def __init__(self, java_parameters, python_parameters):
        self.java_parameters = java_parameters
        self.python_parameters = python_parameters
        self.client_server_connection = ClientServerConnection(
            java_parameters, python_parameters)

        self.entry_point = JavaObject(
            proto.ENTRY_POINT_OBJECT_ID, self.client_server_connection)

        self.java_gateway_server = JavaObject(
            proto.GATEWAY_SERVER_OBJECT_ID, self.client_server_connection)

        if self.java_parameters.auto_convert:
            self.client_server_connection.converters = proto.INPUT_CONVERTER
        else:
            self.client_server_connection.converters = None

        self.jvm = JVMView(
            self.client_server_connection, jvm_name=proto.DEFAULT_JVM_NAME,
            id=proto.DEFAULT_JVM_ID)
