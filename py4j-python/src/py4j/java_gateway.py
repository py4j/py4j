# -*- coding: UTF-8 -*-
"""Module to interact with objects in a Java Virtual Machine from a Pyton Virtual Machine.

Variables that might clash with the JVM start with an underscore (Java Naming Convention do not 
recommend to start with an underscore so clashes become unlikely).

Created on Dec 3, 2009

@author: Barthelemy Dagenais
"""

from collections import deque
from py4j.finalizer import ThreadSafeFinalizer
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
PYTHON_PROXY_TYPE = 'f'

# Protocol
END = 'e'
ERROR = 'x'
SUCCESS = 'y'


# Shortcuts
SUCCESS_PACKAGE = SUCCESS + PACKAGE_TYPE
SUCCESS_CLASS = SUCCESS + CLASS_TYPE
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

CONVERSION = {NULL_TYPE: (lambda x, y: None),
              REFERENCE_TYPE: (lambda target_id, comm_channel: JavaObject(target_id, comm_channel)),
              MAP_TYPE: (lambda target_id, comm_channel: JavaMap(target_id, comm_channel)),
              LIST_TYPE: (lambda target_id, comm_channel: JavaList(target_id, comm_channel)),
              ARRAY_TYPE: (lambda target_id, comm_channel: JavaArray(target_id, comm_channel)),
              SET_TYPE: (lambda target_id, comm_channel: JavaSet(target_id, comm_channel)),
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
    temp = original.replace('\\', '\\\\')
    final = temp.replace('\n', '\\n')
    return final

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
            else:
                original += c
            escaping = False
            
    return original

    
def is_python_proxy(parameter):
    """Determines whether parameter is a Python Proxy, i.e., it has a Java internal class with an
    interfaces member.
    :param parameter: the object to check.
    :rtype: True if the parameter is a Python Proxy
    """
    try:
        is_proxy = len(parameter.Java.interfaces) > 0
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
        for interface in parameter.Java.interfaces:
            command_part += ';' + interface
    else:
        command_part = REFERENCE_TYPE + parameter._get_object_id()
    
    return command_part + '\n'

def get_return_value(answer, comm_channel, target_id=None, name=None):
    """Converts an answer received from the Java gateway into a Python object.
    
    For example, string representation of integers are converted to Python integer, 
    string representation of objects are converted to JavaObject instances, etc.
    
    :param answer: the string returned by the Java gateway
    :param comm_channel: the communication channel used to communicate with the Java Gateway. Only necessary if the answer is a reference (e.g., object, list, map)
    :param target_id: the name of the object from which the answer comes from (e.g., *object1* in `object1.hello()`). Optional.
    :param name: the name of the member from which the answer comes from (e.g., *hello* in `object1.hello()`). Optional.
    """
    if is_error(answer)[0]:
        raise Py4JError('An error occurred while calling %s%s%s' % (target_id, '.', name))
    else:
        type = answer[1]
        if type == VOID_TYPE:
            return
        else:
            return CONVERSION.get(type)(answer[2:], comm_channel)
    
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
    answer = java_object._comm_channel.send_command(command)
    if answer == NO_MEMBER_COMMAND or is_error(answer)[0]:
        raise Py4JError('no field %s in object %s' % (field_name, java_object._target_id))
    else:
        return get_return_value(answer, java_object._comm_channel, java_object._target_id, field_name)
        
def get_method(java_object, method_name):
    """Retrieves a reference to the method of an object.
    
    This function is useful when `auto_field=true` and an instance field has the same name as a method. 
    The full signature of the method is not required: it is determined when the method is called.
    
    :param java_object: the instance containing the method
    :param method_name: the name of the method to retrieve
    """
    return JavaMember(method_name, java_object, java_object._target_id, java_object._comm_channel)

def garbage_collect_object(comm_channel, target_id):
#    print(target_id + ' deleted')
    ThreadSafeFinalizer.remove_finalizer(str(comm_channel.address) + str(comm_channel.port) + target_id)
    if target_id != ENTRY_POINT_OBJECT_ID and comm_channel.is_connected:
        try:
            comm_channel.send_command(MEMORY_COMMAND_NAME + MEMORY_DEL_SUBCOMMAND_NAME + target_id + '\ne\n')
        except:
            pass
        
def garbage_collect_channel(socket):
    """Closes the socket if auto_delete is True and the socket is opened. 
        
    This is an acceptable practice if you know that your Python VM implements garbage collection 
    and closing sockets immediately is not a concern. Otherwise, it is always better (because it 
    is predictable) to explicitly close the socket by calling `CommChannel.close()`.
    """
#    print('delete channel')
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
    
    def __str__(self):
        return repr(self.value)


class Py4JNetworkError(Exception):
    """Exception thrown when a network error occurs with Py4J."""
    def __init__(self, value):
        """
        
        :param value: the error message
        """
        self.value = value
    
    def __str__(self):
        return repr(self.value)

class CommChannelFactory(object):
    """Responsible for managing connections to the JavaGateway.
    
    This implementation is thread-safe and connections are created on-demand. 
    This means that Py4J-Python can be accessed by multiple threads and 
    messages are sent to and processed concurrently by the Java Gateway.
    
    When creating a custom :class:`JavaGateway`, it is recommended to pass an instance of 
    :class:`CommChannelFactory` instead of a :class:`CommChannel`: both have the same interface, 
    but the factory supports multiple threads and connections, which is essential when using 
    callbacks.
    """
    
    def __init__(self, address='localhost', port=25333, auto_close=True, thread_safe=False, gateway_property=None):
        """
        :param address: the address to which the comm channel will connect
        :param port: the port to which the comm channel will connect. Default is 25333.
        :param auto_close: if `True`, the communication channel closes the socket when it is garbage 
          collected.
        :param thread_safe: if `True`, the communication channel must acquire a lock before using the socket.
        """
        self.address = address
        self.port = port
        self.is_connected = True
        self.auto_close = auto_close
        self.gateway_property = gateway_property
        self.deque = deque()
        
    def _get_comm_channel(self):
        if not self.is_connected:
            raise Py4JNetworkError('Gateway is not connected.')
        try:
            comm_channel = self.deque.pop()
        except:
            comm_channel = self._create_comm_channel() 
        return comm_channel
    
    def _create_comm_channel(self):
#        print('Creating comm channel')
        comm_channel = CommChannel(self.address,self.port,self.auto_close,self.gateway_property)
        comm_channel.start()
        return comm_channel
    
    def _give_back_channel(self,comm_channel):
        try:
            self.deque.append(comm_channel)
        except:
            pass
    
    def shutdown_gateway(self):
        """Sends a shutdown command to the gateway. This will close the gateway server: all active 
        connections will be closed. This may be useful if the lifecycle of the Java program must be 
        tied to the Python program."""
        comm_channel = self._get_comm_channel()
        try:
            comm_channel.shutdown_gateway()
            self.close()
            self.is_connected = False
        except Py4JNetworkError:
            self.shutdown_gateway()
            
    def send_command(self, command):
        """Sends a command to the JVM. This method is not intended to be called directly by Py4J users: 
        it is usually called by :class:`JavaMember` instances.
        
        :param command: the `string` command to send to the JVM. The command must follow the Py4J protocol.
        :rtype: the `string` answer received from the JVM. The answer follows the Py4J protocol.
        """
        comm_channel = self._get_comm_channel()
        try:
            response = comm_channel.send_command(command)
            self._give_back_channel(comm_channel)
        except Py4JNetworkError:
            response = self.send_command(command)
            
        return response
    
    def close(self):
        """Closes all currently opened communication channels.
        
        This operation is not thread safe and is only a best effort strategy to close active channels. 
        All channels are guaranteed to be closed only if no other thread is accessing the factory and no call is pending.
        """
        size = len(self.deque)
        for _ in range(0,size):
            try:
                channel = deque.pop()
                channel.close()
            except:
                pass
        

class CommChannel(object):
    """Default communication channel (socket based) responsible for communicating with the Java Virtual Machine."""
    
    def __init__(self, address='localhost', port=25333, auto_close=True, gateway_property=None):
        """
        :param address: the address to which the comm channel will connect
        :param port: the port to which the comm channel will connect. Default is 25333.
        :param auto_close: if `True`, the communication channel closes the socket when it is garbage 
          collected.
        :param thread_safe: if `True`, the communication channel must acquire a lock before using the socket.
        """
        self.address = address
        self.port = port
        self.socket = socket.socket(AF_INET, SOCK_STREAM)
        self.is_connected = False
        self.auto_close = auto_close
        self.gateway_property = gateway_property
        self.wr = weakref.ref(self, lambda wr, socket=self.socket: garbage_collect_channel(socket))
        
    def start(self):
        """Starts the communication channel by connecting to the `address` and the `port`"""
        self.socket.connect((self.address, self.port))
        self.is_connected = True
        self.stream = self.socket.makefile('r', 0)
    
    def close(self, throw_exception=False):
        """Closes the communication channel by closing the socket."""
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
            raise Py4JError('Communication channel must be connected to send shut down command.')
        
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
        self.socket.sendall(command.encode('utf-8'))
        answer = self.stream.readline().decode('utf-8')[:-1]
        logger.debug("Answer received: %s" % (answer))
        return answer

class JavaMember(object):
    """Represents a member (i.e., method) of a :class:`JavaObject`. For now, only methods are supported. Fields
    are retrieved directly and are not contained in a JavaMember.
    """
    
    def __init__(self, name, container, target_id, comm_channel):
        self.name = name
        self.container = container
        self.target_id = target_id
        self.comm_channel = comm_channel
        self.command_header = self.target_id + '\n' + self.name + '\n'
        self.pool = self.comm_channel.gateway_property.pool
        
    def __call__(self, *args):
        args_command = ''.join([get_command_part(arg, self.pool) for arg in args])
        command = CALL_COMMAND_NAME + self.command_header + args_command + END_COMMAND_PART
        answer = self.comm_channel.send_command(command)
        return_value = get_return_value(answer, self.comm_channel, self.target_id, self.name)
        return return_value



class JavaObject(object):
    """Represents a Java object from which you can call methods or access fields."""
    
    def __init__(self, target_id, comm_channel):
        """
        :param target_id: the identifier of the object on the JVM side. Given by the JVM.
        :param comm_channel: the communication channel used to communicate with the JVM.
        """
#        print(target_id + ' created.')
        self._target_id = target_id
        self._comm_channel = comm_channel
        self._auto_field = comm_channel.gateway_property.auto_field
        self._methods = {}
        ThreadSafeFinalizer.add_finalizer( \
            str(self._comm_channel.address) + str(self._comm_channel.port) + self._target_id, \
            weakref.ref(self, lambda wr, cc=self._comm_channel, id=self._target_id: garbage_collect_object(cc, id)))
    
    def _detach(self):
        garbage_collect_object(self._comm_channel, self._target_id)
        
    def _get_object_id(self):
        return self._target_id
        
    def __getattr__(self, name):
        if name not in self._methods:
            if (self._auto_field):
                (is_field, return_value) = self._get_field(name)
                if (is_field):
                    return return_value
            # Theoretically, not thread safe, but the worst case scenario = cache miss or double overwrite of the same method...
            self._methods[name] = JavaMember(name, self, self._target_id, self._comm_channel)
        
        # The name is a method
        return self._methods[name]
    
    def _get_field(self, name):
        command = FIELD_COMMAND_NAME + FIELD_GET_SUBCOMMAND_NAME + self._target_id + '\n' + name + '\n' + END_COMMAND_PART
        answer = self._comm_channel.send_command(command)
        if answer == NO_MEMBER_COMMAND or is_error(answer)[0]:
            return (False, None)
        else:
            return_value = get_return_value(answer, self._comm_channel, self._target_id, name)
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
    def __init__(self, fqn, comm_channel):
        self._fqn = fqn
        self._comm_channel = comm_channel
        self._command_header = fqn + '\n'
        
    def __getattr__(self, name):
        answer = self._comm_channel.send_command(REFLECTION_COMMAND_NAME + REFL_GET_MEMBER_SUB_COMMAND_NAME + self._fqn + '\n' + name + '\n' + END_COMMAND_PART)
        if len(answer) > 1 and answer[0] == SUCCESS:
            if answer[1] == METHOD_TYPE:
                return JavaMember(name, None, STATIC_PREFIX + self._fqn, self._comm_channel)
            elif answer[1] == CLASS_TYPE:
                return JavaClass(self._fqn + name, self._comm_channel)
            else:
                return get_return_value(answer, self._comm_channel, self._fqn, name)
        else:
            raise Py4JError('%s does not exist in the JVM' % (self._fqn + name))
        
    def __call__(self, *args):
        args_command = ''.join([get_command_part(arg) for arg in args])
        command = CONSTRUCTOR_COMMAND_NAME + self._command_header + args_command + END_COMMAND_PART
        answer = self._comm_channel.send_command(command)
        return_value = get_return_value(answer, self._comm_channel, None, self._fqn)
        return return_value

class JavaPackage():
    """A `JavaPackage` represents part of a Java package from which Java classes can be accessed.
    
    Usually, `JavaPackage` are not initialized using their constructor, but they are created while
    accessing the `jvm` property of a gateway, e.g., `gateway.jvm.java.lang`.
    """
    def __init__(self, fqn, comm_channel):
        self._fqn = fqn
        self._comm_channel = comm_channel
        
    def __getattr__(self, name):
        new_fqn = self._fqn + '.' + name
        answer = self._comm_channel.send_command(REFLECTION_COMMAND_NAME + REFL_GET_UNKNOWN_SUB_COMMAND_NAME + new_fqn + '\n' + END_COMMAND_PART)
        if answer == SUCCESS_PACKAGE:
            return JavaPackage(new_fqn, self._comm_channel)
        elif answer == SUCCESS_CLASS:
            return JavaClass(new_fqn, self._comm_channel)
        else:
            raise Py4JError('%s does not exist in the JVM' % new_fqn)

class JVM(object):
    """A `JVM` allows access to the Java Virtual Machine of a `JavaGateway`. This can be used to reference static members (fields and methods) and to call constructors."""
    
    def __init__(self, comm_channel):
        self._comm_channel = comm_channel
        
    def __getattr__(self, name):
        answer = self._comm_channel.send_command(REFLECTION_COMMAND_NAME + REFL_GET_UNKNOWN_SUB_COMMAND_NAME + name + '\n' + END_COMMAND_PART)
        if answer == SUCCESS_PACKAGE:
            return JavaPackage(name, self._comm_channel)
        elif answer == SUCCESS_CLASS:
            return JavaClass(name, self._comm_channel)
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
    
    
    def __init__(self, comm_channel=None, auto_field=False, python_proxy_port=DEFAULT_PYTHON_PROXY_PORT):
        """
        :param comm_channel: communication channel used to connect to the JVM. If `None`, a communication channel factory based on a socket with the default parameters is created.
        :param auto_field: if `False`, each object accessed through this gateway won't try to lookup fields (they will be accessible only by calling get_field). If `True`, fields will be automatically looked up, possibly hiding methods of the same name and making method calls less efficient.
        :param python_proxy_port: port used to receive callback from the JVM.
        """
        self.gateway_property = GatewayProperty(auto_field, PythonProxyPool())
        
        if comm_channel == None:
            comm_channel = CommChannelFactory()
        
        comm_channel.gateway_property = self.gateway_property
        
        self._comm_channel = comm_channel
            
        #JavaObject.__init__(self, ENTRY_POINT_OBJECT_ID, comm_channel)
        self.entry_point = JavaObject(ENTRY_POINT_OBJECT_ID, comm_channel)
        self.jvm = JVM(comm_channel)
        self._callback_server = CallbackServer(self.gateway_property.pool,self._comm_channel, python_proxy_port)
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
        answer = self._comm_channel.send_command(command)
        return get_return_value(answer, self._comm_channel)
        
    def shutdown(self):
        """Shuts down the :class:`CommChannelFactory` and the :class:`CallbackServer <py4j.java_callback.CallbackServer>`.
        """
        try:
            self._comm_channel.shutdown_gateway()
        except:
            pass
        try:
            self._callback_server.shutdown()
        except:
            pass
        
    def close(self):
        """Closes all communication channels. A communication channel will be reopened if necessary 
        (e.g., if a :class:`JavaMethod` is called).
        """
        self._comm_channel.close()
        
    def detach(self, java_object):
        """Makes the Java Gateway dereference this object. 
        
        The equivalent of this method is called when a JavaObject instance 
        is garbage collected on the Python side. This method, or gc.collect()
        should still be invoked when memory is limited or when too many objects
        are created on the Java side.
        :param java_object: The JavaObject instance to dereference (free) on the Java side.
        """
        java_object._detach()
    
    def help(self, var, short_name=True, display=True):
        """Displays a help page about a class or an object.
        
        :param var: JavaObject or JavaClass for which a help page will be generated.
        :param short_name: If True, only the simple name of the parameter types and return types will be displayed. If False, the fully qualified name of the types will be displayed.
        :param display: If True, the help page is displayed in an interactive page similar to the `help` command in Python. If False, the page is returned as a string.
        """
        if hasattr(var, '_get_object_id'):
            answer = self._comm_channel.send_command(HELP_COMMAND_NAME + HELP_OBJECT_SUBCOMMAND_NAME + var._get_object_id() + '\n' + get_command_part(short_name) + 'e\n')
        elif hasattr(var, '_fqn'):
            answer = self._comm_channel.send_command(HELP_COMMAND_NAME + HELP_CLASS_SUBCOMMAND_NAME + var._fqn + '\n' + get_command_part(short_name) + 'e\n')
        else:
            raise Py4JError('var is neither a Java Object nor a Java Class')
        help_page = get_return_value(answer, self._comm_channel, None, None)
        if (display):
            ttypager(help_page)
        else:
            return help_page
            
        
# For circular dependencies
# Purists should close their eyes
from py4j.java_collections import JavaList, JavaMap, JavaArray, JavaSet
from py4j.java_callback import CallbackServer, PythonProxyPool