Py4J Python API
================

.. module:: py4j.java_gateway
  :synopsis: Main Py4J Python module.
.. moduleauthor:: Barthelemy Dagenais <barthe@users.sourceforge.net>

Overview
--------

Using Py4J is usually as simple as creating a :ref:`JavaGateway <api_javagateway>` object:

::
  
  java_gateway = JavaGateway()
  # you are now connected to the JVM 
  # and you can call any method defined on the Java side.

You can still customize and extend Py4J in many ways (e.g., you can choose the port to which you want to connect), so
here are the classes you are the most likely to interact with:

.. autoclass:: py4j.java_gateway.JavaGateway

.. autoclass:: py4j.java_gateway.CommChannel

.. autoclass:: py4j.java_gateway.Py4JError

.. autoclass:: py4j.java_gateway.JavaObject

.. autoclass:: py4j.java_gateway.JavaMember

.. autoclass:: py4j.java_gateway.JavaList


.. _api_javagateway:

JavaGateway
-----------

.. autoclass:: py4j.java_gateway.JavaGateway
   :members:
   :undoc-members:

.. _api_commchannel:

Examples
^^^^^^^^

::
  
  javaGateway = JavaGateway(auto_start=False)
  javaGateway.comm_channel.start()
  # ... to some work here
  javaGateway.comm_channel.stop()

CommChannel
-----------

.. autoclass:: py4j.java_gateway.CommChannel
   :members:
   :undoc-members:



Examples
^^^^^^^^

::

  TBD

.. _api_py4jerror:

Py4JError
-----------

.. autoclass:: py4j.java_gateway.Py4JError
   :members:
   :undoc-members:

.. _api_javaobject:

Examples
^^^^^^^^

JavaObject
-----------

.. autoclass:: py4j.java_gateway.JavaObject
   :members:
   :undoc-members:

.. _api_javamember:

JavaMember
-----------

.. autoclass:: py4j.java_gateway.JavaMember
   :members:
   :undoc-members:

.. _api_javalist:

JavaList
--------

.. autoclass:: py4j.java_gateway.JavaList
   :members:
   :undoc-members:
   
