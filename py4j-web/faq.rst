Frequently Asked Questions
==========================

.. contents:: Summary
   :backlinks: entry
   :local:

How to turn logging on/off?
---------------------------

In Java, simply call ``GatewayServer.turnLoggingOn()`` or ``GatewayServer.turnLoggingOn()``. Py4J-java uses the
``java.util.logging`` framework. To get fined-grained control over the logging behavior, just obtain a Logger instance
by calling ``Logger.getLogger("py4j")``. You can also look at the `Java Logging Overview <http://java.sun.com/javase/6/docs/technotes/guides/logging/overview.html>`_ 
for more information on this framework.

In Python, logging can be enabled this way:

::

  logger = logging.getLogger("py4j")
  logger.setLevel(logging.DEBUG)
  logger.addHandler(logging.StreamHandler())


How to prevent memory leak?
---------------------------

Every time that an object is returned by the Java Gateway, it is cached in a map by the gateway. If the same object is
returned multiple times, it might be cached under different names. As long as the gateway is not shut down on the Java
side, the objects are still referenced by the cache and will **never** be garbage collected. This is to ensure that a
Python program does not access a dead Java object and that multiple Python programs connected to the same gateway can
access the same objects.

You can manually interact with the cache by calling the protected method `DefaultGateway.getBindings() <_static/javadoc/py4j/DefaultGateway.html#getBindings()>`_ 
from your custom Gateway implementation. We plan to implement a few methods to make cache management easier and we might
change the main cache management strategy in the future.


Is Py4J thread-safe?
--------------------

The short answer is: it's complicated. Multiple Python programs can connect to the same Java gateway. When this happens, 
each connection is executed by its own Java thread, so each thread can access the Gateway (and any Java object in the 
JVM) concurrently.

As of version 0.1., we recommend that you serialize the accesses to the JVM by extending the `DefaultSynchronizedGateway <_static/javadoc/index.html?py4j/DefaultSynchronizedGateway.html>`_
instead of the `DefaultGateway <_static/javadoc/index.html?py4j/DefaultGateway.html>`_. This will ensure that only one 
Java method is executed at a time.

When we will implement a better cache management strategy and dynamic invocation strategy (i.e., how Java methods are
called), we will make Py4J completely thread-safe without requiring you to serialize the access to the JVM. Obviously,
if your application is not thread-safe, but want multiple Python programs to access it concurrently, you will still need
to extend `DefaultSynchronizedGateway <_static/javadoc/index.html?py4j/DefaultSynchronizedGateway.html>`_. 
