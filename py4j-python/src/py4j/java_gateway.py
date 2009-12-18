# -*- coding: UTF-8 -*-
"""Module to interact with objects in a Java Virtual Machine from a Pyton Virtual Machine.

Created on Dec 3, 2009

@author: Barthelemy Dagenais
"""

import logging
from IN import AF_INET
from IN import SOCK_STREAM
from socket import socket

class NullHandler(logging.Handler):
    def emit(self, record):
        pass

null_handler = NullHandler()
logging.getLogger("py4j").addHandler(null_handler)
logger = logging.getLogger("py4j.java_gateway")

BUFFER_SIZE = 4096
DEFAULT_PORT = 25333
GATEWAY_OBJECT_ID = 'g'
INTEGER_TYPE = 'i'
BOOLEAN_TYPE = 'b'
DOUBLE_TYPE = 'd'
STRING_TYPE = 's'
REFERENCE_TYPE = 'r'
LIST_TYPE = 'l'
NULL_TYPE = 'n'
END = 'e'
ERROR = 'x'
SUCCESS = 'y'

CALL_COMMAND = 'c\n'
SHUTDOWN_COMMAND = 's\n'
LIST_COMMAND = 'l\n'
LIST_SORT_COMMAND = 's\n'
LIST_REVERSE_COMMAND = 'r\n'
LIST_SLICE_COMMAND = 'l\n'

# TODO
LIST_CONCAT_COMMAND = 'a\n'
LIST_MULT_COMMAND = 'm\n'
LIST_IMULT_COMMAND = 'i\n'
LIST_COUNT_COMMAND = 'f\n'


def escape_new_line(original):
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
        command_part = REFERENCE_TYPE + parameter.get_object_id()
    
    return command_part + '\n'

def get_return_value(answer, comm_channel, target_id = None, name = None):
    if len(answer) == 0 or answer[0] != SUCCESS:
        raise Py4JError('An error occurred while calling %s%s%s' % (target_id, '.', name))
    elif answer[1] == NULL_TYPE:
        return None
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

class Py4JError(Exception):
    def __init__(self, value):
        self.value = value
    
    def __str__(self):
        return repr(self.value)

class CommChannel(object):
    """Default communication channel (socket based) responsible for communicating with the Java Virtual Machine.
    
    This class will eventually be used to restrict the access to the socket or replace the socket communication. 
    """
    
    def __init__(self, address='localhost', port=25333, auto_close=True):
        self.address = address
        self.port = port
        self.socket = socket(AF_INET, SOCK_STREAM)
        self.is_connected = False
        self.auto_close = auto_close
        
    def start(self):
        self.socket.connect((self.address, self.port))
        self.is_connected = True
    
    def stop(self):
        self.socket.close()
        self.is_connected = False
        
    def shutdown(self):
        try:
            self.socket.sendall(SHUTDOWN_COMMAND.encode('utf-8'))
        except Exception:
            # Do nothing!
            pass

    def __del__(self):
        """Closes the socket if auto_delete is True and the socket is opened. 
        
        This is an acceptable practice if you know that your Python VM implements garbage collection 
        and closing sockets immediately is not a concern. Otherwise, it is always better (because it 
        is predictable) to explicitly close the socket by calling CommChannel.close().
        """
        if self.auto_close and self.socket != None and self.is_connected:
            self.stop()
        
    def send_command(self, command):
        logger.debug("Command to send: %s" % (command))
        self.socket.sendall(command.encode('utf-8'))
        answer = self.socket.recv(BUFFER_SIZE).decode('utf-8')
        logger.debug("Answer received: %s" % (answer))
        return answer

class JavaMember(object):
    """Represents a member (field, method) of a Java Object.
    
    For now, only methods are supported.
    """
    
    def __init__(self, name, target_id, comm_channel):
        self.name = name
        self.target_id = target_id
        self.comm_channel = comm_channel
        self.command_header = self.target_id + '\n' + self.name + '\n'
        
    def __call__(self, *args):
        args_command = ''.join([get_command_part(arg) for arg in args])
        command = CALL_COMMAND + self.command_header + args_command + END + '\n'
        answer = self.comm_channel.send_command(command)
        return_value = get_return_value(answer, self.comm_channel, self.target_id, self.name)
        return return_value



class JavaObject(object):
    def __init__(self, target_id, comm_channel):
        self.target_id = target_id
        self.methods = {}
        self.comm_channel = comm_channel
        
    def get_object_id(self):
        return self.target_id
        
    def __getattr__(self, name):
        if name not in self.methods:
            self.methods[name] = JavaMember(name, self.target_id, self.comm_channel)
        return self.methods[name]
    
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
    def __init__(self, target_id, comm_channel):
        JavaObject.__init__(self, target_id, comm_channel)
        self.next_name = 'next'
        
    def __iter__(self):
        return self
    
    def next(self):
        if self.next_name not in self.methods:
            self.methods[self.next_name] = JavaMember(self.next_name, self.target_id, self.comm_channel)
        try:
            return self.methods[self.next_name]()
        except Py4JError:
            raise StopIteration()
    
class JavaList(JavaObject):
    def __init__(self, target_id, comm_channel):
        JavaObject.__init__(self, target_id, comm_channel)

    def __len__(self):
        return self.size()

    def __iter__(self):
        return JavaListIterator(self.iterator().get_object_id(), self.comm_channel)
    
    def __compute_index(self, key):
        size = self.size()
        if 0 <= key < size:
            return key
        elif key < 0 and abs(key) <= size:
            return size + key
        else:
            raise IndexError("list index out of range")
    
    def __compute_item(self, key):
        new_key = self.__compute_index(key)
        return self.get(new_key)
    
    def __set_item(self, key, value):
        new_key = self.__compute_index(key)
        self.set(new_key, value)
    
    def __del_item(self, key):
        new_key = self.__compute_index(key)
        self.remove(new_key)

    def __setitem__(self, key, value):
        if isinstance(key, slice):
#            indices = key.indices(len(self))
#            for i in range(*indices):
#                self.__set_item(i, value)
            raise Py4JError('Slicing not currently supported.') 
        elif isinstance(key, int):
            return self.__set_item(key, value)
        else:
            raise TypeError("list indices must be integers, not %s" % key.__class__.__name__)
        
    def __getitem__(self, key):
        if isinstance(key, slice):
#            indices = key.indices(len(self))
#            new_list = [self.compute_item(i) for i in range(*indices)]
#            return test_list(len(new_list),new_list)
            raise Py4JError('Slicing not currently supported.')
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
        command = LIST_COMMAND + LIST_CONCAT_COMMAND + self.get_object_id() + '\n' + other.get_object_id() + '\n' + END + '\n'
        answer = self.comm_channel.send_command(command)
        return get_return_value(answer, self.comm_channel)
    
    def __radd__(self, other):
        return self.__add__(other)
    
    def __iadd__(self, other):
        self.extend(other)
        return self
    
    def __mul__(self, other):
        command = LIST_COMMAND + LIST_MULT_COMMAND + self.get_object_id() + '\n' + get_command_part(other) + END + '\n'
        answer = self.comm_channel.send_command(command)
        return get_return_value(answer, self.comm_channel)
    
    def __rmul__(self, other):
        return self.__mul__(other)
    
    def __imul__(self, other):
        command = LIST_COMMAND + LIST_IMULT_COMMAND + self.get_object_id() + '\n' + get_command_part(other) + END + '\n'
        self.comm_channel.send_command(command)
        return self
        
    def append(self, value):
        self.add(value)
        
    def insert(self, key, value):
        if isinstance(key, int):
            new_key = self.__compute_index(key)
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
        command = LIST_COMMAND + LIST_COUNT_COMMAND + self.get_object_id() + '\n' + get_command_part(value) + END + '\n'
        answer = self.comm_channel.send_command(command)
        return get_return_value(answer, self.comm_channel)
    
    def sort(self):
        command = LIST_COMMAND + LIST_SORT_COMMAND + self.get_object_id() + '\n' + END + '\n'
        self.comm_channel.send_command(command)
    
    def reverse(self):
        command = LIST_COMMAND + LIST_REVERSE_COMMAND + self.get_object_id() + '\n' + END + '\n'
        self.comm_channel.send_command(command)
    
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

class JavaGateway(JavaObject):
    def __init__(self, comm_channel=None, auto_start=True):
        
        # This is the default Java Gateway
        # The comm channel can be customized to not send anything.
        if comm_channel == None:
            comm_channel = CommChannel()
            
        JavaObject.__init__(self, GATEWAY_OBJECT_ID, comm_channel)
        
        if auto_start:
            self.comm_channel.start()
    
            
if __name__ == '__main__':
#    logger = logging.getLogger("py4j")
#    logger.setLevel(logging.DEBUG)
#    logger.addHandler(logging.StreamHandler())
    
    gateway = JavaGateway()
    ex = gateway.getNewExample()
    response = ex.method3(1, True)
    print(response)
    print('done')
    
    l = ex.getList(3)
    print(len(l))
    print(l)
    print(l[1])
    l[1] = 'Bonjour'
    print(l)
    del l[1]
    print(l)
    print(type(l[1]))
#    for s in l:
#        print(s)
    
    gateway.comm_channel.stop()
