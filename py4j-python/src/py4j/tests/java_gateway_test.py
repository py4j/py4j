'''
Created on Dec 10, 2009

@author: barthelemy
'''
from IN import AF_INET, SOCK_STREAM
from multiprocessing.process import Process
from py4j.java_gateway import JavaGateway, Py4JError
from socket import socket
import subprocess
import time
import unittest

SERVER_PORT = 25333
TEST_PORT = 25332

def start_echo_server():
    subprocess.call(["java","-cp", "../../../../py4j-java/bin/","py4j.EchoServer"])
    
    
def start_echo_server_process():
    # XXX DO NOT FORGET TO KILL THE PROCESS IF THE TEST DOES NOT SUCCEED
    p = Process(target=start_echo_server)
    p.start()
    return p

def start_example_server():
    subprocess.call(["java", "-cp", "../../../../py4j-java/bin/", "py4j.examples.ExampleApplication"])
    
    
def start_example_app_process():
    # XXX DO NOT FORGET TO KILL THE PROCESS IF THE TEST DOES NOT SUCCEED
    p = Process(target=start_example_server)
    p.start()
    return p

def get_test_socket():
    testSocket = socket(AF_INET, SOCK_STREAM)
    testSocket.connect(('localhost', TEST_PORT))
    return testSocket

class TestCommChannel(object):
    """Communication Channel that does nothing. Useful for testing."""
    
    def __init__(self, return_message='yro0'):
        self.return_message = return_message
        pass
    
    def start(self):
        pass
    
    def stop(self):
        pass
    
    def send_command(self, command):
        self.last_message = command
        return self.return_message

class ProtocolTest(unittest.TestCase):
    def testProtocolSend(self):
        testChannel = TestCommChannel()
        gateway = JavaGateway(testChannel, True)
        e = gateway.getExample()
        self.assertEqual('c\nt\ngetExample\ne\n',testChannel.last_message)
        e.method1(1,True,'Hello\nWorld',e,None,1.5)
        self.assertEqual('c\no0\nmethod1\ni1\nbTrue\nsHello\\nWorld\nro0\nn\nd1.5\ne\n',testChannel.last_message)
    
    def testProtocolReceive(self):
        p = start_echo_server_process()
        time.sleep(1)
        try:
            testSocket = get_test_socket()
            testSocket.sendall('yro0\n'.encode('utf-8'))
            testSocket.sendall('ysHello World\n'.encode('utf-8'))
            testSocket.sendall('yi123\n'.encode('utf-8'))
            testSocket.sendall('yd1.25\n'.encode('utf-8'))
            testSocket.sendall('yn\n'.encode('utf-8'))
            testSocket.sendall('ybTrue\n'.encode('utf-8'))
            testSocket.close()
            time.sleep(1)
            
            gateway = JavaGateway()
            ex = gateway.getNewExample()
            self.assertEqual('Hello World',ex.method3(1, True))
            self.assertEqual(123,ex.method3())
            self.assertAlmostEqual(1.25,ex.method3())
            self.assertTrue(ex.method2() == None)
            self.assertTrue(ex.method4())
            gateway.close()
            
        except Exception as e:
            print('Error has occurred', e)
            self.fail('Problem occurred')
        p.join()

class IntegrationTest(unittest.TestCase):

    def setUp(self):
        self.p = start_echo_server_process()
        # This is to ensure that the server is started before connecting to it!
        time.sleep(1)

    def tearDown(self):
        self.p.join()

    def testIntegration(self):
        try:
            testSocket = get_test_socket()
            testSocket.sendall('yro0\n'.encode('utf-8'))
            testSocket.sendall('ysHello World\n'.encode('utf-8'))
            testSocket.sendall('yro1\n'.encode('utf-8'))
            testSocket.sendall('ysHello World2\n'.encode('utf-8'))
            testSocket.close()
            time.sleep(1)
            
            gateway = JavaGateway()
            ex = gateway.getNewExample()
            response = ex.method3(1, True)
            self.assertEqual('Hello World',response)
            ex2 = gateway.entry_point.getNewExample();
            response = ex2.method3(1, True)
            self.assertEqual('Hello World2',response)
            
            gateway.close()
        except Exception as e:
            print('Error has occurred', e)
            self.fail('Problem occurred')
            
    def testException(self):
        try:
            testSocket = get_test_socket()
            testSocket.sendall('yro0\n'.encode('utf-8'))
            testSocket.sendall('x\n')
            testSocket.close()
            time.sleep(1)
            
            gateway = JavaGateway()
            ex = gateway.getNewExample()
                
            try:
                ex.method3(1, True)
                self.fail('Should have failed!')
            except Py4JError:
                self.assertTrue(True)
            
            gateway.close()
            
        except Exception as e:
            print('Error has occurred', e)   
            self.fail('Problem occurred')
    
class JVMTest(unittest.TestCase):
    def setUp(self):
        self.p = start_example_app_process()
        # This is to ensure that the server is started before connecting to it!
        time.sleep(1)

    def tearDown(self):
        self.p.join()
        
    def testConstructors(self):
        gateway = JavaGateway()
        jvm = gateway.jvm
        sb = jvm.java.lang.StringBuffer('hello')
        sb.append('hello world')
        sb.append(1)
        self.assertEqual(sb.toString(), u'hellohello world1')
        
        l1 = jvm.java.util.ArrayList()
        l1.append('hello world')
        l1.append(1)
        self.assertEqual(2, len(l1))
        self.assertEqual(u'hello world', l1[0])
        l2 = [u'hello world', 1]
        self.assertEqual(str(l2), str(l1))
        gateway.shutdown()
        

        
    def testStaticMethods(self):
        gateway = JavaGateway()
        System = gateway.jvm.java.lang.System
        self.assertTrue(System.currentTimeMillis() > 0)
        self.assertEqual(u'123', gateway.jvm.java.lang.String.valueOf(123))
        gateway.shutdown()
    
    def testStaticFields(self):
        gateway = JavaGateway()
        Short = gateway.jvm.java.lang.Short
        self.assertEqual(-32768, Short.MIN_VALUE)
        System = gateway.jvm.java.lang.System
        self.assertFalse(System.out.checkError())
        gateway.shutdown()

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testGateway']
#    logger = logging.getLogger("py4j")
#    logger.setLevel(logging.DEBUG)
#    logger.addHandler(logging.StreamHandler())
    unittest.main()
