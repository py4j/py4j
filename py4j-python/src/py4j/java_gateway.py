# -*- coding: UTF-8 -*-
"""Module to interact with objects in a Java Virtual Machine from a Pyton Virtual Machine.

Variables that might clash with the JVM start with an underscore (Java Naming Convention do not 
recommend to start with an underscore so clashes become unlikely).

Created on Dec 3, 2009

@author: Barthelemy Dagenais
"""

from collections import deque
from pydoc import ttypager
from socket import AF_INET, SOCK_STREAM
import logging
import socket
import weakref


class NullHandler(logging.Handler):
    def emit(self, record):
        pass

null_handler = NullHandler()
logging.getLogger("py4j").addHandler(null_handler)
logger = logging.getLogger("py4j.java_gateway")

BUFFER_SIZE = 4096
DEFAULT_PORT = 25333
DEFAULT_PYTHON_PROXY_PORT = 25334

ESCAPE_CHAR = "\\"

# Entry point
ENTRY_POINT_OBJECT_ID = 't'
CONNECTION_PROPERTY_OBJECT_ID = 'c'
STATIC_PREFIX = 'z:'

# JVM
DEFAULT_JVM_ID = 'rj'
DEFAULT_JVM_NAME = 'default'

# Types
INTEGER_TYPE = 'i'
BOOLEAN_TYPE = 'b'
DOUBLE_TYPE = 'd'
STRING_TYPE = 's'
REFERENCE_TYPE = 'r'
ARRAY_TYPE = 't'
SET_TYPE = 'h'
LIST_TYPE = 'l'
MAP_TYPE = 'a'
NULL_TYPE = 'n'
PACKAGE_TYPE = 'p';
CLASS_TYPE = 'c';
METHOD_TYPE = 'm';
NO_MEMBER = 'o';
VOID_TYPE = 'v'
ITERATOR_TYPE = 'g'
PYTHON_PROXY_TYPE = 'f'

# Protocol
END = 'e'
ERROR = 'x'
SUCCESS = 'y'



# Shortcuts
SUCCESS_PACKAGE = SUCCESS + PACKAGE_TYPE
SUCCESS_CLASS = SUCCESS + CLASS_TYPE
CLASS_FQN_START = 2
END_COMMAND_PART = END + '\n'
NO_MEMBER_COMMAND = SUCCESS + NO_MEMBER

# Commands
CALL_COMMAND_NAME = 'c\n'
FIELD_COMMAND_NAME = 'f\n'
CONSTRUCTOR_COMMAND_NAME = 'i\n'
SHUTDOWN_GATEWAY_COMMAND_NAME = 's\n'
LIST_COMMAND_NAME = 'l\n'
REFLECTION_COMMAND_NAME = "r\n"
MEMORY_COMMAND_NAME = "m\n"
HELP_COMMAND_NAME = 'h\n'
ARRAY_COMMAND_NAME = "a\n"
JVMVIEW_COMMAND_NAME = "j\n";


# Array subcommands
ARRAY_GET_SUB_COMMAND_NAME = 'g\n'
ARRAY_SET_SUB_COMMAND_NAME = 's\n'
ARRAY_SLICE_SUB_COMMAND_NAME = 'l\n'
ARRAY_LEN_SUB_COMMAND_NAME = 'e\n'
ARRAY_CREATE_SUB_COMMAND_NAME = 'c\n'

# Reflection subcommands
REFL_GET_UNKNOWN_SUB_COMMAND_NAME = 'u\n'
REFL_GET_MEMBER_SUB_COMMAND_NAME = 'm\n'
    

# List subcommands
LIST_SORT_SUBCOMMAND_NAME = 's\n'
LIST_REVERSE_SUBCOMMAND_NAME = 'r\n'
LIST_SLICE_SUBCOMMAND_NAME = 'l\n'
LIST_CONCAT_SUBCOMMAND_NAME = 'a\n'
LIST_MULT_SUBCOMMAND_NAME = 'm\n'
LIST_IMULT_SUBCOMMAND_NAME = 'i\n'
LIST_COUNT_SUBCOMMAND_NAME = 'f\n'

# Field subcommands
FIELD_GET_SUBCOMMAND_NAME = 'g\n'
FIELD_SET_SUBCOMMAND_NAME = 's\n'

# Memory subcommands
MEMORY_DEL_SUBCOMMAND_NAME = 'd\n'
MEMORY_ATTACH_SUBCOMMAND_NAME = 'a\n'

# Help subcommands
HELP_OBJECT_SUBCOMMAND_NAME = 'o\n'
HELP_CLASS_SUBCOMMAND_NAME = 'c\n'

# JVM subcommands
JVM_CREATE_VIEW_SUB_COMMAND_NAME = 'c\n'
JVM_IMPORT_SUB_COMMAND_NAME = 'i\n'
JVM_SEARCH_SUB_COMMAND_NAME = 's\n'

CONVERSION = {NULL_TYPE: (lambda x, y: None),
              REFERENCE_TYPE: (lambda target_id, gateway_client: JavaObject(target_id, gateway_client)),
              MAP_TYPE: (lambda target_id, gateway_client: JavaMap(target_id, gateway_client)),
              LIST_TYPE: (lambda target_id, gateway_client: JavaList(target_id, gateway_client)),
              ARRAY_TYPE: (lambda target_id, gateway_client: JavaArray(target_id, gateway_client)),
              SET_TYPE: (lambda target_id, gateway_client: JavaSet(target_id, gateway_client)),
              ITERATOR_TYPE: (lambda target_id, gateway_client: JavaIterator(target_id, gateway_client)),
              BOOLEAN_TYPE: (lambda value, y: value.lower() == 'true'),
              INTEGER_TYPE: (lambda value, y: int(value)),
              DOUBLE_TYPE: (lambda value, y: float(value)),
              STRING_TYPE: (lambda value, y: unescape_new_line(value)),
              }

def escape_new_line(original):
    """Replaces new line characters by a backslash followed by a n.
    
    Backslashes are also escaped by another backslash.
    
    :param original: the string to escape
    
    :rtype: an escaped string
    """
    return original.replace('\\', '\\\\').replace('\r','\\r').replace('\n','\\n')

def unescape_new_line(escaped):
    """Replaces escaped characters by unescaped characters.
    
    For example, double backslashes are replaced by a single backslash.
    
    :param escaped: the escaped string
    
    :rtype: the original string
    """
    escaping = False
    original = ''
    for c in escaped:
        if not escaping:
            if c == ESCAPE_CHAR:
                escaping = True
            else:
                original += c
        else:
            if c == 'n':
                original += '\n'
            elif c == 'r':
                original += '\r'
            else:
                original += c
            escaping = False
            
    return original

    
def is_python_proxy(parameter):
    """Determines whether parameter is a Python Proxy, i.e., it has a Java internal class with an
    implements member.
    :param parameter: the object to check.
    :rtype: True if the parameter is a Python Proxy
    """
    try:
        is_proxy = len(parameter.Java.implements) > 0
    except:
        is_proxy = False
    
    return is_proxy
    
def get_command_part(parameter, python_proxy_pool=None):
    """Converts a Python object into a string representation respecting the Py4J protocol.
    
    For example, the integer `1` is converted to `u'i1'`
    
    :param parameter: the object to convert
    :rtype: the string representing the command part
    """
    command_part = ''
    if parameter == None:
        command_part = NULL_TYPE
    elif isinstance(parameter, bool):
        command_part = BOOLEAN_TYPE + str(parameter)
    elif isinstance(parameter, int) or isinstance(parameter, long):
        command_part = INTEGER_TYPE + str(parameter)
    elif isinstance(parameter, float):
        command_part = DOUBLE_TYPE + str(parameter) 
    elif isinstance(parameter, basestring):
        command_part = STRING_TYPE + escape_new_line(parameter)
    elif is_python_proxy(parameter):
        command_part = PYTHON_PROXY_TYPE + python_proxy_pool.put(parameter)
        for interface in parameter.Java.implements:
            command_part += ';' + interface
    else:
        command_part = REFERENCE_TYPE + parameter._get_object_id()
    
    return command_part + '\n'

def get_return_value(answer, gateway_client, target_id=None, name=None):
    """Converts an answer received from the Java gateway into a Python object.
    
    For example, string representation of integers are converted to Python integer, 
    string representation of objects are converted to JavaObject instances, etc.
    
    :param answer: the string returned by the Java gateway
    :param gateway_client: the gateway client used to communicate with the Java Gateway. Only necessary if the answer is a reference (e.g., object, list, map)
    :param target_id: the name of the object from which the answer comes from (e.g., *object1* in `object1.hello()`). Optional.
    :param name: the name of the member from which the answer comes from (e.g., *hello* in `object1.hello()`). Optional.
    """
    if is_error(answer)[0]:
        if len(answer) > 1:
            raise Py4JError('An error occurred while calling %s%s%s. Trace:\n%s\n' % (target_id, '.', name, unescape_new_line(answer[1:])))
        else:
            raise Py4JError('An error occurred while calling %s%s%s' % (target_id, '.', name))
    else:
        type = answer[1]
        if type == VOID_TYPE:
            return
        else:
            return CONVERSION.get(type)(answer[2:], gateway_client)
    
def is_error(answer):
    if len(answer) == 0 or answer[0] != SUCCESS:
        return (True, None)
    else:
        return (False, None)
    
def get_field(java_object, field_name):
    """Retrieves the field named `field_name` from the `java_object`.
    
    This function is useful when `auto_field=false` in a gateway or Java object.
    
    :param java_object: the instance containing the field
    :param field_name: the name of the field to retrieve
    """
    command = FIELD_COMMAND_NAME + FIELD_GET_SUBCOMMAND_NAME + java_object._target_id + '\n' + field_name + '\n' + END_COMMAND_PART
    answer = java_object._gateway_client.send_command(command)
    if answer == NO_MEMBER_COMMAND or is_error(answer)[0]:
        raise Py4JError('no field %s in object %s' % (field_name, java_object._target_id))
    else:
        return get_return_value(answer, java_object._gateway_client, java_object._target_id, field_name)
        
def set_field(java_object, field_name, value):
    """Sets the field named `field_name` of `java_object` to `value`.
    
    This function is the only way to set a field because the assignment operator in Python cannot
    be overloaded.
    
    :param java_object: the instance containing the field 
    :param field_name: the name of the field to set
    :param value: the value to assign to the field
    """
    command = FIELD_COMMAND_NAME + FIELD_SET_SUBCOMMAND_NAME + java_object._target_id + '\n' + field_name + '\n' \
        + get_command_part(value, java_object._gateway_client.gateway_property.pool) + '\n' + END_COMMAND_PART
        
    answer = java_object._gateway_client.send_command(command)
    if answer == NO_MEMBER_COMMAND or is_error(answer)[0]:
        raise Py4JError('no field %s in object %s' % (field_name, java_object._target_id))
        return get_return_value(answer, java_object._gateway_client, java_object._target_id, field_name)
        
def get_method(java_object, method_name):
    """Retrieves a reference to the method of an object.
    
    This function is useful when `auto_field=true` and an instance field has the same name as a method. 
    The full signature of the method is not required: it is determined when the method is called.
    
    :param java_object: the instance containing the method
    :param method_name: the name of the method to retrieve
    """
    return JavaMember(method_name, java_object, java_object._target_id, java_object._gateway_client)

def garbage_collect_object(gateway_client, target_id):
#    print(target_id + ' deleted')
    ThreadSafeFinalizer.remove_finalizer(str(gateway_client.address) + str(gateway_client.port) + target_id)
    if target_id != ENTRY_POINT_OBJECT_ID and gateway_client.is_connected:
        try:
            gateway_client.send_command(MEMORY_COMMAND_NAME + MEMORY_DEL_SUBCOMMAND_NAME + target_id + '\ne\n')
        except:
            pass
        
def garbage_collect_connection(socket):
    """Closes the socket if auto_delete is True and the socket is opened. 
        
    This is an acceptable practice if you know that your Python VM implements garbage collection 
    and closing sockets immediately is not a concern. Otherwise, it is always better (because it 
    is predictable) to explicitly close the socket by calling `GatewayConnection.close()`.
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
    

class Py4JError(Exception):
    """Exception thrown when a problem occurs with Py4J."""
    def __init__(self, value):
        """
        
        :param value: the error message
        """
        self.value = value
    
    def __repr__(self):
        return self.value
    
    def __str__(self):
        return self.value


class Py4JNetworkError(Exception):
    """Exception thrown when a network error occurs with Py4J."""
    def __init__(self, value):
        """
        
        :param value: the error message
        """
        self.value = value
    
    def __repr__(self):
        return self.value
    
    def __str__(self):
        return self.value

class GatewayClient(object):
    """Responsible for managing connections to the JavaGateway.
    
    This implementation is thread-safe and connections are created on-demand. 
    This means that Py4J-Python can be accessed by multiple threads and 
    messages are sent to and processed concurrently by the Java Gateway.
    
    When creating a custom :class:`JavaGateway`, it is recommended to pass an instance of 
    :class:`GatewayClient` instead of a :class:`GatewayConnection`: both have the same interface, 
    but the client supports multiple threads and connections, which is essential when using 
    callbacks.
    """
    
    def __init__(self, address='localhost', port=25333, auto_close=True, gateway_property=None):
        """
        :param address: the address to which the client will request a connection
        :param port: the port to which the client will request a connection. Default is 25333.
        :param auto_close: if `True`, the connections created by the client close the socket when 
          they are garbage collected.
        :param gateway_property: used to keep gateway preferences without a cycle with the gateway
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
        connection = GatewayConnection(self.address,self.port,self.auto_close,self.gateway_property)
        connection.start()
        return connection
    
    def _give_back_connection(self,connection):
        try:
            self.deque.append(connection)
        except:
            pass
    
    def shutdown_gateway(self):
        """Sends a shutdown command to the gateway. This will close the gateway server: all active 
        connections will be closed. This may be useful if the lifecycle of the Java program must be 
        tied to the Python program."""
        connection = self._get_connection()
        try:
            connection.shutdown_gateway()
            self.close()
            self.is_connected = False
        except Py4JNetworkError:
            self.shutdown_gateway()
            
    def send_command(self, command, retry=True):
        """Sends a command to the JVM. This method is not intended to be called directly by Py4J users: 
        it is usually called by :class:`JavaMember` instances.
        
        :param command: the `string` command to send to the JVM. The command must follow the Py4J protocol.
        :retry: if `True`, the GatewayClient tries to resend a message if it fails.
        :rtype: the `string` answer received from the JVM. The answer follows the Py4J protocol.
        """
        connection = self._get_connection()
        try:
            response = connection.send_command(command)
            self._give_back_connection(connection)
        except Py4JNetworkError:
            if retry:
                response = self.send_command(command)
            else:
                response = ERROR
                
        return response
    
    def close(self):
        """Closes all currently opened connections.
        
        This operation is not thread safe and is only a best effort strategy to close active connections. 
        All connections are guaranteed to be closed only if no other thread is accessing the client and no call is pending.
        """
        size = len(self.deque)
        for _ in range(0,size):
            try:
                connection = deque.pop()
                connection.close()
            except:
                pass
        

class GatewayConnection(object):
    """Default gateway connection (socket based) responsible for communicating with the Java Virtual Machine."""
    
    def __init__(self, address='localhost', port=25333, auto_close=True, gateway_property=None):
        """
        :param address: the address to which the connection will be established
        :param port: the port to which the connection will be established. Default is 25333.
        :param auto_close: if `True`, the connection closes the socket when it is garbage 
          collected.
        :param gateway_property: contains gateway preferences to avoid a cycle with gateway
        """
        self.address = address
        self.port = port
        self.socket = socket.socket(AF_INET, SOCK_STREAM)
        self.is_connected = False
        self.auto_close = auto_close
        self.gateway_property = gateway_property
        self.wr = weakref.ref(self, lambda wr, socket=self.socket: garbage_collect_connection(socket))
        
    def start(self):
        """Starts the connection by connecting to the `address` and the `port`"""
        self.socket.connect((self.address, self.port))
        self.is_connected = True
        self.stream = self.socket.makefile('r', 0)
    
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
        """Sends a shutdown command to the gateway. This will close the gateway server: all active 
        connections will be closed. This may be useful if the lifecycle of the Java program must be 
        tied to the Python program."""
        if (not self.is_connected):
            raise Py4JError('Connection must be connected to send shut down command.')
        
        try:
            self.stream.close()
            self.socket.sendall(SHUTDOWN_GATEWAY_COMMAND_NAME.encode('utf-8'))
            self.socket.close()
            self.is_connected = False
        except Exception:
            # Do nothing! Exceptions might occur anyway.
            pass
            
    def send_command(self, command):
        """Sends a command to the JVM. This method is not intended to be called directly by Py4J users: it is usually called by JavaMember instances.
        
        :param command: the `string` command to send to the JVM. The command must follow the Py4J protocol.
        :rtype: the `string` answer received from the JVM. The answer follows the Py4J protocol.
        """
        logger.debug("Command to send: %s" % (command))
        try:
            self.socket.sendall(command.encode('utf-8'))
            answer = self.stream.readline().decode('utf-8')[:-1]
            logger.debug("Answer received: %s" % (answer))
            # Happens when a the other end is dead. There might be an empty answer before the socket raises an error.
            if answer.strip() == '':
                self.close()
                raise Py4JError()
            return answer
        except:
            logger.exception('Error while sending or receiving.')
            raise Py4JNetworkError('Error while sending or receiving')

class JavaMember(object):
    """Represents a member (i.e., method) of a :class:`JavaObject`. For now, only methods are supported. Fields
    are retrieved directly and are not contained in a JavaMember.
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
            if not isinstance(arg, JavaObject) and not isinstance(arg, basestring):
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
            
        args_command = ''.join([get_command_part(arg, self.pool) for arg in new_args])
        command = CALL_COMMAND_NAME + self.command_header + args_command + END_COMMAND_PART
        answer = self.gateway_client.send_command(command)
        return_value = get_return_value(answer, self.gateway_client, self.target_id, self.name)
        
        for temp_arg in temp_args:
            temp_arg._detach()
        return return_value



class JavaObject(object):
    """Represents a Java object from which you can call methods or access fields."""
    
    def __init__(self, target_id, gateway_client):
        """
        :param target_id: the identifier of the object on the JVM side. Given by the JVM.
        :param gateway_client: the gateway client used to communicate with the JVM.
        """
#        print(target_id + ' created.')
        self._target_id = target_id
        self._gateway_client = gateway_client
        self._auto_field = gateway_client.gateway_property.auto_field
        self._methods = {}
        ThreadSafeFinalizer.add_finalizer( \
            str(self._gateway_client.address) + str(self._gateway_client.port) + self._target_id, \
            weakref.ref(self, lambda wr, cc=self._gateway_client, id=self._target_id: garbage_collect_object(cc, id)))
    
    def _detach(self):
        garbage_collect_object(self._gateway_client, self._target_id)
        
    def _get_object_id(self):
        return self._target_id
        
    def __getattr__(self, name):
        if name not in self._methods:
            if (self._auto_field):
                (is_field, return_value) = self._get_field(name)
                if (is_field):
                    return return_value
            # Theoretically, not thread safe, but the worst case scenario = cache miss or double overwrite of the same method...
            self._methods[name] = JavaMember(name, self, self._target_id, self._gateway_client)
        
        # The name is a method
        return self._methods[name]
    
    def _get_field(self, name):
        command = FIELD_COMMAND_NAME + FIELD_GET_SUBCOMMAND_NAME + self._target_id + '\n' + name + '\n' + END_COMMAND_PART
        answer = self._gateway_client.send_command(command)
        if answer == NO_MEMBER_COMMAND or is_error(answer)[0]:
            return (False, None)
        else:
            return_value = get_return_value(answer, self._gateway_client, self._target_id, name)
            return (True, return_value)
    
    def __eq__(self, other):
        if other == None:
            return False
        elif (hasattr(other, '_get_object_id')):
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
    """A `JavaClass` represents a Java Class from which static members can be retrieved. `JavaClass` 
    instances are also needed to initialize an array.
    
    Usually, `JavaClass` are not initialized using their constructor, but they are created while
    accessing the `jvm` property of a gateway, e.g., `gateway.jvm.java.lang.String`.
    """
    def __init__(self, fqn, gateway_client):
        self._fqn = fqn
        self._gateway_client = gateway_client
        self._command_header = fqn + '\n'
        
    def __getattr__(self, name):
        answer = self._gateway_client.send_command(REFLECTION_COMMAND_NAME + REFL_GET_MEMBER_SUB_COMMAND_NAME + self._fqn + '\n' + name + '\n' + END_COMMAND_PART)
        if len(answer) > 1 and answer[0] == SUCCESS:
            if answer[1] == METHOD_TYPE:
                return JavaMember(name, None, STATIC_PREFIX + self._fqn, self._gateway_client)
            elif answer[1].startswith(CLASS_TYPE):
                return JavaClass(answer[CLASS_FQN_START:], self._gateway_client)
            else:
                return get_return_value(answer, self._gateway_client, self._fqn, name)
        else:
            raise Py4JError('%s does not exist in the JVM' % (self._fqn + name))
        
    def __call__(self, *args):
        args_command = ''.join([get_command_part(arg) for arg in args])
        command = CONSTRUCTOR_COMMAND_NAME + self._command_header + args_command + END_COMMAND_PART
        answer = self._gateway_client.send_command(command)
        return_value = get_return_value(answer, self._gateway_client, None, self._fqn)
        return return_value

class JavaPackage():
    """A `JavaPackage` represents part of a Java package from which Java classes can be accessed.
    
    Usually, `JavaPackage` are not initialized using their constructor, but they are created while
    accessing the `jvm` property of a gateway, e.g., `gateway.jvm.java.lang`.
    """
    def __init__(self, fqn, gateway_client, jvm_id=DEFAULT_JVM_ID):
        self._fqn = fqn
        self._gateway_client = gateway_client
        self._jvm_id = jvm_id
        
    def __getattr__(self, name):
        new_fqn = self._fqn + '.' + name
        answer = self._gateway_client.send_command(REFLECTION_COMMAND_NAME + REFL_GET_UNKNOWN_SUB_COMMAND_NAME + new_fqn + '\n' + self._jvm_id + '\n' + END_COMMAND_PART)
        if answer == SUCCESS_PACKAGE:
            return JavaPackage(new_fqn, self._gateway_client, self._jvm_id)
        elif answer.startswith(SUCCESS_CLASS):
            return JavaClass(answer[CLASS_FQN_START:], self._gateway_client)
        else:
            raise Py4JError('%s does not exist in the JVM' % new_fqn)

class JVMView(object):
    """A `JVMView` allows access to the Java Virtual Machine of a `JavaGateway`. This can be used to reference static members (fields and methods) and to call constructors."""
    
    def __init__(self, gateway_client, jvm_name, id):
        self._gateway_client = gateway_client
        self._jvm_name = jvm_name
        self._id = id
        
    def __getattr__(self, name):
        answer = self._gateway_client.send_command(REFLECTION_COMMAND_NAME + REFL_GET_UNKNOWN_SUB_COMMAND_NAME + name + '\n' + self._id + '\n' + END_COMMAND_PART)
        if answer == SUCCESS_PACKAGE:
            return JavaPackage(name, self._gateway_client, jvm_id = self._id)
        elif answer.startswith(SUCCESS_CLASS):
            return JavaClass(answer[CLASS_FQN_START:], self._gateway_client)
        else:
            raise Py4JError('%s does not exist in the JVM' % name)
    
class GatewayProperty(object):
    def __init__(self, auto_field, pool):
        self.auto_field = auto_field
        self.pool = pool
    
class JavaGateway(object):
    """A `JavaGateway` is the main interaction point between a Python VM and a JVM. 
    
    * A `JavaGateway` instance is connected to a `Gateway` instance on the Java side.
    
    * The `entry_point` field of a `JavaGateway` instance is connected to the `Gateway.entryPoint` instance on the Java side.
    
    * The `jvm` field of `JavaGateway` enables user to access classes, static members (fields and methods) and call constructors.
    
    Methods that are not defined by `JavaGateway` are always redirected to `entry_point`. For example, ``gateway.doThat()`` is equivalent to ``gateway.entry_point.doThat()``.
    This is a trade-off between convenience and potential confusion."""
    
    
    def __init__(self, gateway_client=None, auto_field=False, python_proxy_port=DEFAULT_PYTHON_PROXY_PORT, start_callback_server=False, auto_convert=False):
        """
        :param gateway_client: gateway client used to connect to the JVM. If `None`, a gateway client based on a socket with the default parameters is created.
        :param auto_field: if `False`, each object accessed through this gateway won't try to lookup fields (they will be accessible only by calling get_field). If `True`, fields will be automatically looked up, possibly hiding methods of the same name and making method calls less efficient.
        :param python_proxy_port: port used to receive callback from the JVM.
        :param start_callback_server: if `True`, the callback server is started.
        :param auto_convert: if `True`, try to automatically convert Python objects like sequences and maps to Java Objects. 
                             Default value is `False` to improve performance and because it is still possible to explicitly perform this conversion.
        """
        self.gateway_property = GatewayProperty(auto_field, PythonProxyPool())
        self._python_proxy_port = python_proxy_port
        
        if gateway_client == None:
            gateway_client = GatewayClient()
            
        if auto_convert:
            gateway_client.converters = [SetConverter(), MapConverter(), ListConverter()]
        else:
            gateway_client.converters = None
        
        gateway_client.gateway_property = self.gateway_property
        
        self._gateway_client = gateway_client
            
        self.entry_point = JavaObject(ENTRY_POINT_OBJECT_ID, gateway_client)
        self.jvm = JVMView(gateway_client, jvm_name=DEFAULT_JVM_NAME, id=DEFAULT_JVM_ID)
        if start_callback_server:
            self._callback_server = CallbackServer(self.gateway_property.pool,self._gateway_client, python_proxy_port)
            self._callback_server.start()
            
    def __getattr__(self, name):
        return self.entry_point.__getattr__(name)
            
    def new_array(self, java_class, *dimensions):
        """Creates a Java array of type `java_class` of `dimensions`
        
        :param java_class: The :class:`JavaClass` instance representing the type of the array.
        :param dimensions: A list of dimensions of the array. For example `[1,2]` would produce an `array[1][2]`.
        """
        if len(dimensions) == 0:
            raise Py4JError('new arrays must have at least one dimension')
        command = ARRAY_COMMAND_NAME + ARRAY_CREATE_SUB_COMMAND_NAME + get_command_part(java_class._fqn)
        for dimension in dimensions:
            command += get_command_part(dimension)
        command += END_COMMAND_PART
        answer = self._gateway_client.send_command(command)
        return get_return_value(answer, self._gateway_client)
        
    def shutdown(self):
        """Shuts down the :class:`GatewayClient` and the :class:`CallbackServer <py4j.java_callback.CallbackServer>`.
        """
        try:
            self._gateway_client.shutdown_gateway()
        except:
            pass
        self._shutdown_callback_server()
        
    def _shutdown_callback_server(self):
        """Shuts down the :class:`CallbackServer <py4j.java_callback.CallbackServer>`.
        """
        try:
            self._callback_server.shutdown()
        except:
            pass
        
    def restart_callback_server(self):
        """Shuts down the callback server (if started) and restarts a new one.
        """
        self._shutdown_callback_server()
        self._callback_server = CallbackServer(self.gateway_property.pool,self._gateway_client, self._python_proxy_port)
        self._callback_server.start()
        
    def close(self, keep_callback_server=False):
        """Closes all gateway connections. A connection will be reopened if necessary 
        (e.g., if a :class:`JavaMethod` is called).
        
        :param keep_callback_server: if `True`, the callback server is not shut down.
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
        :param java_object: The JavaObject instance to dereference (free) on the Java side.
        """
        java_object._detach()
    
    def help(self, var, pattern=None, short_name=True, display=True):
        """Displays a help page about a class or an object.
        
        :param var: JavaObject or JavaClass for which a help page will be generated.
        :param pattern: Star-pattern used to filter the members. For example 'get*Foo' may return getMyFoo, getFoo, getFooBar, but not bargetFoo.
        :param short_name: If True, only the simple name of the parameter types and return types will be displayed. If False, the fully qualified name of the types will be displayed.
        :param display: If True, the help page is displayed in an interactive page similar to the `help` command in Python. If False, the page is returned as a string.
        """
        if hasattr(var, '_get_object_id'):
            answer = self._gateway_client.send_command(HELP_COMMAND_NAME + HELP_OBJECT_SUBCOMMAND_NAME + var._get_object_id() + '\n' + get_command_part(pattern) + get_command_part(short_name) + 'e\n')
        elif hasattr(var, '_fqn'):
            answer = self._gateway_client.send_command(HELP_COMMAND_NAME + HELP_CLASS_SUBCOMMAND_NAME + var._fqn + '\n' + get_command_part(pattern) + get_command_part(short_name) + 'e\n')
        else:
            raise Py4JError('var is neither a Java Object nor a Java Class')
        help_page = get_return_value(answer, self._gateway_client, None, None)
        if (display):
            ttypager(help_page)
        else:
            return help_page
            
        
# For circular dependencies
# Purists should close their eyes
from py4j.finalizer import ThreadSafeFinalizer
from py4j.java_callback import CallbackServer, PythonProxyPool
from py4j.java_collections import JavaList, JavaMap, JavaArray, JavaSet, JavaIterator, SetConverter, ListConverter, MapConverter