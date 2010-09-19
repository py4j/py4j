'''
Created on Mar 26, 2010

@author: Barthelemy Dagenais
'''
from multiprocessing.process import Process
from py4j.java_gateway import JavaGateway
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

class Test(unittest.TestCase):

    def setUp(self):
#        logger = logging.getLogger("py4j")
#        logger.setLevel(logging.DEBUG)
#        logger.addHandler(logging.StreamHandler())
        self.p = start_example_app_process()
        time.sleep(0.5)
        self.gateway = JavaGateway()
        
    def tearDown(self):
        self.p.terminate()
        self.gateway.shutdown()
        
        time.sleep(0.5)
    
    def testTreeSet(self):
#        self.gateway.jvm.py4j.GatewayServer.turnLoggingOn()
        set1 = set()
        set2 = self.gateway.jvm.java.util.TreeSet()
        set1.add(u'a')
        set2.add(u'a')
        self.assertEqual(len(set1),len(set2))
        self.assertEqual(u'a' in set1, u'a' in set2)
        self.assertEqual(repr(set1), repr(set2))
        
        set1.add(u'b')
        set2.add(u'b')
        self.assertEqual(len(set1),len(set2))
        self.assertEqual(u'a' in set1, u'a' in set2)
        self.assertEqual(u'b' in set1, u'b' in set2)
        self.assertEqual(repr(set1), repr(set2))
        
        set1.remove(u'a')
        set2.remove(u'a')
        self.assertEqual(len(set1),len(set2))
        self.assertEqual(u'a' in set1, u'a' in set2)
        self.assertEqual(u'b' in set1, u'b' in set2)
        self.assertEqual(repr(set1), repr(set2))
        
        set1.clear()
        set2.clear()
        self.assertEqual(len(set1),len(set2))
        self.assertEqual(u'a' in set1, u'a' in set2)
        self.assertEqual(u'b' in set1, u'b' in set2)
        self.assertEqual(repr(set1), repr(set2))
    
    def testHashSet(self):
        set1 = set()
        set2 = self.gateway.jvm.java.util.HashSet()
        set1.add(u'a')
        set2.add(u'a')
        set1.add(1)
        set2.add(1)
        set1.add(u'b')
        set2.add(u'b')
        self.assertEqual(len(set1),len(set2))
        self.assertEqual(u'a' in set1, u'a' in set2)
        self.assertEqual(u'b' in set1, u'b' in set2)
        self.assertEqual(1 in set1, 1 in set2)
        
        set1.remove(1)
        set2.remove(1)
        self.assertEqual(len(set1),len(set2))
        self.assertEqual(u'a' in set1, u'a' in set2)
        self.assertEqual(u'b' in set1, u'b' in set2)
        self.assertEqual(1 in set1, 1 in set2)
        
        set1.clear()
        set2.clear()
        self.assertEqual(len(set1),len(set2))
        self.assertEqual(u'a' in set1, u'a' in set2)
        self.assertEqual(u'b' in set1, u'b' in set2)
        self.assertEqual(1 in set1, 1 in set2)
        
        
        
if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()