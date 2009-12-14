.. Py4J documentation master file, created by
   sphinx-quickstart on Thu Dec 10 15:12:43 2009.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to Py4J
===============

Py4J enables Python programs to dynamically access arbitrary Java objects. Methods are called as if the Java objects
resided in the Python virtual machine. There is no code to generate and no interface to implement for the shared objects 
on both sides.

Here is a brief example of what you can do with Py4J. The following Python program receives a *java.lang.StringBuffer* instance from a JVM and calls some of its methods:

::

  >>> from py4j.java_gateway import JavaGateway
  >>> gateway = JavaGateway()             # connect to the JVM
  >>> buffer = gateway.getStringBuffer()  # call BufferGateway.getStringBuffer() in the JVM
  >>> buffer.append(True)                 # call StringBuffer.append(boolean) in the JVM
  >>> buffer.append(1.0)
  >>> buffer.append('This is a Python %s' % 'string')
  >>> print(buffer.toString())
  FromJavatrue1.0This is a Python string

This is the highly complex Java program that was executing at the same time (no code was generated and no tool was required to run these programs):

.. code-block:: java

  public class BufferGateway extends DefaultGateway {
	  public StringBuffer getStringBuffer() {
		  StringBuffer sb = new StringBuffer("FromJava");
		  return sb;
	  }
	  
	  public static void main(String[] args) {
		  GatewayServer server = new GatewayServer(new BufferGateway());
		  server.start();
	  }  
  }

Resources
=========

Resources will be added soon.


News
====

* **December 11th 2009** - Py4J is still in the planning phase, but the `code <https://sourceforge.net/projects/py4j/develop>`_ 
  currently works for basic scenarios. A release and a tutorial should be available in the following weeks.
