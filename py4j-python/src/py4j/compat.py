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
    bytearray2 = bytearray
    unichr = unichr
    bytestr = str
    tobytestr = str
    isbytestr = lambda s: isinstance(s, str)
    isbytearray = lambda s: isinstance(s, bytearray)
else:
    items = lambda d: list(d.items())
    iteritems = lambda d: d.items()
    next = next
    range = range
    long = int
    basestring = str
    unicode = str
    bytearray2 = bytes
    unichr = chr
    bytestr = bytes
    tobytestr = lambda s: bytes(s, 'ascii')
    isbytestr = lambda s: False
    isbytearray = lambda s: isinstance(s, bytearray) or isinstance(s, bytes)

if hasattr(inspect, 'getattr_static'):
    hasattr2 = lambda obj, attr: bool(inspect.getattr_static(obj, attr, False))
else:
    hasattr2 = hasattr
