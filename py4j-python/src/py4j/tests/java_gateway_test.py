'''
Created on Dec 10, 2009

@author: barthelemy
'''
from multiprocessing.process import Process
from py4j.finalizer import ThreadSafeFinalizer
from py4j.protocol import *
from py4j.java_gateway import JavaGateway, Py4JError, JavaMember, get_field, get_method, \
     GatewayConnection, GatewayClient, set_field, java_import, Py4JNetworkError, JavaObject

from socket import AF_INET, SOCK_STREAM, socket
from threading import Thread
from traceback import print_exc
import gc
import subprocess
import time
import unittest
import os

SERVER_PORT = 25333
TEST_PORT = 25332
PY4J_JAVA_PATH = os.path.join(os.path.dirname(os.path.realpath(__file__)),'../../../../py4j-java/bin')

def start_echo_server():
    subprocess.call(["java", "-cp", PY4J_JAVA_PATH, "py4j.EchoServer"])
    
    
def start_echo_server_process():
    # XXX DO NOT FORGET TO KILL THE PROCESS IF THE TEST DOES NOT SUCCEED
    p = Process(target=start_echo_server)
    p.start()
    return p

def start_example_server():
    subprocess.call(["java", "-Xmx512m", "-cp", PY4J_JAVA_PATH, "py4j.examples.ExampleApplication"])

def start_example_app_process():
    # XXX DO NOT FORGET TO KILL THE PROCESS IF THE TEST DOES NOT SUCCEED
    p = Process(target=start_example_server)
    p.start()
    return p

def get_test_socket():
    testSocket = socket(AF_INET, SOCK_STREAM)
    testSocket.connect(('localhost', TEST_PORT))
    return testSocket

def safe_shutdown(instance):
    try:
        instance.gateway.shutdown()
    except Exception:
        pass

class TestConnection(object):
    """Connection that does nothing. Useful for testing."""
    
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
        TestConnection.counter += 1
        if not command.startswith('m\nd\n'):
            self.last_message = command
        return self.return_message + str(TestConnection.counter)
    
class ProtocolTest(unittest.TestCase):
    
    def tearDown(self):
        # Safety check in case there was an exception...
        safe_shutdown(self)
    
    def testEscape(self):
        self.assertEqual("Hello\t\rWorld\n\\", unescape_new_line(escape_new_line("Hello\t\rWorld\n\\")))
        self.assertEqual(u"Hello\t\rWorld\n\\", unescape_new_line(escape_new_line(u"Hello\t\rWorld\n\\")))
        
    def testProtocolSend(self):
        testConnection = TestConnection()
        gateway = JavaGateway(testConnection, False)
        e = gateway.getExample()
        self.assertEqual('c\nt\ngetExample\ne\n', testConnection.last_message)
        e.method1(1, True, 'Hello\nWorld', e, None, 1.5)
        self.assertEqual('c\no0\nmethod1\ni1\nbTrue\nsHello\\nWorld\nro0\nn\nd1.5\ne\n', testConnection.last_message)
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
            
            self.gateway = JavaGateway(auto_field=True)
            ex = self.gateway.getNewExample()
            self.assertEqual('Hello World', ex.method3(1, True))
            self.assertEqual(123, ex.method3())
            self.assertAlmostEqual(1.25, ex.method3())
            self.assertTrue(ex.method2() == None)
            self.assertTrue(ex.method4())
            self.gateway.shutdown()
                        
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
        # Safety check in case there was an exception...
        safe_shutdown(self)
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
            
            self.gateway = JavaGateway(auto_field=True)
            ex = self.gateway.getNewExample()
            response = ex.method3(1, True)
            self.assertEqual('Hello World', response)
            ex2 = self.gateway.entry_point.getNewExample();
            response = ex2.method3(1, True)
            self.assertEqual('Hello World2', response)
            self.gateway.shutdown()
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
            
            self.gateway = JavaGateway(auto_field=True)
            ex = self.gateway.getNewExample()
                
            try:
                ex.method3(1, True)
                self.fail('Should have failed!')
            except Py4JError:
                self.assertTrue(True)
            self.gateway.shutdown()
        except Exception as e:
            print('Error has occurred', e)   
            self.fail('Problem occurred')
                

class CloseTest(unittest.TestCase):
    def testNoCallbackServer(self):
        # Test that the program can continue to move on and that no close is required.
        JavaGateway()
        self.assertTrue(True)

    def testCallbackServer(self):
        # A close is required to stop the thread.
        gateway = JavaGateway(start_callback_server=True)
        gateway.close()
        self.assertTrue(True)
        time.sleep(1)

class MethodTest(unittest.TestCase):
    def setUp(self):
        self.p = start_example_app_process()
        # This is to ensure that the server is started before connecting to it!
        time.sleep(1)
        self.gateway = JavaGateway()

    def tearDown(self):
        safe_shutdown(self)
        self.p.join()
        
    def testNoneArg(self):
        ex = self.gateway.getNewExample()
        try:
            ex.method2(None)
            ex2 = ex.method4(None)
            self.assertEquals(ex2.getField1(),3)
            self.assertEquals(2,ex.method7(None))
        except:
            print_exc()
            self.fail()
            
    def testUnicode(self):
        sb = self.gateway.jvm.java.lang.StringBuffer()
        sb.append(u'\r\n\tHello\r\n\t')
        self.assertEqual(u'\r\n\tHello\r\n\t', sb.toString())
    
    def testEscape(self):
        sb = self.gateway.jvm.java.lang.StringBuffer()
        sb.append('\r\n\tHello\r\n\t')
        self.assertEqual(u'\r\n\tHello\r\n\t', sb.toString())

class FieldTest(unittest.TestCase):
    def setUp(self):
        self.p = start_example_app_process()
        # This is to ensure that the server is started before connecting to it!
        time.sleep(1)

    def tearDown(self):
        safe_shutdown(self)
        self.p.join()
        
    def testAutoField(self):
        self.gateway = JavaGateway(auto_field=True)
        ex = self.gateway.getNewExample()
        self.assertEqual(ex.field10, 10)
        sb = ex.field20
        sb.append('Hello')
        self.assertEqual(u'Hello', sb.toString())
        self.assertTrue(ex.field21 == None)
    
    def testNoField(self):
        self.gateway = JavaGateway(auto_field=True)
        ex = self.gateway.getNewExample()
        member = ex.field50
        self.assertTrue(isinstance(member, JavaMember))
        
    def testNoAutoField(self):
        self.gateway = JavaGateway(auto_field=False)
        ex = self.gateway.getNewExample()
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
            
    def testSetField(self):
        self.gateway = JavaGateway(auto_field=False)
        ex = self.gateway.getNewExample()
        
        set_field(ex, 'field10',2334)
        self.assertEquals(get_field(ex,'field10'),2334)
        
        sb = self.gateway.jvm.java.lang.StringBuffer('Hello World!')
        set_field(ex, 'field21', sb)
        self.assertEquals(get_field(ex,'field21').toString(),u'Hello World!')
        
        try:
            set_field(ex,'field1',123)
            self.fail()
        except:
            self.assertTrue(True)
            
        
    def testGetMethod(self):
        # This is necessary if a field hides a method...
        self.gateway = JavaGateway()
        ex = self.gateway.getNewExample()
        self.assertEqual(1, get_method(ex, 'method1')())
        
class MemoryManagementText(unittest.TestCase):
    def setUp(self):
        self.p = start_example_app_process()
        # This is to ensure that the server is started before connecting to it!
        time.sleep(1)
        
    def tearDown(self):
        safe_shutdown(self)
        self.p.join()
        gc.collect()
        
    def testNoAttach(self):
        self.gateway = JavaGateway()
        gateway2 = JavaGateway()
        sb = self.gateway.jvm.java.lang.StringBuffer()
        sb.append('Hello World')
        self.gateway.shutdown()
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
        self.gateway = JavaGateway()
        sb = self.gateway.jvm.java.lang.StringBuffer()
        sb.append('Hello World')
        self.gateway.detach(sb)
        sb2 = self.gateway.jvm.java.lang.StringBuffer()
        sb2.append('Hello World')
        sb2._detach()
        gc.collect()
        self.assertEqual(len(ThreadSafeFinalizer.finalizers), 1)
        self.gateway.shutdown()

class TypeConversionTest(unittest.TestCase):
    def setUp(self):
        self.p = start_example_app_process()
        # This is to ensure that the server is started before connecting to it!
        time.sleep(1)
        self.gateway = JavaGateway()

    def tearDown(self):
        safe_shutdown(self)
        self.p.join()
        
    def testLongInt(self):
        ex = self.gateway.getNewExample()
        self.assertEqual(1,ex.method7(1234))
        self.assertEqual(4,ex.method7(2147483648))

class ExceptionTest(unittest.TestCase):
    def setUp(self):
        self.p = start_example_app_process()
        # This is to ensure that the server is started before connecting to it!
        time.sleep(1)
        self.gateway = JavaGateway()

    def tearDown(self):
        safe_shutdown(self)
        self.p.join()
        
    def testJavaError(self):
        try:
            self.gateway.jvm.Integer.valueOf('allo')
        except Py4JJavaError as e:
            self.assertEqual('java.lang.NumberFormatException',e.java_exception.getClass().getName())
            self.assertTrue(True)
        except Exception:
            self.fail()
            
    def testJavaConstructorError(self):
        try:
            self.gateway.jvm.Integer('allo')
        except Py4JJavaError as e:
            self.assertEqual('java.lang.NumberFormatException',e.java_exception.getClass().getName())
            self.assertTrue(True)
        except Exception:
            self.fail()
            
    def doError(self):
        id = ''
        try:
            self.gateway.jvm.Integer.valueOf('allo')
        except Py4JJavaError as e:
            id = e.java_exception._target_id
        return id
    
    def testJavaErrorGC(self):
        id = self.doError()
        java_object = JavaObject(id, self.gateway._gateway_client)
        try:
            # Should fail because it should have been garbage collected...
            java_object.getCause()
            self.fail()
        except Py4JError:
            self.assertTrue(True)
        
    def testReflectionError(self):
        try:
            self.gateway.jvm.Integer.valueOf2('allo')
        except Py4JJavaError:
            self.fail()
        except Py4JNetworkError:
            self.fail()
        except Py4JError:
            self.assertTrue(True)
            
    def testStrError(self):
        try:
            self.gateway.jvm.Integer.valueOf('allo')
        except Py4JJavaError as e:
            self.assertTrue(str(e).startswith('An error occurred while calling z:java.lang.Integer.valueOf.\n: java.lang.NumberFormatException:'))
        except Exception:
            self.fail()


class JVMTest(unittest.TestCase):
    def setUp(self):
        self.p = start_example_app_process()
        # This is to ensure that the server is started before connecting to it!
        time.sleep(1)
        self.gateway = JavaGateway()

    def tearDown(self):
        safe_shutdown(self)
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
        
    def testDefaultImports(self):
        self.assertTrue(self.gateway.jvm.System.currentTimeMillis() > 0)
        self.assertEqual(u'123', self.gateway.jvm.String.valueOf(123))
        
    def testNone(self):
        ex = self.gateway.entry_point.getNewExample()
        ex.method4(None)
        
    def testJVMView(self):
        newView = self.gateway.new_jvm_view('myjvm')
        time = newView.System.currentTimeMillis()
        self.assertTrue(time > 0)
        time = newView.java.lang.System.currentTimeMillis()
        self.assertTrue(time > 0)
        
    def testImport(self):
        newView = self.gateway.new_jvm_view('myjvm')
        java_import(self.gateway.jvm,'java.util.*')
        java_import(self.gateway.jvm,'java.io.File')
        self.assertTrue(self.gateway.jvm.ArrayList() is not None)
        self.assertTrue(self.gateway.jvm.File('hello.txt') is not None)
        try:
            newView.File('test.txt')
            self.fail('')
        except Exception:
            self.assertTrue(True)
        java_import(newView, 'java.util.HashSet')
        self.assertTrue(newView.HashSet() is not None)
        
        
class HelpTest(unittest.TestCase):
    
    def setUp(self):
        self.p = start_example_app_process()
        # This is to ensure that the server is started before connecting to it!
        time.sleep(1)
        self.gateway = JavaGateway()

    def tearDown(self):
        safe_shutdown(self)
        self.p.join()
        
    def testHelpObject(self):
        ex = self.gateway.getNewExample()
        help_page = self.gateway.help(ex, short_name=True, display=False)
        print(help_page)
        self.assertEqual(939, len(help_page))
        
    def testHelpObjectWithPattern(self):
        ex = self.gateway.getNewExample()
        help_page = self.gateway.help(ex, pattern='m*', short_name=True, display=False)
        print(help_page)
        self.assertEqual(644, len(help_page))
        
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
        gateway_client = GatewayClient()
        self.gateway = JavaGateway(gateway_client=gateway_client)

    def tearDown(self):
        safe_shutdown(self)
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
