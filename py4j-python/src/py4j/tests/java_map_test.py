'''
Created on Feb 5, 2010

@author: barthelemy
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

def get_map():
    return {"a":1,"b":2.0,"c":"z"}

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
    
    def equal_maps(self, m1, m2):
        if len(m1) == len(m2):
            equal = True
            for k in m1:
                equal = m1[k] == m2[k]
                if not equal:
                    break
            return equal
        else:
            return False
    
    def testMap(self):
        dp0 = {}
        dp = get_map()
        dj = self.gateway.jvm.java.util.HashMap()
        self.equal_maps(dj,dp0)
        dj["a"] = 1
        dj["b"] = 2.0
        dj["c"] = "z"
        self.equal_maps(dj,dp)
        
        del(dj["a"])
        del(dp["a"])
        
        dj2 = self.gateway.jvm.java.util.HashMap()
        dj2["b"] = 2.0
        dj2["c"] = "z"
        
        dj3 = self.gateway.jvm.java.util.HashMap()
        dj3["a"] = 1
        dj3["b"] = 2.0
        dj3["c"] = "z"
        
        self.equal_maps(dj,dp)
        self.assertTrue(dj == dj)
        self.assertTrue(dj == dj2)
        self.assertTrue(dj < dj3)
        self.assertTrue(dj != dp)
        
        dps = {1:1, 2:2}
        djs = self.gateway.jvm.java.util.HashMap()
        djs[1] = 1
        djs[2] = 2
        self.assertEqual(str(djs),str(dps))
        

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()