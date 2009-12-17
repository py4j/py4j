'''
Created on Dec 17, 2009

@author: barthelemy
'''
from multiprocessing.process import Process
from py4j.java_gateway import JavaGateway
import subprocess
import time
import unittest


def start_echo_server():
    subprocess.call(["java","-cp", "../../../py4j/bin/","py4j.examples.ExampleApplication"])
    
    
def start_echo_server_process():
    # XXX DO NOT FORGET TO KILL THE PROCESS IF THE TEST DOES NOT SUCCEED
    p = Process(target=start_echo_server)
#    p.daemon = True
    p.start()
    return p

def get_list(count):
    return [unicode(i) for i in range(count)]

class Test(unittest.TestCase):

    def testJavaList(self):
        p = start_echo_server_process()
        time.sleep(1)
        gateway = JavaGateway()
        ex = gateway.getNewExample()
        pList = get_list(3)
        jList = ex.getList(3)
        
        self.assertEqual(len(pList),len(jList))
        self.assertEqual(str(pList),str(jList))
        gateway.comm_channel.shutdown()
        p.terminate()
        


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testJavaList']
    unittest.main()