# -*- coding: UTF-8 -*-
'''
Created on Dec 3, 2009

@author: Barthelemy Dagenais
'''

from IN import AF_INET
from IN import SOCK_STREAM
from socket import socket

DEFAULT_PORT = 25333
GATEWAY_OBJECT_ID = 'g'
INTEGER_TYPE = 'i';
BOOLEAN_TYPE = 'b';
DOUBLE_TYPE = 'd';
STRING_TYPE = 's';
REFERENCE_TYPE = 'r';
NULL_TYPE = 'n';
END = 'e';



class CommChannel(object):
    # Could be eventually used to restrict access to socket
    def __init__(self, socket):
        self.socket = socket

class JavaMember(object):
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
        if isinstance(parameter, int) or isinstance(parameter, long):
            command_part = INTEGER_TYPE + str(parameter)
        elif isinstance(parameter, bool):
            command_part = BOOLEAN_TYPE + str(parameter)
        elif isinstance(parameter, float):
            command_part = DOUBLE_TYPE + str(parameter) 
        elif isinstance(parameter, basestring):
            command_part = STRING_TYPE + self.escape_new_line(parameter)
        else:
            command_part = REFERENCE_TYPE + parameter.get_object_id()
        
        return command_part + '\n'
        
    def __call__(self, *args):
        args_command = ''.join([self.get_command_part(arg) for arg in args])
        command = self.command_header + args_command + END + '\n'
        print(command)

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
    def __init__(self, address='localhost', port=25333):
        self.address = address
        self.port = port
        self.socket = socket(AF_INET, SOCK_STREAM)
        JavaObject.__init__(self, GATEWAY_OBJECT_ID, CommChannel(self.socket))
        
    def start(self):
        self.socket.connect(self.address, self.port)
    
    def stop(self):
        self.socket.close()
            
if __name__ == '__main__':
    gateway = JavaGateway()
    gateway.getExample(1, 2, 'hello world\nNewT\\n!')
    gateway.socket.close()
    print('done')
#    s = socket(AF_INET,SOCK_STREAM)
#    s.connect(('localhost', 25333))
#    #str = re.escape('Hello World\n') + '\n'
#    str = 'g\ngetNewExample\ne\n'
#    print(str)
#    s.send(str.encode('utf-8'))
#    resp = s.recv(4096).decode('utf-8')
#    print(resp)
#    #s.send((re.escape('Hello World! This is éééàààà') + '\n').encode('utf-8'))
#    #s.send((re.escape('Bonjour\n\tLe monde\n') + '\n').encode('utf-8'))
#    s.close()
#    print('done')
