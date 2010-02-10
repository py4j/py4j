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


What is the memory model of Py4J?
---------------------------------

Everytime an object is returned through a gateway, a reference to the object is kept on the Java side. Once the object
is garbage collected on the Python VM (reference count = 0), the reference is removed on the Java VM: if this was the
last reference, the object will likely be garbage collected too. When a gateway is closed or shut down, the remaining
references are also removed on the Java VM.


Is Py4J thread-safe?
--------------------

Py4J itself is thread-safe, but multiple threads could access the same entry point. Each gateway connection is executed
in is own thread (e.g., each time ``JavaGateway()`` is called in Python) so if multiple Python programs (or processes)
access the same entry point, mutiple threads may call the entry point's methods concurrently.
