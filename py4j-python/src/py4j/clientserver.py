# -*- coding: UTF-8 -*-

from __future__ import unicode_literals, absolute_import

import logging
import select
import socket
from threading import local, Thread

from py4j.java_gateway import (
    DEFAULT_CALLBACK_SERVER_ACCEPT_TIMEOUT,
    quiet_close, quiet_shutdown, GatewayClient, JavaGateway,
    CallbackServerParameters, GatewayParameters, CallbackServer)
from py4j import protocol as proto
from py4j.protocol import (
    Py4JError, Py4JNetworkError, smart_decode, get_command_part,
    get_return_value)


logger = logging.getLogger("py4j.clientserver")

thread_connection = local()


JavaParameters = GatewayParameters

PythonParameters = CallbackServerParameters


class JavaClient(GatewayClient):

    def __init__(
            self, java_parameters, python_parameters, gateway_property=None):
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
        except AttributeError:
            connection = ClientServerConnection(
                self.java_parameters, self.python_parameters,
                self.gateway_property, self)
            thread_connection.connection = connection
            self.deque.append(connection)
        return connection

    def _give_back_connection(self, connection):
        # Nothing to do for now
        pass

    def send_command(self, command, retry=True):
        # Never retry with this connection model.
        return super(JavaClient, self).send_command(command, retry=False)


class PythonServer(CallbackServer):

    def __init__(
            self, java_client, java_parameters, python_parameters,
            gateway_property):
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
    def __init__(
            self, java_parameters, python_parameters, gateway_property,
            gateway_client):
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

        # TODO
        self.gateway_client = gateway_client

    def connect_to_java_server(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        if self.ssl_context:
            self.socket = self.ssl_context.wrap_socket(
                self.socket, server_hostname=self.java_address)
        self.socket.connect((self.java_address, self.java_port))
        self.stream = self.socket.makefile("rb", 0)
        self.is_connected = True

    def init_socket_from_python_server(self, socket, stream):
        self.socket = socket
        self.stream = stream
        self.is_connected = True

    def shutdown_gateway(self):
        """Sends a shutdown command to the gateway. This will close the gateway
           server: all active connections will be closed. This may be useful
           if the lifecycle of the Java program must be tied to the Python
           program.
        """
        if not self.is_connected:
            raise Py4JError("Gateway must be connected to send shutdown cmd.")

        try:
            quiet_close(self.stream)
            self.socket.sendall(
                proto.SHUTDOWN_GATEWAY_COMMAND_NAME.encode("utf-8"))
            quiet_close(self.socket)
            self.is_connected = False
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
        self.close_client()

    def close_client(self):
        logger.info("Closing down client")
        quiet_close(self.stream)
        quiet_shutdown(self.socket)
        quiet_close(self.socket)

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
            param = get_return_value("y" + temp, self.gateway_client)
            params.append(param)
            temp = smart_decode(input.readline())[:-1]
        return params


class ClientServer(JavaGateway):

    def __init__(
            self, java_parameters, python_parameters,
            python_server_entry_point=None):
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
