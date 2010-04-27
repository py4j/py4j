:mod:`py4j.java_gateway` --- Py4J Main API
==========================================

.. module:: py4j.java_gateway
  :synopsis: Main Py4J Python module.
.. moduleauthor:: Barthelemy Dagenais <barthe@users.sourceforge.net>

The :mod:`py4j.java_gateway` module defines most of the classes that are needed to use Py4J. Py4J users are expected
to only use explicitly :class:`JavaGateway <py4j.java_gateway.JavaGateway>` and optionally, :class:`CommChannelFactory
<py4j.java_gateway.CommChannelFactory>`, :func:`get_field <py4j.java_gateway.get_field>`, and :func:`get_method
<py4j.java_gateway.get_method>`. The other module members are documented to support the extension of Py4J.

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
  
.. _api_commchannelfactory:

CommChannelFactory
------------------

.. autoclass:: py4j.java_gateway.CommChannelFactory
   :members:
   :undoc-members:



..
  Examples
  ^^^^^^^^

  ::

    TBD

.. _api_commchannel:

CommChannel
-----------

.. autoclass:: py4j.java_gateway.CommChannel
   :members:
   :undoc-members:

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

.. _api_jvm:

JVM
---

.. autoclass:: py4j.java_gateway.JVM
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

..
  Examples
  ^^^^^^^^

  ::

    TBD

.. _api_javamember:

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

.. _api_javaclass:

JavaClass
---------

.. autoclass:: py4j.java_gateway.JavaClass
   :members:
   :undoc-members:

..
  Examples
  ^^^^^^^^

  ::

    TBD

.. _api_javapackage:

JavaPackage
-----------

.. autoclass:: py4j.java_gateway.JavaPackage
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

The following two functions get be used to get a particular field or method when fields and methods in a Java class have the same name:
   
.. autofunction:: py4j.java_gateway.get_field

.. autofunction:: py4j.java_gateway.get_method
   
The following functions can be used to extend Py4J (e.g., to create new commands):

.. autofunction:: py4j.java_gateway.escape_new_line

.. autofunction:: py4j.java_gateway.unescape_new_line 

.. autofunction:: py4j.java_gateway.get_command_part

.. autofunction:: py4j.java_gateway.get_return_value