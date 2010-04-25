:mod:`py4j.java_gateway` --- Py4J Main API
==========================================

.. module:: py4j.java_gateway
  :synopsis: Main Py4J Python module.
.. moduleauthor:: Barthelemy Dagenais <barthe@users.sourceforge.net>

.. _api_javagateway:

JavaGateway
-----------

.. autoclass:: py4j.java_gateway.JavaGateway
   :members:
   :undoc-members:

   
.. _api_java_gateway_examples:

Examples
^^^^^^^^

Using the ``jvm`` property:
::

  >>> gateway = JavaGateway()
  >>> jvm = gateway.jvm
  >>> l = jvm.java.util.ArrayList()
  >>> l.append(10)
  >>> l.append(1)
  >>> jvm.java.util.Collections.sort(l)
  >>> l
  [1, 10]
  >>> l.append(5)
  >>> l.sort()
  >>> l
  [1, 5, 10]
  
Using non-default value of ``auto_start``:
::
  
  java_gateway = JavaGateway(auto_start=False)
  java_gateway.comm_channel.start()
  # ... do some work here
  java_gateway.comm_channel.stop()


Using ``auto_field``:

First we declare a class that has a field AND a method called `member`:

.. code-block:: java

  package py4j.examples;
  public class ExampleWithField {
      public int member = 1;
      public String member() {
          return "Hello World";
      }
  }

Then we play with the class using the two possible values of auto_field:

::

  >>> java_gateway = JavaGateway() # auto_field = False
  >>> example = java_gateway.jvm.py4j.examples.ExampleWithField()
  >>> example.member()
  u'Hello World'
  >>> get_field(example,'member')
  1
  >>> java_gateway2 = JavaGateway(auto_field=True)
  >>> example2 = java_gateway2.jvm.py4j.examples.ExampleWithField()
  >>> example2.member
  1
  >>> get_method(example2,'member')()
  u'Hello World'
  
.. _api_commchannel:

CommChannel
-----------

.. autoclass:: py4j.java_gateway.CommChannel
   :members:
   :undoc-members:

   .. automethod:: __del__()



..
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

..
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

..
  Examples
  ^^^^^^^^

  ::

    TBD

JavaMember
-----------

.. autoclass:: py4j.java_gateway.JavaMember
   :members:
   :undoc-members:

..
  Examples
  ^^^^^^^^

  ::

    TBD



 .. _api_functions:
 

Py4J Functions
--------------

.. _api_functions_get_field:
 
    
.. autofunction:: py4j.java_gateway.get_field

.. autofunction:: py4j.java_gateway.get_method
   
.. autofunction:: py4j.java_gateway.escape_new_line

.. autofunction:: py4j.java_gateway.unescape_new_line 

.. autofunction:: py4j.java_gateway.get_command_part

.. autofunction:: py4j.java_gateway.get_return_value