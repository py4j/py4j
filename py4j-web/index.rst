.. Py4J documentation master file, created by
   sphinx-quickstart on Thu Dec 10 15:12:43 2009.

Welcome to Py4J
===============

Py4J enables Python programs running in a Python interpreter to dynamically access Java objects in a Java Virtual
Machine. Methods are called as if the Java objects resided in the Python interpreter and Java collections can be
accessed through standard Python collection methods. Py4J also enables Java programs to call back Python objects. Py4J
is distributed under the `BSD license <http://sourceforge.net/apps/trac/py4j/browser/trunk/py4j-python/LICENSE.txt>`_.

Here is a brief example of what you can do with Py4J. The following Python program creates a `java.util.ArrayList`
instance from a JVM and calls some of its methods using the standard Python list methods. It also accesses a custom
Java class, `ListPrinter` to print the list as a String.

::

  >>> from py4j.java_gateway import JavaGateway
  >>> gateway = JavaGateway()                        # connect to the JVM        
  >>> java_list = gateway.jvm.java.util.ArrayList()  # create an ArrayList
  >>> java_list.append('Hello ')                     # call ArrayList.add in the JVM 
  >>> java_list.append('World')
  >>> java_list.append('Now')
  >>> liststr = gateway.entry_point.getListAsString(java_list[:-1])
  >>> print(liststr)
  Hello World

This is the highly complex Java program that was executing at the same time (no code was generated and no tool was
required to run these programs). The `ListPrinter` is the `gateway.entry_point` in the previous code snippet.

.. code-block:: java

  public class ListPrinter {
      public String getListAsString(List<?> list) {
          StringBuffer sb = new StringBuffer();
          for (Object o: list) {
              sb.append(o.toString());
          }
          return sb.toString();
      }

      public static void main(String[] args) {
          GatewayServer server = new GatewayServer(new ListPrinter());
          server.start();
      }
  }
 


Resources
=========

* Take a look at the tutorial :doc:`getting_started`.
* Browse the :doc:`contents` or the :doc:`faq`.
* Ask a question on the `mailing list <https://lists.sourceforge.net/lists/listinfo/py4j-users>`_.
* Look at the `roadmap <https://sourceforge.net/apps/trac/py4j/roadmap>`_.

News
====

* **April 11th 2010** - Py4J 0.3 has been released. See the :doc:`changelog` for more details about the new features!
* **February 11th 2010** - Py4J 0.2 has been released. See the :doc:`changelog` for more details about all the new features that found their way in the latest release!
* **December 23rd 2009** - Py4J 0.1 has been released. Rejoice!
* **December 11th 2009** - Py4J is still in the planning phase, but the `code <https://sourceforge.net/projects/py4j/develop>`_ 
  currently works for basic scenarios. A release and a tutorial should be available in the following weeks.
