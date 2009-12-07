# -*- coding: UTF-8 -*-
'''
Created on Dec 3, 2009

@author: Barthelemy Dagenais
'''

from IN import AF_INET
from IN import SOCK_STREAM
from socket import socket
import re

DEFAULT_PORT = 25333

def escape_new_line(original):
    temp = original.replace('\\','\\\\')
    final = temp.replace('\n','\\n')
    return final

class CommChannel(object):
    # Could be eventually used to restrict access to socket
    def __init__(self, socket):
        self.socket = socket

class JavaMethod(object):
    def __init__(self, name, target_id, comm_channel):
        self.name = name
        self.target_id = target_id
        self.comm_channel = comm_channel
        
    def __call__(self, *args):
        print('Calling ' + self.name + ' from ' + self.target_id)
        for arg in args:
            print(arg)

class JavaObject(object):
    def __init__(self, target_id):
        self.target_id = target_id
        self.methods = {}
        
    def __getattr__(self, name):
        if name not in self.methods:
            self.methods[name] = JavaMethod(name,'g', self.comm_channel)
        return self.methods[name]

class JavaGateway(object):
    def __init__(self, port=25333):
        self.methods = {}
        self.socket = socket(AF_INET,SOCK_STREAM)
        self.comm_channel = CommChannel(self.socket) 
            
    def __getattr__(self, name):
        if name not in self.methods:
            self.methods[name] = JavaMethod(name,'g', self.comm_channel)
        return self.methods[name]

if __name__ == '__main__':
    gateway = JavaGateway()
    gateway.getExample(1,2,'hello')
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