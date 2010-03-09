# -*- coding: UTF-8 -*-
"""Module that defines a Finalizer class responsible for registering and cleaning finalizer

Created on Mar 7, 2010

@author: Barthelemy Dagenais
"""

from threading import RLock

class ThreadSafeFinalizer(object):
    finalizers = {}
    lock = RLock()
    
    
    @classmethod
    def add_finalizer(cls, id, weak_ref):
        with cls.lock:
            cls.finalizers[id] = weak_ref
        
    @classmethod
    def remove_finalizer(cls, id):
        with cls.lock:
            cls.finalizers.pop(id,None)
        
    @classmethod
    def clean_finalizers(cls, clean_all = False):
        with cls.lock:
            if clean_all:
                cls.finalizers.clear()
            else:
                for id,ref in cls.finalizers.items():
                    if ref() is None:
                        cls.finalizers.pop(id,None)
            
            

class Finalizer(object):
    finalizers = {}
    
    @classmethod
    def add_finalizer(cls, id, weak_ref):
        cls.finalizers[id] = weak_ref
        
    @classmethod
    def remove_finalizer(cls, id):
        cls.finalizers.pop(id,None)
        
    @classmethod
    def clean_finalizers(cls, clean_all = False):
        if clean_all:
            cls.finalizers.clear()
        else:
            for id,ref in cls.finalizers.items():
                if ref() is None:
                    cls.finalizers.pop(id,None)
    

def clean_finalizers(clean_all = False):
    ThreadSafeFinalizer.clean_finalizers(clean_all)
    Finalizer.clean_finalizers(clean_all)