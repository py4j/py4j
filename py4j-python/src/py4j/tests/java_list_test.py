'''
Created on Dec 17, 2009

@author: barthelemy
'''
from multiprocessing.process import Process
from py4j.java_gateway import JavaGateway
import logging
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

def get_list(count):
    return [unicode(i) for i in range(count)]

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
    
    def testJavaListProtocol(self):
        ex = self.gateway.getNewExample()
        pList = get_list(3)
        jList = ex.getList(3)
        pList.append(u'1')
        jList.append(u'1')
        pList.sort()
        jList.sort()
        self.assertEqual(len(pList), len(jList))
        self.assertEqual(str(pList), str(jList))
        pList.reverse()
        jList.reverse()
        self.assertEqual(len(pList), len(jList))
        self.assertEqual(str(pList), str(jList))
        self.assertEqual(pList.count(u'1'), jList.count(u'1'))
        self.assertEqual(pList.count(u'2'), jList.count(u'2'))
        self.assertEqual(pList.count(u'-1'), jList.count(u'-1'))
        
        # Hack because this is a list of strings
        self.assertEqual(max(pList), max(jList))
        self.assertEqual(min(pList), min(jList))
        
    def testJavaListProtocol2(self):
        ex = self.gateway.entry_point.getNewExample()
        pList = get_list(3)
        pList2 = get_list(4)
        jList = ex.getList(3)
        jList2 = ex.getList(4)
        
        pList3 = pList + pList2
        jList3 = jList + jList2
        self.assertEqual(len(pList3), len(jList3))
        self.assertEqual(str(pList3), str(jList3))
        
        pList3 = pList * 3
        jList3 = jList * 3
        self.assertEqual(len(pList3), len(jList3))
        self.assertEqual(str(pList3), str(jList3))
        
        pList3 = 3 * pList
        jList3 = 3 * jList
        self.assertEqual(len(pList3), len(jList3))
        self.assertEqual(str(pList3), str(jList3))
        
        pList3 = pList * 0
        jList3 = jList * 0
        self.assertEqual(len(pList3), len(jList3))
        self.assertEqual(str(pList3), str(jList3))
        
        pList += pList2
        jList += jList2
        self.assertEqual(len(pList), len(jList))
        self.assertEqual(str(pList), str(jList))
        
        pList2 *= 3
        jList2 *= 3
        self.assertEqual(len(pList2), len(jList2))
        self.assertEqual(str(pList2), str(jList2))
        
        pList2 *= -1
        jList2 *= -1
        self.assertEqual(len(pList2), len(jList2))
        self.assertEqual(str(pList2), str(jList2))
        
    
    def testJavaListGetSlice(self):
        ex = self.gateway.getNewExample()
        pList = get_list(5)
        jList = ex.getList(5)
        
        pSlice = pList[1:3]
        jSlice = jList[1:3]
        self.assertEqual(len(pSlice), len(jSlice))
        self.assertEqual(str(pSlice), str(jSlice))
        
        pSlice = pList[0:0]
        jSlice = jList[0:0]
        self.assertEqual(len(pSlice), len(jSlice))
        self.assertEqual(str(pSlice), str(jSlice))
        
        pSlice = pList[0:-2]
        jSlice = jList[0:-2]
        self.assertEqual(len(pSlice), len(jSlice))
        self.assertEqual(str(pSlice), str(jSlice))
        
    def testJavaListDelSlice(self):
        ex = self.gateway.getNewExample()
        pList = get_list(5)
        jList = ex.getList(5)
        
        del pList[1:3]
        del jList[1:3]
        self.assertEqual(len(pList), len(jList))
        self.assertEqual(str(pList), str(jList))
        
    def testJavaListSetSlice(self):
        ex = self.gateway.getNewExample()
        pList = get_list(6)
        jList = ex.getList(6)
        tList = [u'500',u'600']
        
        pList[0:0] = tList
        jList[0:0] = tList
        self.assertEqual(len(pList), len(jList))
        self.assertEqual(str(pList), str(jList))
        
        pList[1:2] = tList
        jList[1:2] = tList
        self.assertEqual(len(pList), len(jList))
        self.assertEqual(str(pList), str(jList))
        
        pList[3:5] = tList
        jList[3:5] = tList
        self.assertEqual(len(pList), len(jList))
        self.assertEqual(str(pList), str(jList))
        
        pList[1:5:2] = tList
        jList[1:5:2] = tList
        self.assertEqual(len(pList), len(jList))
        self.assertEqual(str(pList), str(jList))
        
        pList[0:4] = tList
        jList[0:4] = tList
        self.assertEqual(len(pList), len(jList))
        self.assertEqual(str(pList), str(jList))
        
        pList = get_list(6)
        jList = ex.getList(6)
        try:
            pList[0:6:2] = tList
            self.fail('Should have failed')
        except ValueError:
            self.assertTrue(True)
        try:
            jList[0:6:2] = tList
            self.fail('Should have failed')
        except ValueError:
            self.assertTrue(True)
        
        self.assertEqual(len(pList), len(jList))
        self.assertEqual(str(pList), str(jList))
        
        pList = get_list(6)
        jList = ex.getList(6)
        
        pList[100:100] = tList
        jList[100:100] = tList
        self.assertEqual(len(pList), len(jList))
        self.assertEqual(str(pList), str(jList))
        
        pList[1000:10000] = tList
        jList[1000:10000] = tList
        self.assertEqual(len(pList), len(jList))
        self.assertEqual(str(pList), str(jList))
        
    def testJavaList(self):
        ex = self.gateway.getNewExample()
        pList = get_list(3)
        jList = ex.getList(3)
        pList2 = get_list(3)
        jList2 = ex.getList(3)
        
        # Lists are not "hashable" in Python. Too bad.
        #self.assertEqual(hash(pList),hash(pList2))
        self.assertEqual(hash(jList),hash(jList2))
        
        self.assertEqual(len(pList), len(jList))
        self.assertEqual(str(pList), str(jList))
        self.assertEqual(pList, pList2)
        self.assertEqual(jList, jList2)
        pList.append(u'4')
        jList.append(u'4')
        self.assertEqual(len(pList), len(jList))
        self.assertEqual(str(pList), str(jList))
        
        self.assertEqual(pList[0], jList[0])
        self.assertEqual(pList[3], jList[3])
        
        pList.extend(pList2)
        jList.extend(jList2)
        self.assertEqual(len(pList), len(jList))
        self.assertEqual(str(pList), str(jList))
        
        self.assertEqual(u'1' in pList, u'1' in jList)
        self.assertEqual(u'500' in pList, u'500' in jList)
        
        pList[0] = u'100'
        jList[0] = u'100'
        pList[3] = u'150'
        jList[3] = u'150'
        pList[-1] = u'200'
        jList[-1] = u'200'
        self.assertEqual(len(pList), len(jList))
        self.assertEqual(str(pList), str(jList))
        
        pList.insert(0,u'100')
        jList.insert(0,u'100')
        pList.insert(3,u'150')
        jList.insert(3,u'150')
        pList.insert(-1,u'200')
        jList.insert(-1,u'200')
        pList.insert(len(pList),u'300')
        jList.insert(len(pList),u'300')
        pList.insert(300,u'1500')
        jList.insert(300,u'1500')
        self.assertEqual(len(pList), len(jList))
        self.assertEqual(str(pList), str(jList))
        
        self.assertEqual(pList.pop(),jList.pop())
        self.assertEqual(len(pList), len(jList))
        self.assertEqual(str(pList), str(jList))
        
        self.assertEqual(pList.pop(-1),jList.pop(-1))
        self.assertEqual(len(pList), len(jList))
        self.assertEqual(str(pList), str(jList))
        
        self.assertEqual(pList.pop(2),jList.pop(2))
        self.assertEqual(len(pList), len(jList))
        self.assertEqual(str(pList), str(jList))
        
        del pList[0]
        del jList[0]
        del pList[-1]
        del jList[-1]
        del pList[1]
        del jList[1]
        self.assertEqual(len(pList), len(jList))
        self.assertEqual(str(pList), str(jList))
        
        pList.append(u'700')
        jList.append(u'700')
        pList.insert(0,u'700')
        jList.insert(0,u'700')
        
        pList.remove(u'700')
        jList.remove(u'700')
        self.assertEqual(len(pList), len(jList))
        self.assertEqual(str(pList), str(jList))
        
        # Catch here: Java has a remote(int) method that is not directly supported in Python.
        # This could get tricky with list of integers... Needs to think about that.
        jList.remove(0)
        del pList[0]
        self.assertEqual(len(pList), len(jList))
        self.assertEqual(str(pList), str(jList))
        
        try:
            jList[15]
            self.fail('Should Fail!')
        except IndexError:
            self.assertTrue(True)
        
    def testBinaryOp(self):
        ex = self.gateway.getNewExample()
        pList = get_list(3)
        jList = ex.getList(3)
        jList2 = ex.getList(4)
        self.assertTrue(jList == jList)
        self.assertTrue(jList != jList2)
        #self.assertTrue(jList < jList2)
        self.assertTrue(jList != pList)
        #self.assertTrue(jList == pList)
#        self.assertTrue(jList2 != pList)
#        self.assertTrue(jList2 > pList)
        
        


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testJavaList']
    unittest.main()
