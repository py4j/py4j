'''
Created on Mar 7, 2010

@author: barthelemy
'''
from py4j.finalizer import ThreadSafeFinalizer
from weakref import ref
import gc
import weakref

finalizers = []

def del_A(name):
    print('An A deleted:' + name)

class A(object):
    def __init__(self, name, finalizers):
        print('A created')
        self.name = name
        finalizers.append(weakref.ref(self, lambda wr, n = self.name: del_A(n)))

class B(object):
    def __init__(self):
        print('B created')

def do_work(finalizers):
    a = A('a1', finalizers)
    b = B()
    a.others = []
    a.others.append(b)
    b.container = a

def deleted(accumulator,id):
    print(id)
    accumulator.acc += 1

class Accumulator(object):
    def __init__(self):
        self.acc = 0
    
class JavaObjecTest(object):
    def __init__(self,id,acc):
        self.id = id
        self.acc = acc
        self.methods = []
        finalizers.append(ref(self,lambda wr, i = self.id, a = self.acc : deleted(a,i)))
        
class JavaMemberTest(object):
    def __init__(self, name, container):
        self.name = name
        self.container = container

def work_circ(acc):
    jobj = JavaObjecTest(1,acc)
    jmem1 = JavaMemberTest('append',jobj)
    jobj.methods.append(jmem1)
    print('Hello!')
    
def indirect(acc):
    work_circ(acc)
    gc.collect()
        
if __name__ == '__main__':
#    finalizers = []
#    do_work(finalizers)
    acc = Accumulator()
    indirect(acc)
    print('Stop')
    print(acc.acc)