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

Use the :func:`get_field <py4j.java_gateway.get_field>` function:

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

See :ref:`Py4J Threading Model <adv_threading>` for more details.

I found a bug, how do I report it?
----------------------------------

Please report bugs on our `issue tracker <https://sourceforge.net/apps/trac/py4j/newticket>`_.

How can I contribute?
---------------------

There are many ways to contribute to Py4J:

* **Found a bug or have a feature request?** Fill a detailed `issue report
  <https://sourceforge.net/apps/trac/py4j/newticket>`_.
* **Have a tip or trick to share with fellow Py4J users?** Add a `how to
  <https://sourceforge.net/apps/trac/py4j/wiki/HowTos>`_ on the wiki.
* **Found a typo or have a better way to clarify the documentation?** Write a comment at the bottom of documentation
  the 
  page, send a patch on the `mailing list <http://sourceforge.net/mailarchive/forum.php?forum_name=py4j-users>`_, or 
  fill a `bug report <https://sourceforge.net/apps/trac/py4j/newticket>`_. The source of each documentation page is 
  accessible in the sidebar. We use `ReStructuredText <http://docutils.sourceforge.net/docs/user/rst/quickstart.html>`_
* **Good at writing Python or Java?** Good news, we could use some help, especially in the Python department! 
  You can either contribute a code patch through the `mailing list
  <http://sourceforge.net/mailarchive/forum.php?forum_name=py4j-users>`_ by adding a feature or just addressing an
  `open issue <https://sourceforge.net/apps/trac/py4j/report/1>`_.
* **Feeling artsy?** We need a logo. Hop on the `mailing list
  <http://sourceforge.net/mailarchive/forum.php?forum_name=py4j-users>`_.

In case of doubt, do not hesitate to contact the founder of the project, `Barthelemy
<mailto:barthe@users.sourceforge.net>`_.