# -*- coding: UTF-8 -*-
"""Module to interact with objects in a Java Virtual Machine from a Pyton Virtual Machine.

Variables that might clash with the JVM start with an underscore (Java Naming Convention do not 
recommend to start with an underscore so clashes become unlikely).

Created on Dec 3, 2009

@author: Barthelemy Dagenais
"""

from socket import AF_INET, SOCK_STREAM
from pydoc import ttypager
import logging
import socket


class NullHandler(logging.Handler):
    def emit(self, record):
        pass

null_handler = NullHandler()
logging.getLogger("py4j").addHandler(null_handler)
logger = logging.getLogger("py4j.java_gateway")

BUFFER_SIZE = 4096
DEFAULT_PORT = 25333

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
LIST_TYPE = 'l'
MAP_TYPE = 'a'
NULL_TYPE = 'n'
PACKAGE_TYPE = 'p';
CLASS_TYPE = 'c';
METHOD_TYPE = 'm';
NO_MEMBER = 'o';
VOID_TYPE = 'v'

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
REFLECTION_COMMAND_NAME = "r\n";
MEMORY_COMMAND_NAME = "m\n";
HELP_COMMAND_NAME = 'h\n'

# Reflection subcommands
REFL_GET_UNKNOWN_SUB_COMMAND_NAME = 'u\n';
REFL_GET_MEMBER_SUB_COMMAND_NAME = 'm\n';
    

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

    
def get_command_part(parameter):
    """Converts a Python object into a string representation respecting the Py4J protocol.
    
    For example, the integer `1` is converted to `u'i1'`
    
    :param parameter: the object to convert
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
    else:
        command_part = REFERENCE_TYPE + parameter._get_object_id()
    
    return command_part + '\n'

def get_return_value(answer, comm_channel, target_id = None, name = None):
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
    elif answer[1] == NULL_TYPE:
        return None
    elif answer[1] == VOID_TYPE:
        return
    elif answer[1] == REFERENCE_TYPE:
        return JavaObject(answer[2:], comm_channel)
    elif answer[1] == LIST_TYPE:
        return JavaList(answer[2:], comm_channel)
    elif answer[1] == MAP_TYPE:
        return JavaMap(answer[2:], comm_channel)
    elif answer[1] == INTEGER_TYPE:
        return int(answer[2:])
    elif answer[1] == BOOLEAN_TYPE:
        return answer[2:].lower() == 'true'
    elif answer[1] == DOUBLE_TYPE:
        return float(answer[2:])
    elif answer[1] == STRING_TYPE:
        return unescape_new_line(answer[2:])
    
def is_error(answer):
    if len(answer)==0 or answer[0] != SUCCESS:
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
    return JavaMember(method_name, java_object._target_id, java_object._comm_channel)

class Py4JError(Exception):
    """Exception thrown when a problem occurs with Py4J."""
    def __init__(self, value):
        """
        
        :param value: the error message
        """
        self.value = value
    
    def __str__(self):
        return repr(self.value)

class CommChannel(object):
    """Default communication channel (socket based) responsible for communicating with the Java Virtual Machine."""
    
    def __init__(self, address='localhost', port=25333, auto_close=True):
        """
        :param address: the address to which the comm channel will connect
        :param port: the port to which the comm channel will connect. Default is 25333.
        :param auto_close: if `True`, the communication channel closes the socket when it is garbage 
          collected (i.e., when `CommChannel.__del__()` is called).
        """
        self.address = address
        self.port = port
        self.socket = socket.socket(AF_INET, SOCK_STREAM)
        self.is_connected = False
        self.auto_close = auto_close
        self.queue = []
        
    def start(self):
        """Starts the communication channel by connecting to the `address` and the `port`"""
        self.socket.connect((self.address, self.port))
        self.is_connected = True
        self.stream = self.socket.makefile('r',0)
    
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

    def __del__(self):
        """Closes the socket if auto_delete is True and the socket is opened. 
        
        This is an acceptable practice if you know that your Python VM implements garbage collection 
        and closing sockets immediately is not a concern. Otherwise, it is always better (because it 
        is predictable) to explicitly close the socket by calling `CommChannel.close()`.
        """
        if self.auto_close and self.socket != None and self.is_connected:
            self.close()
            
    def delay_command(self, command):
        self.queue.append(command)
        
    def send_delay(self):
        if len(self.queue) > 0 and self.is_connected:
            logger.debug('')
            return self.send_command(self.queue.pop(0))
        else:
            return None
        
    def send_command(self, command):
        """Sends a command to the JVM. This method is not intended to be called directly by Py4J users: it is usually called by JavaMember instances.
        
        :param command: the `string` command to send to the JVM. The command must follow the Py4J protocol.
        :rtype: the `string` answer received from the JVM. The answer follows the Py4J protocol.
        """
        
        logger.debug("Command to send: %s" % (command))
        self.socket.sendall(command.encode('utf-8'))
        answer = self.stream.readline().decode('utf-8')[:-1]
        logger.debug("Answer received: %s" % (answer))
        self.send_delay()
        return answer

class JavaMember(object):
    """Represents a member (field, method) of a Java Object. For now, only methods are supported.
    """
    
    def __init__(self, name, target_id, comm_channel):
        self.name = name
        self.target_id = target_id
        self.comm_channel = comm_channel
        self.command_header = self.target_id + '\n' + self.name + '\n'
        
    def __call__(self, *args):
        args_command = ''.join([get_command_part(arg) for arg in args])
        command = CALL_COMMAND_NAME + self.command_header + args_command + END_COMMAND_PART
        answer = self.comm_channel.send_command(command)
        return_value = get_return_value(answer, self.comm_channel, self.target_id, self.name)
        return return_value



class JavaObject(object):
    """Represents a Java object from which you can call methods."""
    
    def __init__(self, target_id, comm_channel):
        """
        :param target_id: the identifier of the object on the JVM side. Given by the JVM.
        :param comm_channel: the communication channel used to communicate with the JVM.
        """
        self._target_id = target_id
        self._methods = {}
        self._comm_channel = comm_channel
        self._auto_field = comm_channel.gateway._auto_field
        
    def _get_object_id(self):
        return self._target_id
        
    def __getattr__(self, name):
        if name not in self._methods:
            if (self._auto_field):
                (is_field, return_value) = self._get_field(name)
                if (is_field):
                    return return_value
            self._methods[name] = JavaMember(name, self._target_id, self._comm_channel)
        
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
        elif (hasattr(other,'_get_object_id')):
            return self.equals(other)
        else:
            return other.__eq__(self)
    
    def __hash__(self):
        return self.hashCode()
    
    def __str__(self):
        return self.toString()
    
    def __repr__(self):
        # For now...
        return self.toString()
    
    def __del__(self):
        if self._comm_channel.is_connected:
            self._comm_channel.delay_command(MEMORY_COMMAND_NAME + MEMORY_DEL_SUBCOMMAND_NAME + self._target_id + '\ne\n')
    


class JavaClass():
    def __init__(self, fqn, comm_channel):
        self._fqn = fqn
        self._comm_channel = comm_channel
        self._command_header = fqn + '\n'
        
    def __getattr__(self, name):
        answer = self._comm_channel.send_command(REFLECTION_COMMAND_NAME + REFL_GET_MEMBER_SUB_COMMAND_NAME + self._fqn + '\n' + name + '\n' + END_COMMAND_PART)
        if len(answer) > 1 and answer[0] == SUCCESS:
            if answer[1] == METHOD_TYPE:
                return JavaMember(name, STATIC_PREFIX + self._fqn, self._comm_channel)
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
    def __init__(self, fqn, comm_channel):
        self._fqn = fqn
        self._comm_channel = comm_channel
        
    def __getattr__(self, name):
        new_fqn = self._fqn + '.' + name
        answer = self._comm_channel.send_command(REFLECTION_COMMAND_NAME + REFL_GET_UNKNOWN_SUB_COMMAND_NAME + new_fqn + '\n' + END_COMMAND_PART)
        if answer == SUCCESS_PACKAGE:
            return JavaPackage(new_fqn,self._comm_channel)
        elif answer == SUCCESS_CLASS:
            return JavaClass(new_fqn, self._comm_channel)
        else:
            raise Py4JError('%s does not exist in the JVM' % new_fqn)

class JVM():
    """A `JVM` allows access to the Java Virtual Machine of a `JavaGateway`. This can be used to reference static members (fields and methods) and to call constructors."""
    
    def __init__(self, comm_channel):
        self._comm_channel = comm_channel
        
    def __getattr__(self, name):
        answer = self._comm_channel.send_command(REFLECTION_COMMAND_NAME + REFL_GET_UNKNOWN_SUB_COMMAND_NAME + name + '\n' + END_COMMAND_PART)
        if answer == SUCCESS_PACKAGE:
            return JavaPackage(name,self._comm_channel)
        elif answer == SUCCESS_CLASS:
            return JavaClass(name, self._comm_channel)
        else:
            raise Py4JError('%s does not exist in the JVM' % name)
    
class JavaGateway(JavaObject):
    """A `JavaGateway` is the main interaction point between a Python VM and a JVM. 
    
    * A `JavaGateway` instance is connected to a `Gateway` instance on the Java side.
    
    * The `entry_point` field of a `JavaGateway` instance is connected to the `Gateway.entryPoint` instance on the Java side.
    
    * The `jvm` field of `JavaGateway` enables user to access classes, static members (fields and methods) and call constructors.
    
    Methods that are not defined by `JavaGateway` are always redirected to `entry_point`. For example, ``gateway.doThat()`` is equivalent to ``gateway.entry_point.doThat()``.
    This is a trade-off between convenience and potential confusion."""
    
    
    def __init__(self, comm_channel=None, auto_start=True, auto_field=False):
        """
        :param comm_channel: communication channel used to connect to the JVM. If `None`, a communication channel based on a socket with the default parameters is created.
        :param auto_start: if `True`, the JavaGateway connects to the JVM as soon as it is created. Otherwise, you need to explicitly call `gateway.comm_channel.start()`.
        :param auto_field: if `False`, each object accessed through this gateway won't try to lookup fields (they will be accessible only by calling get_field). If `True`, fields will be automatically looked up, possibly hiding methods of the same name and making method calls less efficient.
        """
        if comm_channel == None:
            comm_channel = CommChannel()
            
        self._auto_field = auto_field
        comm_channel.gateway = self
            
        JavaObject.__init__(self, ENTRY_POINT_OBJECT_ID, comm_channel)
        self.entry_point = JavaObject(ENTRY_POINT_OBJECT_ID, comm_channel)
        self.jvm = JVM(comm_channel)
        if auto_start:
            self._comm_channel.start()
            
    def start(self):
        self._comm_channel.start()
        
    def close(self):
        self._comm_channel.close()
            
    def shutdown(self):
        self._comm_channel.shutdown_gateway()
        
    def attach(self, java_object):
        answer = self._comm_channel.send_command(MEMORY_COMMAND_NAME + MEMORY_ATTACH_SUBCOMMAND_NAME + java_object._get_object_id() + '\ne\n')
        return get_return_value(answer, self._comm_channel, None, None)
    
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
from py4j.java_collections import JavaList, JavaMap
