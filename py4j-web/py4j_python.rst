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
  # ... do some work here
  javaGateway.comm_channel.stop()

CommChannel
-----------

.. autoclass:: py4j.java_gateway.CommChannel
   :members:
   :undoc-members:

   .. automethod:: __del__()



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


Examples
^^^^^^^^

::

  TBD

.. _api_javaobject:

JavaObject
-----------

.. autoclass:: py4j.java_gateway.JavaObject
   :members:
   :undoc-members:

.. _api_javamember:

Examples
^^^^^^^^

::

  TBD

JavaMember
-----------

.. autoclass:: py4j.java_gateway.JavaMember
   :members:
   :undoc-members:

Examples
^^^^^^^^

::

  TBD

.. _api_javalist:

JavaList
--------

.. autoclass:: py4j.java_gateway.JavaList
   :members:
   :undoc-members:

Examples
^^^^^^^^

::

  TBD
   
