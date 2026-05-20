"""
Compatibility shims left over from py4j's Python 2 / 3 dual-support era.

Python 2 support has been removed (py4j requires Python 3.9+). The
names below are kept solely so that downstream code that still imports
from this module (``from py4j.compat import unicode``, etc.) continues
to work.

New code inside py4j should use the Python 3 built-ins directly:

  - ``unicode``      -> ``str``
  - ``basestring``   -> ``str``
  - ``long``         -> ``int``
  - ``range``        -> built-in ``range``
  - ``unichr``       -> ``chr``
  - ``bytestr``      -> ``bytes``
  - ``bytearray2``   -> ``bytes`` (or ``bytearray``; alias kept as ``bytes``)
  - ``iteritems(d)`` -> ``d.items()``
  - ``items(d)``     -> ``list(d.items())``
  - ``next(x)``      -> built-in ``next(x)``
  - ``Queue``        -> ``from queue import Queue``
  - ``Empty``        -> ``from queue import Empty``
  - ``CompatThread`` -> ``threading.Thread`` (already supports ``daemon``)

Only ``hasattr2`` has no Python-3-builtin replacement: it uses
``inspect.getattr_static`` to test for an attribute without triggering
descriptor / ``__getattr__`` side effects, which is genuinely
different behavior from the built-in ``hasattr``.

This module may be removed in a future major release; downstream code
should migrate off the imports above.

:author: Alex Grönholm
"""
import inspect
import sys
from threading import Thread
from queue import Queue as _StdQueue, Empty as _StdEmpty


version_info = sys.version_info


def items(d):
    return list(d.items())


def iteritems(d):
    return d.items()


# Built-in passthroughs — kept as module attributes so existing
# ``from py4j.compat import range, unicode, ...`` imports still work.
range = range
long = int
basestring = str
unicode = str
bytearray2 = bytes
unichr = chr
bytestr = bytes


def tobytestr(s):
    return bytes(s, "ascii")


def isbytestr(s):
    return isinstance(s, bytes)


def ispython3bytestr(s):
    return isinstance(s, bytes)


def isbytearray(s):
    return isinstance(s, bytearray)


def bytetoint(b):
    return b


def bytetostr(b):
    return str(b, encoding="ascii")


def strtobyte(s):
    return bytes(s, encoding="ascii")


Queue = _StdQueue
Empty = _StdEmpty


if hasattr(inspect, "getattr_static"):
    def hasattr2(obj, attr):
        return bool(inspect.getattr_static(obj, attr, False))
else:
    hasattr2 = hasattr


# Python 3's ``threading.Thread`` accepts the ``daemon`` kwarg natively,
# so this is just a passthrough. Kept as a name for external callers
# that imported ``CompatThread`` from this module.
CompatThread = Thread
