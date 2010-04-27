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
    """The CallbackServer is responsible for receiving call back connection requests from the JVM.
    Usually connections are reused on the Java side, but there is at least one connection per 
    concurrent thread. 
    """
    
    def __init__(self, pool, comm_channel, port = DEFAULT_PYTHON_PROXY_PORT):
        """
        :param pool: the pool responsible of tracking Python objects passed to the Java side.
        :param comm_channel: the communication channel used to call Java objects.
        :param port: the port the CallbackServer is listening to.
        """
        super(CallbackServer, self).__init__()
        self.comm_channel = comm_channel
        self.port = port
        self.pool = pool
        self.connections = []
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.lock = RLock()
        self.is_shutdown = False
    
    def run(self):
        """Starts listening and accepting connection requests.
        
        This method is called when invoking `CallbackServer.start()`. A CallbackServer instance
        is created and started automatically when a :class:`JavaGateway <py4j.java_gateway.JavaGateway>`
        instance is created.
        """
        try:
            with self.lock:
                self.is_shutdown = False
            logger.info('Callback Server Starting')
            self.server_socket.bind(('localhost', self.port))
            self.server_socket.listen(5)
            logger.info('Socket listening on' + str(self.server_socket.getsockname()))
            socket, _ = self.server_socket.accept()
            input = socket.makefile('r', 0)
            connection = CallbackConnection(self.pool, input, socket, self.comm_channel)
            with self.lock:
                if not self.is_shutdown:
                    self.connections.append(connection)
                    connection.start()
                else:
                    connection.socket.shutdown(socket.SHUT_RDWR)
                    connection.socket.close()
        except:
            logger.exception('Error while waiting for a connection.')
    
    def shutdown(self):
        """Stops listening and accepting connection requests. All live connections are closed.
        
        This method can safely be called by another thread.        
        """
        logger.info('Callback Server Shutting Down')
        with self.lock:
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
    """A `CallbackConnection` receives callbacks and garbage collection requests from the Java side. 
    """
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
                    return_message = self._call_proxy(obj_id, self.input)
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
            
    def _call_proxy(self, obj_id, input):
        return_message = ERROR_RETURN_MESSAGE
        if obj_id in self.pool:
            try:
                method = input.readline().decode('utf-8')[:-1]
                params = self._get_params(input)
                return_value = getattr(self.pool[obj_id],method)(*params)
                return_message = 'y' + get_command_part(return_value)
            except:
                logger.exception('There was an exception while executing the Python Proxy.')
        return return_message
    
    def _get_params(self, input):
        params = []
        temp = input.readline().decode('utf-8')[:-1]
        while temp != END:
            param = get_return_value('y'+temp, self.comm_channel)
            params.append(param)
            temp = input.readline().decode('utf-8')[:-1]
        return params
    
class PythonProxyPool(object):
    """A `PythonProxyPool` manages proxies that are passed to the Java side. A proxy is a Python
    class that implements a Java interface.
    
    A proxy has an internal class named `Java` with a member named `interfaces` which is a list of
    fully qualified names (string) of the implemented interfaces.
    
    The `PythonProxyPool` implements a subset of the dict interface: `pool[id]`, `del(pool[id])`, 
    `pool.put(proxy)`, `pool.clear()`, `id in pool`, `len(pool)`.
    
    The `PythonProxyPool` is thread-safe.
    """
    def __init__(self):
        self.lock = RLock()
        self.dict = {}
        self.next_id = 0
    
    def put(self, object):
        """Adds a proxy to the pool.
        
        :param object: The proxy to add to the pool.
        :rtype: A unique identifier associated with the object.
        """
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
    
