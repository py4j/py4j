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
NULL_TYPE = 'n'
END = 'e'
ERROR = 'x'
SUCCESS = 'y'

CALL_COMMAND = 'c\n'

class Py4JError(Exception):
    def __init__(self, value):
        self.value = value
    
    def __str__(self):
        return repr(self.value)

class CommChannel(object):
    """Default communication channel (socket based) responsible for communicating with the Java Virtual Machine.
    
    This class will eventually be used to restrict the access to the socket or replace the socket communication. 
    """
    
    def __init__(self, address='localhost', port=25333):
        self.address = address
        self.port = port
        self.socket = socket(AF_INET, SOCK_STREAM)
        
    def start(self):
        self.socket.connect((self.address, self.port))
    
    def stop(self):
        self.socket.close()
        
    def send_command(self, command):
        logger.debug("Command to send: %s" % (command))
        self.socket.sendall(command.encode('utf-8'))
        answer = self.socket.recv(BUFFER_SIZE).decode('utf-8')
        logger.debug("Answer received: %s" % (answer))
        return answer

class NullCommChannel(object):
    """Communication Channel that does nothing. Useful for testing."""
    
    def __init__(self, return_message=SUCCESS + NULL_TYPE):
        self.return_message = return_message
        pass
    
    def start(self):
        pass
    
    def stop(self):
        pass
    
    def send_command(self, command):
        logger.debug("Null command received: %s" % (command))
        return self.return_message


class JavaMember(object):
    """Represents a member (field, method) of a Java Object.
    
    For now, only methods are supported.
    """
    
    def __init__(self, name, target_id, comm_channel):
        self.name = name
        self.target_id = target_id
        self.comm_channel = comm_channel
        self.command_header = self.target_id + '\n' + self.name + '\n'
        
    def escape_new_line(self, original):
        temp = original.replace('\\', '\\\\')
        final = temp.replace('\n', '\\n')
        return final
    
    def get_command_part(self, parameter):
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
            command_part = STRING_TYPE + self.escape_new_line(parameter)
        else:
            command_part = REFERENCE_TYPE + parameter.get_object_id()
        
        return command_part + '\n'
    
    def get_return_value(self, answer):
        if len(answer) == 1 or answer[0] != SUCCESS:
            raise Py4JError('An error occured while calling %s.%s' % (self.target_id, self.name))
        elif answer[1] == NULL_TYPE:
            return None
        elif answer[1] == REFERENCE_TYPE:
            return JavaObject(answer[2:], self.comm_channel)
        elif answer[1] == INTEGER_TYPE:
            return int(answer[2:])
        elif answer[1] == BOOLEAN_TYPE:
            return bool(answer[2:])
        elif answer[1] == DOUBLE_TYPE:
            return float(answer[2:])
        elif answer[1] == STRING_TYPE:
            return answer[2:]
        
    def __call__(self, *args):
        args_command = ''.join([self.get_command_part(arg) for arg in args])
        command = CALL_COMMAND + self.command_header + args_command + END + '\n'
        answer = self.comm_channel.send_command(command)
        return_value = self.get_return_value(answer)
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
    

class JavaGateway(JavaObject):
    def __init__(self, comm_channel=None):
        
        # This is the default Java Gateway
        # The comm channel can be customized to not send anything.
        if comm_channel == None:
            comm_channel = CommChannel()
            
        JavaObject.__init__(self, GATEWAY_OBJECT_ID, comm_channel)
    
            
if __name__ == '__main__':
    logger = logging.getLogger("py4j")
    logger.setLevel(logging.DEBUG)
    logger.addHandler(logging.StreamHandler())
    
    gateway = JavaGateway()
    gateway.comm_channel.start()
    ex = gateway.getNewExample()
    response = ex.method3(1, True)
    print(response)
    gateway.comm_channel.stop()
    print('done')
