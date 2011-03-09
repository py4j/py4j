#coding: utf-8
'''
Compatibility functions for unified behavior between Python 2.x and 3.x.

:author: Alex Grönholm
'''
import sys
import inspect

if sys.version_info[0] < 3:
    items = lambda d: d.items()
    iteritems = lambda d: d.iteritems()
    next = lambda x: x.next()
    range = xrange
    long = long
    basestring = basestring
    unicode = unicode
else:
    items = lambda d: list(d.items())
    iteritems = lambda d: d.items()
    next = next
    range = range
    long = int
    basestring = str
    unicode = str

if hasattr(inspect, 'getattr_static'):
    hasattr2 = lambda obj, attr: bool(inspect.getattr_static(obj, attr, False))
else:
    hasattr2 = hasattr 
