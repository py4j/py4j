# -*- coding: UTF-8 -*-
"""Module to interact with objects in a Java Virtual Machine from a
Pyton Virtual Machine.

Variables that might clash with the JVM start with an underscore
(Java Naming Convention do not recommend to start with an underscore
so clashes become unlikely).

Created on Dec 3, 2009

:author: Barthelemy Dagenais
"""
from __future__ import unicode_literals
from collections import deque
from pydoc import ttypager
from socket import AF_INET, SOCK_STREAM
from threading import Thread, RLock
import logging
import socket
import weakref
import os
from traceback import print_exc

from py4j.finalizer import ThreadSafeFinalizer
from py4j.protocol import *
from py4j.compat import range, hasattr2, isbytearray


class NullHandler(logging.Handler):
    def emit(self, record):
        pass

null_handler = NullHandler()
logging.getLogger("py4j").addHandler(null_handler)
logger = logging.getLogger("py4j.java_gateway")

BUFFER_SIZE = 4096
DEFAULT_PORT = 25333
DEFAULT_PYTHON_PROXY_PORT = 25334
PY4J_SKIP_COLLECTIONS = 'PY4J_SKIP_COLLECTIONS'
PY4J_TRUE = set(['yes', 'y', 't', 'true'])


def java_import(jvm_view, import_str):
    """Imports the package or class specified by `import_str` in the
    jvm view namespace.

    :param jvm_view: The jvm_view in which to import a class/package.
    :import_str: The class (e.g., java.util.List) or the package
                 (e.g., java.io.*) to import
    """
    gateway_client = jvm_view._gateway_client
    command = JVMVIEW_COMMAND_NAME + JVM_IMPORT_SUB_COMMAND_NAME +\
            jvm_view._id + '\n' + escape_new_line(import_str) + '\n' +\
            END_COMMAND_PART + '\n' + escape_new_line(import_str) + '\n' +\
            END_COMMAND_PART
    answer = gateway_client.send_command(command)
    return_value = get_return_value(answer, gateway_client, None, None)
    return return_value


def get_field(java_object, field_name):
    """Retrieves the field named `field_name` from the `java_object`.

    This function is useful when `auto_field=false` in a gateway or
    Java object.

    :param java_object: the instance containing the field
    :param field_name: the name of the field to retrieve
    """
    command = FIELD_COMMAND_NAME + FIELD_GET_SUBCOMMAND_NAME +\
            java_object._target_id + '\n' + field_name + '\n' +\
            END_COMMAND_PART
    answer = java_object._gateway_client.send_command(command)

    if answer == NO_MEMBER_COMMAND or is_error(answer)[0]:
        raise Py4JError('no field {0} in object {1}'.format(
            field_name, java_object._target_id))
    else:
        return get_return_value(answer, java_object._gateway_client,
                java_object._target_id, field_name)


def set_field(java_object, field_name, value):
    """Sets the field named `field_name` of `java_object` to `value`.

    This function is the only way to set a field because the assignment
    operator in Python cannot be overloaded.

    :param java_object: the instance containing the field
    :param field_name: the name of the field to set
    :param value: the value to assign to the field
    """

    command_part = get_command_part(value,
            java_object._gateway_client.gateway_property.pool)

    command = FIELD_COMMAND_NAME + FIELD_SET_SUBCOMMAND_NAME +\
            java_object._target_id + '\n' + field_name + '\n' +\
            command_part + '\n' + END_COMMAND_PART

    answer = java_object._gateway_client.send_command(command)
    if answer == NO_MEMBER_COMMAND or is_error(answer)[0]:
        raise Py4JError('no field {0} in object {1}'.format(
            field_name, java_object._target_id))
        return get_return_value(answer, java_object._gateway_client,
            java_object._target_id, field_name)


def get_method(java_object, method_name):
    """Retrieves a reference to the method of an object.

    This function is useful when `auto_field=true` and an instance field has
    the same name as a method. The full signature of the method is not
    required: it is determined when the method is called.

    :param java_object: the instance containing the method
    :param method_name: the name of the method to retrieve
    """
    return JavaMember(method_name, java_object, java_object._target_id,
            java_object._gateway_client)


def _garbage_collect_object(gateway_client, target_id):
#    print(target_id + ' deleted')
    ThreadSafeFinalizer.remove_finalizer(smart_decode(gateway_client.address) +
            smart_decode(gateway_client.port) + target_id)
    if target_id != ENTRY_POINT_OBJECT_ID and gateway_client.is_connected:
        try:
            gateway_client.send_command(MEMORY_COMMAND_NAME +
                                        MEMORY_DEL_SUBCOMMAND_NAME +
                                        target_id +
                                        '\ne\n'
                                        )
        except:
            pass


def _garbage_collect_connection(socket):
    """Closes the socket if auto_delete is True and the socket is opened.

    This is an acceptable practice if you know that your Python VM implements
    garbage collection and closing sockets immediately is not a concern.
    Otherwise, it is always better (because it is predictable) to explicitly
    close the socket by calling `GatewayConnection.close()`.
    """
#    print('delete connection')
    if socket != None:
        try:
            socket.shutdown(socket.SHUT_RDWR)
            socket.close()
        except Exception:
            pass


class DummyRLock(object):
    def __init__(self):
        pass

    def acquire(self, blocking=1):
        pass

    def release(self):
        pass

    def __enter__(self):
        pass

    def __exit__(self, type, value, tb):
        pass


class GatewayClient(object):
    """Responsible for managing connections to the JavaGateway.

    This implementation is thread-safe and connections are created on-demand.
    This means that Py4J-Python can be accessed by multiple threads and
    messages are sent to and processed concurrently by the Java Gateway.

    When creating a custom :class:`JavaGateway`, it is recommended to pass an
    instance of :class:`GatewayClient` instead of a :class:`GatewayConnection`:
    both have the same interface, but the client supports multiple threads and
    connections, which is essential when using callbacks.  """

    def __init__(self, address='localhost', port=25333, auto_close=True,
            gateway_property=None):
        """
        :param address: the address to which the client will request a
         connection

        :param port: the port to which the client will request a connection.
         Default is 25333.

        :param auto_close: if `True`, the connections created by the client
         close the socket when they are garbage collected.

        :param gateway_property: used to keep gateway preferences without a
         cycle with the gateway
        """
        self.address = address
        self.port = port
        self.is_connected = True
        self.auto_close = auto_close
        self.gateway_property = gateway_property
        self.deque = deque()

    def _get_connection(self):
        if not self.is_connected:
            raise Py4JNetworkError('Gateway is not connected.')
        try:
            connection = self.deque.pop()
        except:
            connection = self._create_connection()
        return connection

    def _create_connection(self):
#        print('Creating connection')
        connection = GatewayConnection(self.address, self.port,
                self.auto_close, self.gateway_property)
        connection.start()
        return connection

    def _give_back_connection(self, connection):
        try:
            self.deque.append(connection)
        except:
            pass

    def shutdown_gateway(self):
        """Sends a shutdown command to the gateway. This will close the
           gateway server: all active connections will be closed. This may
           be useful if the lifecycle of the Java program must be tied to
           the Python program.
        """
        connection = self._get_connection()
        try:
            connection.shutdown_gateway()
            self.close()
            self.is_connected = False
        except Py4JNetworkError:
            self.shutdown_gateway()

    def send_command(self, command, retry=True):
        """Sends a command to the JVM. This method is not intended to be
           called directly by Py4J users. It is usually called by
           :class:`JavaMember` instances.

        :param command: the `string` command to send to the JVM. The command
         must follow the Py4J protocol.

        :param retry: if `True`, the GatewayClient tries to resend a message
         if it fails.

        :rtype: the `string` answer received from the JVM. The answer follows
         the Py4J protocol.
        """
        connection = self._get_connection()
        try:
            response = connection.send_command(command)
            self._give_back_connection(connection)
        except Py4JNetworkError:
            if retry:
                #print_exc()
                response = self.send_command(command)
            else:
                response = ERROR

        return response

    def close(self):
        """Closes all currently opened connections.

        This operation is not thread safe and is only a best effort strategy
        to close active connections.

        All connections are guaranteed to be closed only if no other thread
        is accessing the client and no call is pending.
        """
        size = len(self.deque)
        for _ in range(0, size):
            try:
                connection = deque.pop()
                connection.close()
            except:
                pass


class GatewayConnection(object):
    """Default gateway connection (socket based) responsible for communicating
       with the Java Virtual Machine."""

    def __init__(self, address='localhost', port=25333, auto_close=True,
            gateway_property=None):
        """
        :param address: the address to which the connection will be established

        :param port: the port to which the connection will be established.
         Default is 25333.

        :param auto_close: if `True`, the connection closes the socket when it
         is garbage collected.

        :param gateway_property: contains gateway preferences to avoid a cycle
         with gateway
        """
        self.address = address
        self.port = port
        self.socket = socket.socket(AF_INET, SOCK_STREAM)
        self.is_connected = False
        self.auto_close = auto_close
        self.gateway_property = gateway_property
        self.wr = weakref.ref(self,
            lambda wr, socket=self.socket: _garbage_collect_connection(socket))

    def start(self):
        """Starts the connection by connecting to the `address` and the `port`
        """
        self.socket.connect((self.address, self.port))
        self.is_connected = True
        self.stream = self.socket.makefile('rb', 0)

    def close(self, throw_exception=False):
        """Closes the connection by closing the socket."""
        try:
            self.stream.close()
            self.socket.shutdown(socket.SHUT_RDWR)
            self.socket.close()
        except Exception as e:
            if throw_exception:
                raise e
        finally:
            self.is_connected = False

    def shutdown_gateway(self):
        """Sends a shutdown command to the gateway. This will close the gateway
           server: all active connections will be closed. This may be useful
           if the lifecycle of the Java program must be tied to the Python
           program.
        """
        if (not self.is_connected):
            raise Py4JError('Gateway must be connected to send shutdown cmd.')

        try:
            self.stream.close()
            self.socket.sendall(SHUTDOWN_GATEWAY_COMMAND_NAME.encode('utf-8'))
            self.socket.close()
            self.is_connected = False
        except Exception:
            # Do nothing! Exceptions might occur anyway.
            pass

    def send_command(self, command):
        """Sends a command to the JVM. This method is not intended to be
           called directly by Py4J users: it is usually called by JavaMember
           instances.

        :param command: the `string` command to send to the JVM. The command
         must follow the Py4J protocol.

        :rtype: the `string` answer received from the JVM. The answer follows
         the Py4J protocol.
        """
        logger.debug("Command to send: %s" % (command))
        try:
            #print(command)
            self.socket.sendall(command.encode('utf-8'))
            answer = smart_decode(self.stream.readline()[:-1])
            logger.debug("Answer received: %s" % (answer))
            # Happens when a the other end is dead. There might be an empty
            # answer before the socket raises an error.
            if answer.strip() == '':
                self.close()
                raise Py4JError()
            return answer
        except:
            #print_exc()
            logger.exception('Error while sending or receiving.')
            raise Py4JNetworkError('Error while sending or receiving')


class JavaMember(object):
    """Represents a member (i.e., method) of a :class:`JavaObject`. For now,
       only methods are supported. Fields are retrieved directly and are not
       contained in a JavaMember.
    """

    def __init__(self, name, container, target_id, gateway_client):
        self.name = name
        self.container = container
        self.target_id = target_id
        self.gateway_client = gateway_client
        self.command_header = self.target_id + '\n' + self.name + '\n'
        self.pool = self.gateway_client.gateway_property.pool
        self.converters = self.gateway_client.converters

    def _get_args(self, args):
        temp_args = []
        new_args = []
        for arg in args:
            if not isinstance(arg, JavaObject) and \
               not isinstance(arg, basestring):
                for converter in self.gateway_client.converters:
                    if converter.can_convert(arg):
                        temp_arg = converter.convert(arg, self.gateway_client)
                        temp_args.append(temp_arg)
                        new_args.append(temp_arg)
                        break
                else:
                    new_args.append(arg)
            else:
                new_args.append(arg)

        return (new_args, temp_args)

    def __call__(self, *args):
        if self.converters is not None and len(self.converters) > 0:
            (new_args, temp_args) = self._get_args(args)
        else:
            new_args = args
            temp_args = []

        args_command = ''.join(
                [get_command_part(arg, self.pool) for arg in new_args])

        command = CALL_COMMAND_NAME +\
            self.command_header +\
            args_command +\
            END_COMMAND_PART

        answer = self.gateway_client.send_command(command)
        return_value = get_return_value(answer, self.gateway_client,
                self.target_id, self.name)

        for temp_arg in temp_args:
            temp_arg._detach()

        return return_value


class JavaObject(object):
    """Represents a Java object from which you can call methods or access
       fields."""

    def __init__(self, target_id, gateway_client):
        """
        :param target_id: the identifier of the object on the JVM side. Given
         by the JVM.

        :param gateway_client: the gateway client used to communicate with
         the JVM.
        """
#        print(target_id + ' created.')
        self._target_id = target_id
        self._gateway_client = gateway_client
        self._auto_field = gateway_client.gateway_property.auto_field
        self._methods = {}

        key = smart_decode(self._gateway_client.address) +\
              smart_decode(self._gateway_client.port) +\
              self._target_id

        value = weakref.ref(self, lambda wr, cc=self._gateway_client,
                id=self._target_id: _garbage_collect_object(cc, id))

        ThreadSafeFinalizer.add_finalizer(key, value)

    def _detach(self):
        _garbage_collect_object(self._gateway_client, self._target_id)

    def _get_object_id(self):
        return self._target_id

    def __getattr__(self, name):
        if name not in self._methods:
            if (self._auto_field):
                (is_field, return_value) = self._get_field(name)
                if (is_field):
                    return return_value
            # Theoretically, not thread safe, but the worst case scenario is
            # cache miss or double overwrite of the same method...
            self._methods[name] = JavaMember(name, self, self._target_id,
                    self._gateway_client)

        # The name is a method
        return self._methods[name]

    def _get_field(self, name):
        command = FIELD_COMMAND_NAME +\
            FIELD_GET_SUBCOMMAND_NAME +\
            self._target_id + '\n' +\
            name + '\n' +\
            END_COMMAND_PART

        answer = self._gateway_client.send_command(command)
        if answer == NO_MEMBER_COMMAND or is_error(answer)[0]:
            return (False, None)
        else:
            return_value = get_return_value(answer, self._gateway_client,
                    self._target_id, name)
            return (True, return_value)

    def __eq__(self, other):
        if other == None:
            return False
        elif (hasattr2(other, '_get_object_id')):
            return self.equals(other)
        else:
            return other.__eq__(self)

    def __hash__(self):
        return self.hashCode()

    def __str__(self):
        return self.toString()

    def __repr__(self):
        # For now...
        return 'JavaObject id=' + self._target_id


class JavaClass():
    """A `JavaClass` represents a Java Class from which static members can be
       retrieved. `JavaClass` instances are also needed to initialize an array.

       Usually, `JavaClass` are not initialized using their constructor, but
       they are created while accessing the `jvm` property of a gateway, e.g.,
       `gateway.jvm.java.lang.String`.
    """
    def __init__(self, fqn, gateway_client):
        self._fqn = fqn
        self._gateway_client = gateway_client
        self._command_header = fqn + '\n'

    def __getattr__(self, name):
        command = REFLECTION_COMMAND_NAME +\
            REFL_GET_MEMBER_SUB_COMMAND_NAME +\
            self._fqn + '\n' +\
            name + '\n' +\
            END_COMMAND_PART
        answer = self._gateway_client.send_command(command)

        if len(answer) > 1 and answer[0] == SUCCESS:
            if answer[1] == METHOD_TYPE:
                return JavaMember(name, None, STATIC_PREFIX + self._fqn,
                        self._gateway_client)
            elif answer[1].startswith(CLASS_TYPE):
                return JavaClass(answer[CLASS_FQN_START:],
                        self._gateway_client)
            else:
                return get_return_value(answer, self._gateway_client,
                        self._fqn, name)
        else:
            raise Py4JError('{0} does not exist in the JVM'.
                    format(self._fqn + name))

    def __call__(self, *args):
        args_command = ''.join([get_command_part(arg) for arg in args])
        command = CONSTRUCTOR_COMMAND_NAME +\
            self._command_header +\
            args_command +\
            END_COMMAND_PART
        answer = self._gateway_client.send_command(command)
        return_value = get_return_value(answer, self._gateway_client, None,
                self._fqn)
        return return_value


class JavaPackage():
    """A `JavaPackage` represents part of a Java package from which Java
       classes can be accessed.

       Usually, `JavaPackage` are not initialized using their constructor, but
       they are created while accessing the `jvm` property of a gateway, e.g.,
       `gateway.jvm.java.lang`.
    """
    def __init__(self, fqn, gateway_client, jvm_id=None):
        self._fqn = fqn
        self._gateway_client = gateway_client
        if jvm_id is None:
            self._jvm_id = DEFAULT_JVM_ID
        self._jvm_id = jvm_id

    def __getattr__(self, name):
        if name == '__call__':
            raise Py4JError('Trying to call a package.')
        new_fqn = self._fqn + '.' + name
        command = REFLECTION_COMMAND_NAME +\
                REFL_GET_UNKNOWN_SUB_COMMAND_NAME +\
                new_fqn + '\n' +\
                self._jvm_id + '\n' +\
                END_COMMAND_PART
        answer = self._gateway_client.send_command(command)
        if answer == SUCCESS_PACKAGE:
            return JavaPackage(new_fqn, self._gateway_client, self._jvm_id)
        elif answer.startswith(SUCCESS_CLASS):
            return JavaClass(answer[CLASS_FQN_START:], self._gateway_client)
        else:
            raise Py4JError('%s does not exist in the JVM' % new_fqn)


class JVMView(object):
    """A `JVMView` allows access to the Java Virtual Machine of a
       `JavaGateway`.

       This can be used to reference static members (fields and methods) and
       to call constructors.
    """

    def __init__(self, gateway_client, jvm_name, id=None, jvm_object=None):
        self._gateway_client = gateway_client
        self._jvm_name = jvm_name
        if id is not None:
            self._id = id
        elif jvm_object is not None:
            self._id = REFERENCE_TYPE + jvm_object._get_object_id()
            # So that both JVMView instances (on Python and Java) have the
            # same lifecycle. Theoretically, JVMView could inherit from
            # JavaObject, but I would like to avoid the use of reflection
            # for regular Py4J classes.
            self._jvm_object = jvm_object

    def __getattr__(self, name):
        answer = self._gateway_client.send_command(REFLECTION_COMMAND_NAME +\
                REFL_GET_UNKNOWN_SUB_COMMAND_NAME + name + '\n' + self._id +\
                '\n' + END_COMMAND_PART)
        if answer == SUCCESS_PACKAGE:
            return JavaPackage(name, self._gateway_client, jvm_id=self._id)
        elif answer.startswith(SUCCESS_CLASS):
            return JavaClass(answer[CLASS_FQN_START:], self._gateway_client)
        else:
            raise Py4JError('%s does not exist in the JVM' % name)


class GatewayProperty(object):
    def __init__(self, auto_field, pool):
        self.auto_field = auto_field
        self.pool = pool


class JavaGateway(object):
    """A `JavaGateway` is the main interaction point between a Python VM and
       a JVM.

    * A `JavaGateway` instance is connected to a `Gateway` instance on the
      Java side.

    * The `entry_point` field of a `JavaGateway` instance is connected to
      the `Gateway.entryPoint` instance on the Java side.

    * The `jvm` field of `JavaGateway` enables user to access classes, static
      members (fields and methods) and call constructors.

    Methods that are not defined by `JavaGateway` are always redirected to
    `entry_point`. For example, ``gateway.doThat()`` is equivalent to
    ``gateway.entry_point.doThat()``. This is a trade-off between convenience
    and potential confusion.
    """

    def __init__(self, gateway_client=None, auto_field=False,
            python_proxy_port=DEFAULT_PYTHON_PROXY_PORT,
            start_callback_server=False, auto_convert=False):
        """
        :param gateway_client: gateway client used to connect to the JVM. If
         `None`, a gateway client based on a socket with the default
         parameters is created.

        :param auto_field: if `False`, each object accessed through this
         gateway won't try to lookup fields (they will be accessible only by
         calling get_field). If `True`, fields will be automatically looked
         up, possibly hiding methods of the same name and making method calls
         less efficient.

        :param python_proxy_port: port used to receive callback from the JVM.

        :param start_callback_server: if `True`, the callback server is
         started.

        :param auto_convert: if `True`, try to automatically convert Python
         objects like sequences and maps to Java Objects. Default value is
         `False` to improve performance and because it is still possible to
         explicitly perform this conversion.
        """
        self.gateway_property = GatewayProperty(auto_field, PythonProxyPool())
        self._python_proxy_port = python_proxy_port

        if gateway_client == None:
            gateway_client = GatewayClient()

        if auto_convert:
            gateway_client.converters = INPUT_CONVERTER
        else:
            gateway_client.converters = None

        gateway_client.gateway_property = self.gateway_property

        self._gateway_client = gateway_client

        self.entry_point = JavaObject(ENTRY_POINT_OBJECT_ID, gateway_client)
        self.jvm = JVMView(gateway_client, jvm_name=DEFAULT_JVM_NAME,
                id=DEFAULT_JVM_ID)
        if start_callback_server:
            self._callback_server = CallbackServer(self.gateway_property.pool,
                    self._gateway_client, python_proxy_port)
            self._callback_server.start()

    def __getattr__(self, name):
        return self.entry_point.__getattr__(name)

    def new_jvm_view(self, name='custom jvm'):
        """Creates a new JVM view with its own imports. A JVM view ensures
        that the import made in one view does not conflict with the import
        of another view.

        Generally, each Python module should have its own view (to replicate
        Java behavior).

        :param name: Optional name of the jvm view. Does not need to be
         unique, i.e., two distinct views can have the same name
         (internally, they will have a distinct id).

        :rtype: A JVMView instance (same class as the gateway.jvm instance).
        """
        command = JVMVIEW_COMMAND_NAME +\
            JVM_CREATE_VIEW_SUB_COMMAND_NAME +\
            get_command_part(name) +\
            END_COMMAND_PART

        answer = self._gateway_client.send_command(command)
        java_object = get_return_value(answer, self._gateway_client)

        return JVMView(gateway_client=self._gateway_client, jvm_name=name,
                jvm_object=java_object)

    def new_array(self, java_class, *dimensions):
        """Creates a Java array of type `java_class` of `dimensions`

        :param java_class: The :class:`JavaClass` instance representing the
         type of the array.

        :param dimensions: A list of dimensions of the array. For example
         `[1,2]` would produce an `array[1][2]`.

        :rtype: A :class:`JavaArray <py4j.java_collections.JavaArray>`
         instance.
        """
        if len(dimensions) == 0:
            raise Py4JError('new arrays must have at least one dimension')
        command = ARRAY_COMMAND_NAME +\
                  ARRAY_CREATE_SUB_COMMAND_NAME +\
                  get_command_part(java_class._fqn)
        for dimension in dimensions:
            command += get_command_part(dimension)
        command += END_COMMAND_PART
        answer = self._gateway_client.send_command(command)
        return get_return_value(answer, self._gateway_client)

    def shutdown(self):
        """Shuts down the :class:`GatewayClient` and the
           :class:`CallbackServer <py4j.java_callback.CallbackServer>`.
        """
        try:
            self._gateway_client.shutdown_gateway()
        except:
            pass
        self._shutdown_callback_server()

    def _shutdown_callback_server(self):
        """Shuts down the
           :class:`CallbackServer <py4j.java_callback.CallbackServer>`.
        """
        try:
            self._callback_server.shutdown()
        except:
            pass

    def restart_callback_server(self):
        """Shuts down the callback server (if started) and restarts a new one.
        """
        self._shutdown_callback_server()
        self._callback_server = CallbackServer(self.gateway_property.pool,
                self._gateway_client, self._python_proxy_port)
        self._callback_server.start()

    def close(self, keep_callback_server=False):
        """Closes all gateway connections. A connection will be reopened if
           necessary (e.g., if a :class:`JavaMethod` is called).

        :param keep_callback_server: if `True`, the callback server is not
         shut down.
        """
        self._gateway_client.close()
        if not keep_callback_server:
            self._shutdown_callback_server()

    def detach(self, java_object):
        """Makes the Java Gateway dereference this object.

        The equivalent of this method is called when a JavaObject instance
        is garbage collected on the Python side. This method, or gc.collect()
        should still be invoked when memory is limited or when too many objects
        are created on the Java side.

        :param java_object: The JavaObject instance to dereference (free) on
         the Java side.
        """
        java_object._detach()

    def help(self, var, pattern=None, short_name=True, display=True):
        """Displays a help page about a class or an object.

        :param var: JavaObject or JavaClass for which a help page will be
         generated.

        :param pattern: Star-pattern used to filter the members. For example
         'get*Foo' may return getMyFoo, getFoo, getFooBar, but not bargetFoo.

        :param short_name: If True, only the simple name of the parameter
         types and return types will be displayed. If False, the fully
         qualified name of the types will be displayed.

        :param display: If True, the help page is displayed in an interactive
         page similar to the `help` command in Python. If False, the page is
         returned as a string.
        """
        if hasattr2(var, '_get_object_id'):
            command = HELP_COMMAND_NAME +\
                      HELP_OBJECT_SUBCOMMAND_NAME +\
                      var._get_object_id() + '\n' +\
                      get_command_part(pattern) +\
                      get_command_part(short_name) +\
                      END_COMMAND_PART
            answer = self._gateway_client.send_command(command)
        elif hasattr2(var, '_fqn'):
            command = HELP_COMMAND_NAME +\
                      HELP_CLASS_SUBCOMMAND_NAME +\
                      var._fqn + '\n' +\
                      get_command_part(pattern) +\
                      get_command_part(short_name) +\
                      END_COMMAND_PART
            answer = self._gateway_client.send_command(command)
        else:
            raise Py4JError('var is neither a Java Object nor a Java Class')

        help_page = get_return_value(answer, self._gateway_client, None, None)
        if (display):
            ttypager(help_page)
        else:
            return help_page


# CALLBACK SPECIFIC


class CallbackServer(object):
    """The CallbackServer is responsible for receiving call back connection
       requests from the JVM. Usually connections are reused on the Java side,
       but there is at least one connection per concurrent thread.
    """

    def __init__(self, pool, gateway_client, port=DEFAULT_PYTHON_PROXY_PORT):
        """
        :param pool: the pool responsible of tracking Python objects passed to
         the Java side.

        :param gateway_client: the gateway client used to call Java objects.

        :param port: the port the CallbackServer is listening to.
        """
        super(CallbackServer, self).__init__()
        self.gateway_client = gateway_client
        self.port = port
        self.pool = pool
        self.connections = []
        # Lock is used to isolate critical region like connection creation.
        # Some code can produce exceptions when ran in parallel, but
        # They will be caught and dealt with.
        self.lock = RLock()
        self.is_shutdown = False

    def start(self):
        """Starts the CallbackServer. This method should be called by the
        client instead of run()."""
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR,
                1)
        self.server_socket.bind(('localhost', self.port))

        # Maybe thread needs to be cleanup up?
        self.thread = Thread(target=self.run)
        self.thread.start()

    def run(self):
        """Starts listening and accepting connection requests.

           This method is called when invoking `CallbackServer.start()`. A
           CallbackServer instance is created and started automatically when
           a :class:`JavaGateway <py4j.java_gateway.JavaGateway>` instance is
           created.
        """
        try:
            with self.lock:
                self.is_shutdown = False
            logger.info('Callback Server Starting')
            self.server_socket.listen(5)
            logger.info('Socket listening on {0}'.
                    format(smart_decode(self.server_socket.getsockname())))

            while not self.is_shutdown:
                socket, _ = self.server_socket.accept()
                input = socket.makefile('rb', 0)
                connection = CallbackConnection(self.pool, input, socket,
                        self.gateway_client)
                with self.lock:
                    if not self.is_shutdown:
                        self.connections.append(connection)
                        connection.start()
                    else:
                        connection.socket.shutdown(socket.SHUT_RDWR)
                        connection.socket.close()
        except:
            logger.exception('Error while waiting for a connection.')

    def shutdown(self):
        """Stops listening and accepting connection requests. All live
           connections are closed.

           This method can safely be called by another thread.
        """
        logger.info('Callback Server Shutting Down')
        with self.lock:
            self.is_shutdown = True
            try:
                self.server_socket.shutdown(socket.SHUT_RDWR)
                self.server_socket.close()
                self.server_socket = None
            except:
                pass

            for connection in self.connections:
                try:
                    connection.socket.shutdown(socket.SHUT_RDWR)
                    connection.socket.close()
                except:
                    pass

            self.pool.clear()
        self.thread.join()
        self.thread = None


class CallbackConnection(Thread):
    """A `CallbackConnection` receives callbacks and garbage collection
       requests from the Java side.
    """
    def __init__(self, pool, input, socket, gateway_client):
        super(CallbackConnection, self).__init__()
        self.pool = pool
        self.input = input
        self.socket = socket
        self.gateway_client = gateway_client

    def run(self):
        logger.info('Callback Connection ready to receive messages')
        try:
            while True:
                command = smart_decode(self.input.readline())[:-1]
                obj_id = smart_decode(self.input.readline())[:-1]
                logger.info('Received command {0} on object id {1}'.
                        format(command, obj_id))
                if obj_id is None or len(obj_id.strip()) == 0:
                    break
                if command == CALL_PROXY_COMMAND_NAME:
                    return_message = self._call_proxy(obj_id, self.input)
                    self.socket.sendall(return_message.encode('utf-8'))
                elif command == GARBAGE_COLLECT_PROXY_COMMAND_NAME:
                    self.input.readline()
                    del(self.pool[obj_id])
                else:
                    logger.error('Unknown command %s' % command)
        except:
            logger.exception('Error while callback connection was waiting for'
                'a message')

        try:
            logger.info('Closing down connection')
            self.socket.shutdown(socket.SHUT_RDWR)
            self.socket.close()
        except Exception:
            pass

    def _call_proxy(self, obj_id, input):
        return_message = ERROR_RETURN_MESSAGE
        if obj_id in self.pool:
            try:
                method = smart_decode(input.readline())[:-1]
                params = self._get_params(input)
                return_value = getattr(self.pool[obj_id], method)(*params)
                return_message = 'y' +\
                        get_command_part(return_value, self.pool)
            except Exception:
                #print_exc()
                logger.exception('There was an exception while executing the '\
                                 'Python Proxy on the Python Side.')
        return return_message

    def _get_params(self, input):
        params = []
        temp = smart_decode(input.readline())[:-1]
        while temp != END:
            param = get_return_value('y' + temp, self.gateway_client)
            params.append(param)
            temp = smart_decode(input.readline())[:-1]
        return params


class PythonProxyPool(object):
    """A `PythonProxyPool` manages proxies that are passed to the Java side.
       A proxy is a Python class that implements a Java interface.

       A proxy has an internal class named `Java` with a member named
       `implements` which is a list of fully qualified names (string) of the
       implemented interfaces.

       The `PythonProxyPool` implements a subset of the dict interface:
       `pool[id]`, `del(pool[id])`, `pool.put(proxy)`, `pool.clear()`,
       `id in pool`, `len(pool)`.

       The `PythonProxyPool` is thread-safe.
    """
    def __init__(self):
        self.lock = RLock()
        self.dict = {}
        self.next_id = 0

    def put(self, object):
        """Adds a proxy to the pool.

        :param object: The proxy to add to the pool.
        :rtype: A unique identifier associated with the object.
        """
        with self.lock:
            id = PYTHON_PROXY_PREFIX + smart_decode(self.next_id)
            self.next_id += 1
            self.dict[id] = object
        return id

    def __getitem__(self, key):
        with self.lock:
            return self.dict[key]

    def __delitem__(self, key):
        with self.lock:
            del(self.dict[key])

    def clear(self):
        with self.lock:
            self.dict.clear()

    def __contains__(self, key):
        with self.lock:
            return key in self.dict

    def __len__(self):
        with self.lock:
            return len(self.dict)

# Basic registration
register_output_converter(REFERENCE_TYPE,
    lambda target_id, gateway_client: JavaObject(target_id, gateway_client))

if PY4J_SKIP_COLLECTIONS not in os.environ or\
   os.environ[PY4J_SKIP_COLLECTIONS].lower() not in PY4J_TRUE:
    __import__('py4j.java_collections')
