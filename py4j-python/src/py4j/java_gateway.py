# -*- coding: UTF-8 -*-
"""Module to interact with objects in a Java Virtual Machine from a Pyton Virtual Machine.

Variables that might clash with the JVM start with an underscore (Java Naming Convention do not 
recommend to start with an underscore so clashes become unlikely).

Created on Dec 3, 2009

@author: Barthelemy Dagenais
"""

import logging
from IN import AF_INET
from IN import SOCK_STREAM
import socket

class NullHandler(logging.Handler):
    def emit(self, record):
        pass

null_handler = NullHandler()
logging.getLogger("py4j").addHandler(null_handler)
logger = logging.getLogger("py4j.java_gateway")

BUFFER_SIZE = 4096
DEFAULT_PORT = 25333

# Entry point
ENTRY_POINT_OBJECT_ID = 't'
STATIC_PREFIX = 'z:'

# Types
INTEGER_TYPE = 'i'
BOOLEAN_TYPE = 'b'
DOUBLE_TYPE = 'd'
STRING_TYPE = 's'
REFERENCE_TYPE = 'r'
LIST_TYPE = 'l'
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



def escape_new_line(original):
    """Replaces new line characters by a backslash followed by a n.
    
    Backslashes are also escaped by another backslash.
    
    :param original: the string to escape
    
    :rtype: an escaped string
    """
    temp = original.replace('\\', '\\\\')
    final = temp.replace('\n', '\\n')
    return final
    
def get_command_part(parameter):
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
    elif answer[1] == INTEGER_TYPE:
        return int(answer[2:])
    elif answer[1] == BOOLEAN_TYPE:
        return answer[2:].lower() == 'true'
    elif answer[1] == DOUBLE_TYPE:
        return float(answer[2:])
    elif answer[1] == STRING_TYPE:
        return answer[2:]
    
def is_error(answer):
    if len(answer)==0 or answer[0] != SUCCESS:
        return (True, None)
    else:
        return (False, None)
    
def get_field(java_object, field_name):
    command = FIELD_COMMAND_NAME + FIELD_GET_SUBCOMMAND_NAME + java_object._target_id + '\n' + field_name + '\n' + END_COMMAND_PART
    answer = java_object._comm_channel.send_command(command)
    if answer == NO_MEMBER_COMMAND or is_error(answer)[0]:
        raise Py4JError('no field %s in object %s' % (field_name, java_object._target_id))
    else:
        return get_return_value(answer, java_object._comm_channel, java_object._target_id, field_name)
        
    

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
    
    def __init__(self, address='localhost', port=25333, auto_close=True, auto_field=True):
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
        self.auto_field = auto_field
        
    def start(self):
        """Starts the communication channel by connecting to the `address` and the `port`"""
        self.socket.connect((self.address, self.port))
        self.is_connected = True
    
    def close(self, throw_exception=False):
        """Closes the communication channel by closing the socket."""
        try:
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
        
    def send_command(self, command):
        """Sends a command to the JVM. This method is not intended to be called directly by Py4J users: it is usually called by JavaMember instances.
        
        :param command: the `string` command to send to the JVM. The command must follow the Py4J protocol.
        :rtype: the `string` answer received from the JVM. The answer follows the Py4J protocol.
        """
        
        logger.debug("Command to send: %s" % (command))
        self.socket.sendall(command.encode('utf-8'))
        answer = self.socket.recv(BUFFER_SIZE).decode('utf-8')
        logger.debug("Answer received: %s" % (answer))
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
        self._auto_field = comm_channel.auto_field
        
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
        else:
            return self.equals(other)
    
    def __hash__(self):
        return self.hashCode()
    
    def __str__(self):
        return self.toString()
    
    def __repr__(self):
        # For now...
        return self.toString()
    
class JavaListIterator(JavaObject):
    """Maps a Python list iterator to a Java list iterator.
    
    The `JavaListIterator` follows the Python iterator protocol and raises a `StopIteration` error when the iterator can no longer iterate."""
    def __init__(self, target_id, comm_channel):
        JavaObject.__init__(self, target_id, comm_channel)
        self._next_name = 'next'
        
    def __iter__(self):
        return self
    
    def next(self):
        """This next method wraps the `next` method in Java iterators. 
        
        The `Iterator.next()` method is called and if an exception occur (e.g., 
        NoSuchElementException), a StopIteration exception is raised."""
        if self._next_name not in self._methods:
            self._methods[self._next_name] = JavaMember(self._next_name, self._target_id, self._comm_channel)
        try:
            return self._methods[self._next_name]()
        except Py4JError:
            raise StopIteration()
    
class JavaList(JavaObject):
    """Maps a Python list to a Java list.
    
    All operations possible on a Python list are implemented. For example, slicing (e.g., list[1:3]) 
    will create a copy of the list on the JVM. Slicing is thus not equivalent to subList(), because 
    a modification to a slice such as the addition of a new element will not affect the original 
    list."""
    
    def __init__(self, target_id, comm_channel):
        JavaObject.__init__(self, target_id, comm_channel)

    def __len__(self):
        return self.size()

    def __iter__(self):
        return JavaListIterator(self.iterator()._get_object_id(), self._comm_channel)
    
    def __compute_index(self, key, adjustLast = False):
        size = self.size()
        if 0 <= key < size:
            return key
        elif key < 0 and abs(key) <= size:
            return size + key
        elif adjustLast:
            return size
        else:
            raise IndexError("list index out of range")
    
    def __compute_item(self, key):
        new_key = self.__compute_index(key)
        return self.get(new_key)
    
    def __set_item(self, key, value):
        new_key = self.__compute_index(key)
        self.set(new_key, value)

    def __set_item_from_slice(self, indices, iterable):
        offset = 0
        last = 0
        value_iter = iter(iterable)
        
        # First replace and delete if from_slice > to_slice
        for i in range(*indices):
            try:
                value = value_iter.next()
                self.__set_item(i, value)
            except StopIteration:
                self.__del_item(i)
                offset -= 1
            last = i + 1
        
        # Then insert if from_slice < to_slice 
        for elem in value_iter:
            self.insert(last,elem)
            last += 1
    
    def __insert_item_from_slice(self, indices, iterable):
        index = indices[0]
        for elem in iterable:
            self.insert(index,elem)
            index += 1
    
    def __repl_item_from_slice(self, range, iterable):
        value_iter = iter(iterable)
        for i in range:
            value = value_iter.next()
            self.__set_item(i, value)
            
    def __append_item_from_slice(self, range, iterable):
        for value in iterable:
            self.append(value)
    
    def __del_item(self, key):
        new_key = self.__compute_index(key)
        self.remove(new_key)

    def __setitem__(self, key, value):
        if isinstance(key, slice):
            self_len = len(self)
            indices = key.indices(self_len)
            if indices[0] >= self_len:
                self.__append_item_from_slice(range, value)
            elif indices[0] == indices[1]:
                self.__insert_item_from_slice(indices, value)
            elif indices[2] == 1:
                self.__set_item_from_slice(indices, value)
            else:
                self_range = range(*indices)
                lenr = len(self_range)
                lenv = len(value)
                if lenr != lenv:
                    raise ValueError("attempt to assign sequence of size %d to extended slice of size %d" % (lenv,lenr))
                else:
                    return self.__repl_item_from_slice(self_range,value)
            
        elif isinstance(key, int):
            return self.__set_item(key, value)
        else:
            raise TypeError("list indices must be integers, not %s" % key.__class__.__name__)
    
    def __get_slice(self, indices):
        command = LIST_COMMAND_NAME + LIST_SLICE_SUBCOMMAND_NAME + self._get_object_id() + '\n'
        for index in indices:
            command += get_command_part(index)
        command += END_COMMAND_PART
        answer = self._comm_channel.send_command(command)
        return get_return_value(answer, self._comm_channel)
        
        
    def __getitem__(self, key):
        if isinstance(key, slice):
            indices = key.indices(len(self))
            return self.__get_slice(range(*indices))
        elif isinstance(key, int):
            return self.__compute_item(key)
        else:
            raise TypeError("list indices must be integers, not %s" % key.__class__.__name__)
        
    def __delitem__(self, key):
        if isinstance(key, slice):
            indices = key.indices(len(self))
            offset = 0
            for i in range(*indices):
                self.__del_item(i + offset)
                offset -= 1 
        elif isinstance(key, int):
            return self.__del_item(key)
        else:
            raise TypeError("list indices must be integers, not %s" % key.__class__.__name__)
    
    def __contains__(self, item):
        return self.contains(item)
        
    def __add__(self, other):
        command = LIST_COMMAND_NAME + LIST_CONCAT_SUBCOMMAND_NAME + self._get_object_id() + '\n' + other._get_object_id() + '\n' + END_COMMAND_PART
        answer = self._comm_channel.send_command(command)
        return get_return_value(answer, self._comm_channel)
    
    def __radd__(self, other):
        return self.__add__(other)
    
    def __iadd__(self, other):
        self.extend(other)
        return self
    
    def __mul__(self, other):
        command = LIST_COMMAND_NAME + LIST_MULT_SUBCOMMAND_NAME + self._get_object_id() + '\n' + get_command_part(other) + END_COMMAND_PART
        answer = self._comm_channel.send_command(command)
        return get_return_value(answer, self._comm_channel)
    
    def __rmul__(self, other):
        return self.__mul__(other)
    
    def __imul__(self, other):
        command = LIST_COMMAND_NAME + LIST_IMULT_SUBCOMMAND_NAME + self._get_object_id() + '\n' + get_command_part(other) + END_COMMAND_PART
        self._comm_channel.send_command(command)
        return self
        
    def append(self, value):
        self.add(value)
        
    def insert(self, key, value):
        if isinstance(key, int):
            new_key = self.__compute_index(key, True)
            return self.add(new_key, value)
        else:
            raise TypeError("list indices must be integers, not %s" % key.__class__.__name__)
        
    def extend(self, other_list):
        self.addAll(other_list)

    def pop(self, key=None):
        if key == None:
            new_key = self.size() - 1
        else:
            new_key = self.__compute_index(key) 
        return self.remove(new_key);
    
    def index(self, value):
        return self.indexOf(value)
    
    def count(self, value):
        command = LIST_COMMAND_NAME + LIST_COUNT_SUBCOMMAND_NAME + self._get_object_id() + '\n' + get_command_part(value) + END_COMMAND_PART
        answer = self._comm_channel.send_command(command)
        return get_return_value(answer, self.comm_channel)
    
    def sort(self):
        command = LIST_COMMAND_NAME + LIST_SORT_SUBCOMMAND_NAME + self._get_object_id() + '\n' + END_COMMAND_PART
        self._comm_channel.send_command(command)
    
    def reverse(self):
        command = LIST_COMMAND_NAME + LIST_REVERSE_SUBCOMMAND_NAME + self._get_object_id() + '\n' + END_COMMAND_PART
        self._comm_channel.send_command(command)
    
    # remove is automatically supported by Java...
    
    def __str__(self):
        return self.__repr__()
    
    def __repr__(self):
        # TODO Make it more efficient/pythonic
        # TODO Debug why strings are not outputed with apostrophes.
        if len(self) == 0:
            return '[]'
        else:
            srep = '['
            for elem in self:
                srep += repr(elem) + ', '
                
            return srep[:-2] + ']'

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
    
    Methods that are not defined by `JavaGateway` are always redirected to `entry_point`. For example, ``gateway.doThat()`` is equivalent to ``gateway.entry_point.doThat()``.
    This is a trade-off between convenience and potential confusion."""
    
    
    def __init__(self, comm_channel=None, auto_start=True, auto_field=True):
        """
        :param comm_channel: communication channel used to connect to the JVM. If `None`, a communication channel based on a socket with the default parameters is created.
        :param auto_start: if `True`, the JavaGateway connects to the JVM as soon as it is created. Otherwise, you need to explicitly call `gateway.comm_channel.start()`.
        """
        if comm_channel == None:
            comm_channel = CommChannel()
            
        comm_channel.auto_field = auto_field
            
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
