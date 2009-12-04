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

if __name__ == '__main__':
    s = socket(AF_INET,SOCK_STREAM)
    s.connect(('localhost', 25333))
    #str = re.escape('Hello World\n') + '\n'
    str = 'c\no123\nmethod1\n2\ntrue\n' + escape_new_line('\"Hello World\nThis is a test.\"\\n') + '\ntrue' + '\ne\n'
    print(str)
    s.send(str.encode('utf-8'))
    #s.send((re.escape('Hello World! This is éééàààà') + '\n').encode('utf-8'))
    #s.send((re.escape('Bonjour\n\tLe monde\n') + '\n').encode('utf-8'))
    s.close()
    print('done')