'''
Created on Dec 10, 2009

@author: barthelemy
'''
from multiprocessing.process import Process
from py4j.finalizer import ThreadSafeFinalizer
from py4j.java_gateway import JavaGateway, Py4JError, JavaMember, get_field, \
    get_method, unescape_new_line, escape_new_line, CommChannel, CommChannelFactory
from socket import AF_INET, SOCK_STREAM, socket
from threading import Thread
import gc
import subprocess
import time
import unittest

SERVER_PORT = 25333
TEST_PORT = 25332

def start_echo_server():
    subprocess.call(["java", "-cp", "../../../../py4j-java/bin/", "py4j.EchoServer"])
    
    
def start_echo_server_process():
    # XXX DO NOT FORGET TO KILL THE PROCESS IF THE TEST DOES NOT SUCCEED
    p = Process(target=start_echo_server)
    p.start()
    return p

def start_example_server():
    subprocess.call(["java", "-Xmx512m", "-cp", "../../../../py4j-java/bin/", "py4j.examples.ExampleApplication"])
    
    
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
    
    counter = -1
    
    def __init__(self, return_message='yro'):
        self.address = 'localhost'
        self.port = 1234
        self.return_message = return_message
        self.is_connected = True
    
    def start(self):
        pass
    
    def stop(self):
        pass
    
    def send_command(self, command):
        TestCommChannel.counter += 1
        if not command.startswith('m\nd\n'):
            self.last_message = command
        return self.return_message + str(TestCommChannel.counter)
    
class ProtocolTest(unittest.TestCase):
    
    def testEscape(self):
        self.assertEqual("Hello\tWorld\n\\", unescape_new_line(escape_new_line("Hello\tWorld\n\\")))
    
    def testProtocolSend(self):
        testChannel = TestCommChannel()
        gateway = JavaGateway(testChannel, False)
        e = gateway.getExample()
        self.assertEqual('c\nt\ngetExample\ne\n', testChannel.last_message)
        e.method1(1, True, 'Hello\nWorld', e, None, 1.5)
        self.assertEqual('c\no0\nmethod1\ni1\nbTrue\nsHello\\nWorld\nro0\nn\nd1.5\ne\n', testChannel.last_message)
        del(e)
    
    def testProtocolReceive(self):
        p = start_echo_server_process()
        time.sleep(1)
        try:
            testSocket = get_test_socket()
            testSocket.sendall('yo\n'.encode('utf-8'))
            testSocket.sendall('yro0\n'.encode('utf-8'))
            testSocket.sendall('yo\n'.encode('utf-8'))
            testSocket.sendall('ysHello World\n'.encode('utf-8'))
            #testSocket.sendall('yo\n'.encode('utf-8')) Not necessary because method3 is cached!
            testSocket.sendall('yi123\n'.encode('utf-8'))
            #testSocket.sendall('yo\n'.encode('utf-8')) Not necessary because method3 is cached!
            testSocket.sendall('yd1.25\n'.encode('utf-8'))
            testSocket.sendall('yo\n'.encode('utf-8'))
            testSocket.sendall('yn\n'.encode('utf-8'))
            testSocket.sendall('yo\n'.encode('utf-8'))
            testSocket.sendall('ybTrue\n'.encode('utf-8'))
            testSocket.close()
            time.sleep(1)
            
            gateway = JavaGateway(auto_field=True)
            ex = gateway.getNewExample()
            self.assertEqual('Hello World', ex.method3(1, True))
            self.assertEqual(123, ex.method3())
            self.assertAlmostEqual(1.25, ex.method3())
            self.assertTrue(ex.method2() == None)
            self.assertTrue(ex.method4())
            gateway.shutdown()
                        
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
            testSocket.sendall('yo\n'.encode('utf-8'))
            testSocket.sendall('yro0\n'.encode('utf-8'))
            testSocket.sendall('yo\n'.encode('utf-8'))
            testSocket.sendall('ysHello World\n'.encode('utf-8'))
#            testSocket.sendall('yo\n'.encode('utf-8')) # No need because getNewExampe is in cache now!
            testSocket.sendall('yro1\n'.encode('utf-8'))
            testSocket.sendall('yo\n'.encode('utf-8'))
            testSocket.sendall('ysHello World2\n'.encode('utf-8'))
            testSocket.close()
            time.sleep(1)
            
            gateway = JavaGateway(auto_field=True)
            ex = gateway.getNewExample()
            response = ex.method3(1, True)
            self.assertEqual('Hello World', response)
            ex2 = gateway.entry_point.getNewExample();
            response = ex2.method3(1, True)
            self.assertEqual('Hello World2', response)
            
            gateway.shutdown()
        except Exception as e:
            print('Error has occurred', e)
            self.fail('Problem occurred')
            
    def testException(self):
        try:
            testSocket = get_test_socket()
            testSocket.sendall('yo\n'.encode('utf-8'))
            testSocket.sendall('yro0\n'.encode('utf-8'))
            testSocket.sendall('yo\n'.encode('utf-8'))
            testSocket.sendall('x\n')
            testSocket.close()
            time.sleep(1)
            
            gateway = JavaGateway(auto_field=True)
            ex = gateway.getNewExample()
                
            try:
                ex.method3(1, True)
                self.fail('Should have failed!')
            except Py4JError:
                self.assertTrue(True)
            
            gateway.shutdown()
            
        except Exception as e:
            print('Error has occurred', e)   
            self.fail('Problem occurred')

class FieldTest(unittest.TestCase):
    def setUp(self):
        self.p = start_example_app_process()
        # This is to ensure that the server is started before connecting to it!
        time.sleep(1)

    def tearDown(self):
        self.gateway.shutdown()
        self.p.join()
        
    def testAutoField(self):
        self.gateway = JavaGateway(auto_field=True)
        gateway = self.gateway
        ex = gateway.getNewExample()
        self.assertEqual(ex.field10, 10)
        sb = ex.field20
        sb.append('Hello')
        self.assertEqual(u'Hello', sb.toString())
        self.assertTrue(ex.field21 == None)
    
    def testNoField(self):
        self.gateway = JavaGateway(auto_field=True)
        gateway = self.gateway
        ex = gateway.getNewExample()
        member = ex.field50
        self.assertTrue(isinstance(member, JavaMember))
        
    def testNoAutoField(self):
        self.gateway = JavaGateway(auto_field=False)
        gateway = self.gateway
        ex = gateway.getNewExample()
        self.assertTrue(isinstance(ex.field10, JavaMember))
        self.assertTrue(isinstance(ex.field50, JavaMember))
        self.assertEqual(10, get_field(ex, 'field10'))
        
        try:
            get_field(ex, 'field50')
            self.fail()
        except:
            self.assertTrue(True)
            
        ex._auto_field = True
        sb = ex.field20
        sb.append('Hello')
        self.assertEqual(u'Hello', sb.toString())
        
        try:
            get_field(ex, 'field20')
            self.fail()
        except:
            self.assertTrue(True)
            
        
    def testGetMethod(self):
        # This is necessary if a field hides a method...
        self.gateway = JavaGateway()
        gateway = self.gateway
        ex = gateway.getNewExample()
        self.assertEqual(1, get_method(ex, 'method1')())
        
class MemoryManagementText(unittest.TestCase):
    def setUp(self):
        self.p = start_example_app_process()
        # This is to ensure that the server is started before connecting to it!
        time.sleep(1)
        
    def tearDown(self):
        self.p.join()
        gc.collect()
        
        
    def testNoAttach(self):
        gateway = JavaGateway()
        gateway2 = JavaGateway()
        sb = gateway.jvm.java.lang.StringBuffer()
        sb.append('Hello World')
        gateway.shutdown()
        try:
            sb.append('Python')
            self.fail('Should have failed')
        except:
            self.assertTrue(True)
        try:
            sb2 = gateway2.jvm.java.lang.StringBuffer()
            sb2.append('Python')
            self.fail('Should have failed')
        except:
            self.assertTrue(True)
        
    def testDetach(self):
        gateway = JavaGateway()
        sb = gateway.jvm.java.lang.StringBuffer()
        sb.append('Hello World')
        gateway.detach(sb)
        sb2 = gateway.jvm.java.lang.StringBuffer()
        sb2.append('Hello World')
        sb2._detach()
        gc.collect()
        self.assertEqual(len(ThreadSafeFinalizer.finalizers), 1)
        gateway.shutdown()
        
class JVMTest(unittest.TestCase):
    def setUp(self):
        self.p = start_example_app_process()
        # This is to ensure that the server is started before connecting to it!
        time.sleep(1)
        self.gateway = JavaGateway()

    def tearDown(self):
        self.gateway.shutdown()
        self.p.join()
        
    def testConstructors(self):
        jvm = self.gateway.jvm
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
        print(l1)
        print(l2)
        self.assertEqual(str(l2), str(l1))
        
    def testStaticMethods(self):
        System = self.gateway.jvm.java.lang.System
        self.assertTrue(System.currentTimeMillis() > 0)
        self.assertEqual(u'123', self.gateway.jvm.java.lang.String.valueOf(123))
    
    def testStaticFields(self):
        Short = self.gateway.jvm.java.lang.Short
        self.assertEqual(-32768, Short.MIN_VALUE)
        System = self.gateway.jvm.java.lang.System
        self.assertFalse(System.out.checkError())

class HelpTest(unittest.TestCase):
    
    def setUp(self):
        self.p = start_example_app_process()
        # This is to ensure that the server is started before connecting to it!
        time.sleep(1)
        self.gateway = JavaGateway()

    def tearDown(self):
        self.gateway.shutdown()
        self.p.join()
        
    def testHelpObject(self):
        ex = self.gateway.getNewExample()
        help_page = self.gateway.help(ex, short_name=True, display=False)
        print(help_page)
        self.assertEqual(828, len(help_page))
        
    def testHelpClass(self):
        String = self.gateway.jvm.java.lang.String
        help_page = self.gateway.help(String, short_name=False, display=False)
        print(help_page)
        self.assertEqual(3439, len(help_page))

class Runner(Thread):
    def __init__(self, runner_range, gateway):
        Thread.__init__(self)
        self.range = runner_range
        self.gateway = gateway
        self.ok = True
        
    def run(self):
        ex = self.gateway.getNewExample()
        for i in self.range:
            try:
                l = ex.getList(i)
                if len(l) != i:
                    self.ok = False
                    break
                self.gateway.detach(l)
#                gc.collect()
            except Exception:
                self.ok = False
                break
            
class ThreadTest(unittest.TestCase):
    def setUp(self):
        self.p = start_example_app_process()
        # This is to ensure that the server is started before connecting to it!
        time.sleep(1)
        comm_channel = CommChannelFactory()
        self.gateway = JavaGateway(comm_channel=comm_channel)

    def tearDown(self):
        self.gateway.shutdown()
        self.p.join()
        
    def testStress(self):
        # Real stress test!
#        runner1 = Runner(xrange(1,10000,2),self.gateway)
#        runner2 = Runner(xrange(1000,1000000,10000), self.gateway)
#        runner3 = Runner(xrange(1000,1000000,10000), self.gateway)
        # Small stress test
        runner1 = Runner(xrange(1,10000,1000),self.gateway)
        runner2 = Runner(xrange(1000,1000000,100000), self.gateway)
        runner3 = Runner(xrange(1000,1000000,100000), self.gateway)
        runner1.start()
        runner2.start()
        runner3.start()
        runner1.join()
        runner2.join()
        runner3.join()
        self.assertTrue(runner1.ok)
        self.assertTrue(runner2.ok)
        self.assertTrue(runner3.ok)
        
    
        

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testGateway']
#    logger = logging.getLogger("py4j")
#    logger.setLevel(logging.DEBUG)
#    logger.addHandler(logging.StreamHandler())
    unittest.main()
