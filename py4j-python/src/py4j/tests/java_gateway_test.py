'''
Created on Dec 10, 2009

@author: barthelemy
'''
from socket import AF_INET, SOCK_STREAM
from multiprocessing.process import Process
from py4j.java_gateway import JavaGateway, Py4JError, JavaMember, get_field, get_method, \
    unescape_new_line, escape_new_line
from socket import socket
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
        self.is_connected = True
        pass
    
    def start(self):
        pass
    
    def stop(self):
        pass
    
    def send_command(self, command):
        self.last_message = command
        return self.return_message
    
    def delay_command(self, command):
        pass
    
    def send_delay(self):
        pass
    
class ProtocolTest(unittest.TestCase):
    
    def testEscape(self):
        self.assertEqual("Hello\tWorld\n\\",unescape_new_line(escape_new_line("Hello\tWorld\n\\")))
    
    def testProtocolSend(self):
        testChannel = TestCommChannel()
        gateway = JavaGateway(testChannel, True, False)
        e = gateway.getExample()
        self.assertEqual('c\nt\ngetExample\ne\n', testChannel.last_message)
        e.method1(1, True, 'Hello\nWorld', e, None, 1.5)
        self.assertEqual('c\no0\nmethod1\ni1\nbTrue\nsHello\\nWorld\nro0\nn\nd1.5\ne\n', testChannel.last_message)
    
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
            testSocket.sendall('yo\n'.encode('utf-8'))
            testSocket.sendall('yro0\n'.encode('utf-8'))
            testSocket.sendall('yo\n'.encode('utf-8'))
            testSocket.sendall('ysHello World\n'.encode('utf-8'))
            testSocket.sendall('yo\n'.encode('utf-8'))
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
            
            gateway.close()
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
            
            gateway.close()
            
        except Exception as e:
            print('Error has occurred', e)   
            self.fail('Problem occurred')

class FieldTest(unittest.TestCase):
    def setUp(self):
        self.p = start_example_app_process()
        # This is to ensure that the server is started before connecting to it!
        time.sleep(1)

    def tearDown(self):
        self.p.join()
        
    def testAutoField(self):
        gateway = JavaGateway(auto_field=True)
        ex = gateway.getNewExample()
        self.assertEqual(ex.field10, 10)
        sb = ex.field20
        sb.append('Hello')
        self.assertEqual(u'Hello', sb.toString())
        self.assertTrue(ex.field21 == None)
        gateway.shutdown()
    
    def testNoField(self):
        gateway = JavaGateway(auto_field=True)
        ex = gateway.getNewExample()
        member = ex.field50
        self.assertTrue(isinstance(member, JavaMember))
        gateway.shutdown()
        
    def testNoAutoField(self):
        gateway = JavaGateway(auto_field=False)
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
            
        gateway.shutdown()
        
    def testGetMethod(self):
        # This is necessary if a field hides a method...
        gateway = JavaGateway()
        ex = gateway.getNewExample()
        self.assertEqual(1, get_method(ex, 'method1')())
        gateway.shutdown()
        
class MemoryManagementText(unittest.TestCase):
    def setUp(self):
        self.p = start_example_app_process()
        # This is to ensure that the server is started before connecting to it!
        time.sleep(1)
        
    def tearDown(self):
        self.p.join()
        
    def testAttach(self):
        gateway = JavaGateway()
        gateway2 = JavaGateway()
        sb = gateway.jvm.java.lang.StringBuffer()
        sb.append('Hello World')
        sb2 = gateway2.attach(sb)
        gateway.close()
        sb2.append('Python')
        self.assertEqual(u'Hello WorldPython',sb2.toString())
        gateway2.shutdown()
        
    def testAttachException(self):
        gateway = JavaGateway()
        gateway2 = JavaGateway()
        sb = gateway.jvm.java.lang.StringBuffer()
        sb.append('Hello World')
        gateway.close()
        
        # Wait is necessary, otherwise, it may happen that sb is still not deleted when attach is sent:
        # This is because close and attach can be executed in parallel on the Java side. The joy of multiple gateways...
        time.sleep(1)
        
        try:
            gateway2.attach(sb)
            self.fail('Should have failed')
        except:
            self.assertTrue(True)

        gateway2.shutdown()
        
    def testNoAttach(self):
        gateway = JavaGateway()
        gateway2 = JavaGateway()
        sb = gateway.jvm.java.lang.StringBuffer()
        sb.append('Hello World')
        gateway.close()
        try:
            sb.append('Python')
            self.fail('Should have failed')
        except:
            self.assertTrue(True)
        gateway2.shutdown()
        
class ConnectionPropertyTest(unittest.TestCase):
    def setUp(self):
        self.p = start_example_app_process()
        # This is to ensure that the server is started before connecting to it!
        time.sleep(1)
        
    def tearDown(self):
        self.p.join()
        
    def testDefaultProperties(self):
        gateway = JavaGateway()
        gateway2 = JavaGateway()
        
        sb = gateway.jvm.java.lang.StringBuffer()
        sb.append('Hello World')
        self.assertEqual(u'Hello World', sb.toString())
        gateway.close()
        
        try:
            # Should not work because sb reference has been removed from the gateway when the
            # gateway connection closed.
            l = gateway2.jvm.java.util.ArrayList()
            l.append(sb)
            self.fail()
        except:
            self.assertTrue(True)
            
        gateway2.shutdown()
        
        
    def testDontCleanConnection(self):
        gateway = JavaGateway()
        gateway.connection_property.setCleanConnection(False)
        gateway2 = JavaGateway()
        
        sb = gateway.jvm.java.lang.StringBuffer()
        sb.append('Hello World')
        
        self.assertEqual(u'Hello World', sb.toString())
        gateway.close()
        
        l = gateway2.jvm.java.util.ArrayList()
        l.append(sb)
        sb2 = l[0]
        self.assertEqual(u'Hello World', sb2.toString())
            
        sb2.append('Should Work Now')
        self.assertEqual(u'Hello WorldShould Work Now', sb2.toString())
        
        gateway2.shutdown()
        
        try:
            # Should not work because gateway has shutdown.
            sb2.append('Should not work')
            self.fail()
        except:
            self.assertTrue(True)

        
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
        print(l1)
        print(l2)
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
        self.assertEqual(695,len(help_page))
        
    def testHelpClass(self):
        String = self.gateway.jvm.java.lang.String
        help_page = self.gateway.help(String, short_name=False, display=False)
        print(help_page)
        self.assertEqual(3439,len(help_page))
        

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testGateway']
#    logger = logging.getLogger("py4j")
#    logger.setLevel(logging.DEBUG)
#    logger.addHandler(logging.StreamHandler())
    unittest.main()
