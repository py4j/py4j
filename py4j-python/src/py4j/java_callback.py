'''
Created on Apr 5, 2010

@author: Barthelemy Dagenais
'''
from py4j.java_gateway import *
from threading import RLock, Thread
import logging
import socket

PYTHON_PROXY_PREFIX = 'p'
ERROR_RETURN_MESSAGE = ERROR + '\n'

CALL_PROXY_COMMAND_NAME = 'c'
GARBAGE_COLLECT_PROXY_COMMAND_NAME = 'g'


logger = logging.getLogger("py4j.java_callback")

class CallbackServer(Thread):
    def __init__(self, pool, comm_channel, port = DEFAULT_PYTHON_PROXY_PORT):
        super(CallbackServer, self).__init__()
        self.comm_channel = comm_channel
        self.port = port
        self.pool = pool
        self.connections = []
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    def run(self):
        try:
            logger.info('Callback Server Starting')
            self.server_socket.bind(('localhost', self.port))
            self.server_socket.listen(5)
            logger.info('Socket listening on' + str(self.server_socket.getsockname()))
            socket, _ = self.server_socket.accept()
            input = socket.makefile('r', 0)
            connection = CallbackConnection(self.pool, input, socket, self.comm_channel)
            self.connections.append(connection)
            connection.start()
        except:
            logger.exception('Error while waiting for a connection.')
    
    def shutdown(self):
        logger.info('Callback Server Shutting Down')
        try:
            self.server_socket.shutdown(socket.SHUT_RDWR)
            self.server_socket.close()
        except:
            pass
        
        for connection in self.connections:
            try:
                connection.socket.shutdown(socket.SHUT_RDWR)
                connection.socket.close()
            except:
                pass
            
        self.pool.clear()
                
    
class CallbackConnection(Thread):
    def __init__(self, pool, input, socket, comm_channel):
        super(CallbackConnection, self).__init__()
        self.pool = pool
        self.input = input
        self.socket = socket
        self.comm_channel = comm_channel
    
    def run(self):
        logger.info('Callback Connection ready to receive messages')
        try:
            while True:
                command = self.input.readline().decode('utf-8')[:-1]
                obj_id = self.input.readline().decode('utf-8')[:-1]
                logger.info('Received command %s on object id %s' % (command,obj_id))
                if obj_id is None or len(obj_id.strip()) == 0:
                    break
                if command == CALL_PROXY_COMMAND_NAME:
                    return_message = self.call_proxy(obj_id, self.input)
                    self.socket.sendall(return_message.encode('utf-8'))
                elif command == GARBAGE_COLLECT_PROXY_COMMAND_NAME:
                    self.input.readline()
                    del(self.pool[obj_id])
                else:
                    logger.error('Unknown command %s' % command)
        except:
            logger.exception('Error while callback connection waiting for a message')
            
        try:
            self.socket.shutdown(socket.SHUT_RDWR)
            self.socket.close()
        except Exception:
            pass
            
    def call_proxy(self, obj_id, input):
        return_message = ERROR_RETURN_MESSAGE
        if obj_id in self.pool:
            try:
                method = input.readline().decode('utf-8')[:-1]
                params = self.get_params(input)
                return_value = getattr(self.pool[obj_id],method)(*params)
                return_message = 'y' + get_command_part(return_value)
            except:
                logger.exception('There was an exception while executing the Python Proxy.')
        return return_message
    
    def get_params(self, input):
        params = []
        temp = input.readline().decode('utf-8')[:-1]
        while temp != END:
            param = get_return_value('y'+temp, self.comm_channel)
            params.append(param)
            temp = input.readline().decode('utf-8')[:-1]
        return params
    
class PythonProxyPool(object):
    def __init__(self):
        self.lock = RLock()
        self.dict = {}
        self.next_id = 0
    
    def put(self, object):
        with self.lock:
            id = PYTHON_PROXY_PREFIX + str(self.next_id)
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
    
