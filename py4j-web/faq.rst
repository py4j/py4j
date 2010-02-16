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


What is the memory model of Py4J?
---------------------------------

Every time an object is returned through a gateway, a reference to the object is kept on the Java side. Once the object
is garbage collected on the Python VM (reference count = 0), the reference is removed on the Java VM: if this was the
last reference, the object will likely be garbage collected too. When a gateway is closed or shut down, the remaining
references are also removed on the Java VM.


Is Py4J thread-safe?
--------------------

The Java component of Py4J is thread-safe, but multiple threads could access the same entry point. Each gateway
connection is executed in is own thread (e.g., each time ``JavaGateway()`` is called in Python) so if multiple Python
programs are connected to the same gateway, i.e., the same address and the same port, multiple threads
may call the entry point's methods concurrently.

In the following example, two threads are accessing the same entry point. If `gateway1` and `gateway2` were created in 
separate processes, `method1` would be accessed concurrently.

::

  gateway1 = JavaGateway() # Thread One is accessing the JVM.
  gateway2 = JavaGateway() # Thread Two is accessing the JVM.
  gateway1.entry_point.method1() # Thread One is calling method1
  gateway2.entry_point.method1() # Thread Two is calling method1


The Python component of Py4J is not thread-safe by default to optimize the performance. Only one thread should access
the same JavaGateway instance. If multiple threads must access the same JavaGateway instance, a communication channel
with thread_safe=True should be created:

::
  comm_channel = CommChannel(thread_safe=True)
  gateway = JavaGateway(comm_channel=comm_channel)
  # gateway can now be accessed by multiple threads.


