Frequently Asked Questions
==========================

.. contents:: Summary
   :backlinks: entry
   :local:

How to turn logging on/off?
---------------------------

Logging is turned off by default. In Java, simply call ``GatewayServer.turnLoggingOn()`` or
``GatewayServer.turnLoggingOff()``. Py4J-java uses the ``java.util.logging`` framework. To get fined-grained control
over the logging behavior, just obtain a Logger instance by calling ``Logger.getLogger("py4j")``. You can also look at
the `Java Logging Overview <http://java.sun.com/javase/6/docs/technotes/guides/logging/overview.html>`_ for more
information on this framework.

In Python, logging can be enabled this way:

::

  logger = logging.getLogger("py4j")
  logger.setLevel(logging.DEBUG)
  logger.addHandler(logging.StreamHandler())

**Hint:** you can enable/disable Java logging from Python too:

::

  gateway.jvm.py4j.GatewayServer.turnLoggingOn()


How to call a constructor?
--------------------------

Use the ``jvm`` member of a gateway followed by the class's fully qualified name:

::

  >>> gateway = JavaGateway()
  >>> java_list = gateway.jvm.java.util.ArrayList()


How to call a static method?
----------------------------

Use the ``jvm`` member of a gateway followed by the fully qualified name of the method's class. Do the same for static
fields.

::

  >>> gateway = JavaGateway()
  >>> timestamp = gateway.jvm.java.lang.System.currentTimeMillis()


How to access a field?
----------------------

Use the :ref:`get_field <api_functions_get_field>` function:

::

  >>> field_value = py4j.java_gateway.get_field(object,'public_field')
  
  
Or you can also set the :ref:`auto_field <api_javagateway>` parameter to `True` when you create the gateway:

::

  >>> gateway = JavaGateway(auto_field=True)
  >>> object = gateway.entry_point.getObject()
  >>> field_value = object.public_field


How to create an array?
-----------------------

Use the :func:`new_array <py4j.java_gateway.JavaGateway.new_array>` function:

::

   >>> gateway = JavaGateway()
   >>> string_class = gateway.jvm.java.lang.String
   >>> string_array = gateway.new_array(string_class, 3, 5)
   >>> string_array[2][4] = 'Hello World'
   >>> string_array[2][4]
   u'Hello World'
   >>> string_array[2][3] is None
   True
   >>> string_array[3][1]
   Traceback (most recent call last):
   ...
   IndexError: list index out of range


What ports are used by Py4J?
----------------------------

Py4J by default uses the TCP port 25333 to communicate from Python to Java and TCP port 25334 to communicate from Java
to Python. It also uses TCP port 25332 for a test echo server (only used by unit tests).

These ports can be customized when creating a :class:`JavaGateway <py4j.java_gateway.JavaGateway>` on the Python side
and a GatewayServer on the Java side.


What is the memory model of Py4J?
---------------------------------

**Java objects sent to the Python side**

Every time an object is returned through a gateway, a reference to the object is kept on the Java side (in the Gateway
class). Once the object is garbage collected on the Python VM (reference count = 0), the reference is removed on the
Java VM: if this was the last reference, the object will likely be garbage collected too. When a gateway is shut down,
the remaining references are also removed on the Java VM.

Because Java objects on the Python side are involved in a circular reference (:class:`JavaObject
<py4j.java_gateway.JavaObject>` and :class:`JavaMember <py4j.java_gateway.JavaMember>` reference each other), these
objects are not immediately garbage collected once the last reference to the object is removed (but they are guaranteed
to be eventually collected **if the Python garbage collector runs before the Python program exits**).

In doubt, users can always call the :func:`detach <py4j.java_gateway.JavaGateway.detach>` function on the Python
gateway.

**Python objects sent to the Java side (callback)**

Every time a Python object is sent to the Java side, a reference to this object is kept on the Python side (by a
:class:`PythonProxyPool <py4j.java_callback.PythonProxyPool>`). Once a python object is garbage collected on the Java
side, a message is sent to the Python side to remove the reference to the Python object. When a gateway is shut down,
the remaining references are removed from the Python VM.

Unfortunately, there is no guarantee that the garbage collection message will ever be sent to the Python side (it
usually works on Sun/Oracle VM). It might thus be necessary to manually remove the reference to the Python objects. Some
helper functions will be developed in the future, but it is unlikely that garbage collection will be guarenteed because
of the specification of Java finalizers (which is surprisingly worse than Python finalizer strategies).

Is Py4J thread-safe?
--------------------

The Java component of Py4J is thread-safe, but multiple threads could access the same entry point. Each gateway
connection is executed in is own thread (e.g., each time a Python thread calls a Java method) so if multiple Python
threads/processes/programs are connected to the same gateway, i.e., the same address and the same port, multiple threads
may call the entry point's methods concurrently.

In the following example, two threads are accessing the same entry point. If `gateway1` and `gateway2` were created in 
separate processes, `method1` would be accessed concurrently.

::
  
  # ... in Thread One
  gateway1 = JavaGateway() # Thread One is accessing the JVM.
  gateway1.entry_point.method1() # Thread One is calling method1
  # ... in Thread Two
  gateway2 = JavaGateway() # Thread Two is accessing the JVM.
  gateway2.entry_point.method1() # Thread Two is calling method1


The Python component of Py4J is also thread-safe, except the :func:`close <py4j.java_gateway.CommChannelFactory.close>`
function of a :class:`CommChannelFactory <py4j.java_gateway.CommChannelFactory>`, which must not be accessed
concurrently with other methods to ensure that all communication channels are closed. This is a trade-off to avoid
accessing a lock every time a Java method is called on the Python side. This will only be a problem if attempting to
shut down or close a JavaGateway while calling Java methods on the Python side.

I found a bug, how do I report it?
----------------------------------

Please report bugs on our `issue tracker <https://sourceforge.net/apps/trac/py4j/newticket>`_.

How can I contribute?
---------------------

There are tons of ways to contribute.

* Bug reports
* How-tos
* Documentation patch
* Code patch
* Art and Logos

In case of doubt, do not hesitate to contact me.