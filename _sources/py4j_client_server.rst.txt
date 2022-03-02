:mod:`py4j.clientserver` --- Py4J Single Threading Model Implementation
=======================================================================

.. module:: py4j.clientserver
  :synopsis: Py4J single threading model implementation
.. moduleauthor:: Barthelemy Dagenais <barthelemy@infobart.com>

The :mod:`py4j.clientserver` module defines an implementation of Python Server
and Java client that ensures that commands started from a Python or Java thread
are always executed on the same Java or Python thread.

For example, if a command to Python is sent from Java UI thread and the Python
code calls some Java code, the Java code will be executed in the UI thread.

Py4J users are expected to only use explicitly :class:`ClientServer
<py4j.clientserver.ClientServer>` and optionally, :class:`JavaParameters
<py4j.clientserver.JavaParameters>` and :class:`PythonParameters
<py4j.clientserver.PythonParameters>`.  The other module members are documented
to support the extension of Py4J.

.. _api_clientserver:

ClientServer
------------

.. autoclass:: py4j.clientserver.ClientServer
   :members:
   :undoc-members:


.. _api_clientserver_examples:

Examples
^^^^^^^^

Using the ``jvm`` property:
::

  >>> clientserver = ClientServer()
  >>> l = clientserver.jvm.java.util.ArrayList()
  >>> l.append(10)
  >>> l.append(1)
  >>> jvm.java.util.Collections.sort(l)
  >>> l
  [1, 10]

The :class:`ClientServer <py4j.clientserver.ClientServer>` class is a subclass
of :class:`JavaGateway <py4j.java_gateway.JavaGateway>` is fully compatible
with all examples and code written for a `JavaGateway`.`


.. _api_javaparameters:

JavaParameters
--------------

.. autoclass:: py4j.clientserver.JavaParameters
   :members:
   :undoc-members:


.. _api_pythonparameters:

PythonParameters
----------------

.. autoclass:: py4j.clientserver.PythonParameters
   :members:
   :undoc-members:


.. _api_javaclient:

JavaClient
----------

.. autoclass:: py4j.clientserver.JavaClient
   :members:
   :undoc-members:


.. _api_pythonserver:

PythonServer
------------

.. autoclass:: py4j.clientserver.PythonServer
   :members:
   :undoc-members:


.. _api_clientserverconnection:

ClientServerConnection
----------------------

.. autoclass:: py4j.clientserver.ClientServerConnection
   :members:
   :undoc-members:
