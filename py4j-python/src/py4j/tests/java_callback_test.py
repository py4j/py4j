'''
Created on Apr 5, 2010

@author: Barthelemy Dagenais
'''
from multiprocessing.process import Process
from py4j.java_gateway import JavaGateway, DEFAULT_PYTHON_PROXY_PORT
from py4j.java_callback import PythonProxyPool, CallbackServer
from threading import Thread
import logging
import socket
import subprocess
import time
import unittest


def start_example_server():
    subprocess.call(["java", "-cp", "../../../../py4j-java/bin/", "py4j.examples.ExampleApplication"])
    
    
def start_example_app_process():
    # XXX DO NOT FORGET TO KILL THE PROCESS IF THE TEST DOES NOT SUCCEED
    p = Process(target=start_example_server)
    p.start()
    return p

class Runner(Thread):
    def __init__(self, runner_range, pool):
        Thread.__init__(self)
        self.range = runner_range
        self.pool = pool
        self.ok = True
        
    def run(self):
        for i in self.range:
            try:
                id = self.pool.put(i)
                self.ok = id in self.pool and self.pool[id] == i
                if not self.ok:
                    break
            except Exception as e:
                print(e)
                self.ok = False
                break

class TestPool(unittest.TestCase):

#    def setUp(self):
##        logger = logging.getLogger("py4j")
##        logger.setLevel(logging.DEBUG)
##        logger.addHandler(logging.StreamHandler())
#        self.p = start_example_app_process()
#        time.sleep(0.5)
#        self.gateway = JavaGateway()
#        
#    def tearDown(self):
#        self.p.terminate()
#        self.gateway.shutdown()
#        time.sleep(0.5)
    
    def testPool(self):
        pool = PythonProxyPool()
        runners = [Runner(xrange(0,10000),pool) for _ in xrange(0,3)]
        for runner in runners:
            runner.start()
            
        for runner in runners:
            runner.join()
            
        for runner in runners:
            self.assertTrue(runner.ok)

class SimpleProxy(object):
    
    def hello(self, i, j):
        return 'Hello\nWorld' + str(i) + str(j)
            
class TestConnection(unittest.TestCase):
    
    def testSimpleConnection(self):
        logger = logging.getLogger("py4j")
        logger.setLevel(logging.DEBUG)
        logger.addHandler(logging.StreamHandler())
        pool = PythonProxyPool()
        obj = SimpleProxy()
        id = pool.put(obj)
        server = CallbackServer(pool, None)
        server.start()
        time.sleep(0.5)
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect(('localhost', DEFAULT_PYTHON_PROXY_PORT))
        stream = sock.makefile('r', 0)
        
        command = id + '\nhello\ni5\nsA\\nB\ne\n'
        sock.sendall(command.encode('utf-8'))
        answer = stream.readline().decode('utf-8')[:-1]
        self.assertEqual('ysHello\\nWorld5A\\nB',answer)
        
        command = id + '\nhello\ni10\nsA\\nB\ne\n'
        sock.sendall(command.encode('utf-8'))
        answer = stream.readline().decode('utf-8')[:-1]
        self.assertEqual('ysHello\\nWorld10A\\nB',answer)
        
        try:
            sock.close()
            server.shutdown()
        except:
            pass
            
if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
    
