Getting Started with Py4J
=========================

This short tutorial assumes that you have already :ref:`installed <install_instructions>` Py4J and that you are using
the latest version. In this tutorial, you will write a simple Stack class in Java and then, you will write a Python
program that accesses the stack.

You will also see how Java lists can be manipulated as Python lists.

Writing the Java Program
------------------------

The first step is to write a short Java program. Here you will create a Stack class that offers two basic services and
two advanced services:

1. Push an element at the top of the stack.
2. Pop the element at the top of the stack.
3. Get the list that contains the stack.
4. Push all elements contained in a list.

Here is the code of the stack:

.. code-block:: java

  package py4j.examples;

  import java.util.LinkedList;
  import java.util.List;

  public class Stack {
      private List<String> internalList = new LinkedList<String>(); 
      
      public void push(String element) {
          internalList.add(0, element);
      }
      
      public String pop() {
          return internalList.remove(0);
      }
      
      public List<String> getInternalList() {
          return internalList;
      }
      
      public void pushAll(List<String> elements) {
          for (String element : elements) {
              this.push(element);
          }
      }
  }

To make the stack available to a Python program, you need an entry point, something that will allow Python programs to:

1. Access the JVM running your program.
2. Access the objects that you created on the JVM.

This entry point is implemented by two classes. The first class is a `GatewayServer <_static/javadoc/index.html?py4j/GatewayServer.html>`_: 
it allows Python programs to communicate with the JVM through a local network socket. The second class is *Gateway* that
allows Python programs to get specific objects that you created in the JVM. 

The `GatewayServer <_static/javadoc/index.html?py4j/GatewayServer.html>`_ provided by Py4J can be used as is. At most,
you will need to configure it to specify a network address and port, if the defaults (localhost, 25333) do not work for
you.

You still need to create your Gateway class and for that you can extend the `DefaultGateway <_static/javadoc/index.html?py4j/DefaultGateway.html>`_ class.

.. note::
   
   If you do not want to extend `DefaultGateway <_static/javadoc/index.html?py4j/DefaultGateway.html>`_, you can simply 
   implement the `Gateway <_static/javadoc/index.html?py4j/Gateway.html>`_ interface. Looking at the `code of DefaultGateway <http://sourceforge.net/apps/trac/py4j/browser/trunk/py4j-java/src/py4j/DefaultGateway.java>`_  
   will give you good examples on how to implement these methods.

Here is an example of a custom Gateway class that would allow a Python program to access stacks:

.. code-block:: java

  package py4j.examples;

  import py4j.DefaultGateway;
  import py4j.GatewayServer;

  public class StackGateway extends DefaultGateway {

      public Stack createNewStack() {
          return new Stack();
      }
      
      public static void main(String[] args) {
          GatewayServer gatewayServer = new GatewayServer(new StackGateway());
          gatewayServer.start();
          System.out.println("Gateway Server Started");
      }
      
  }

There are a few important lines in this code. First, you declare a class that extends the `DefaultGateway <_static/javadoc/index.html?py4j/DefaultGateway.html>`_.

.. code-block:: java

   public class StackGateway extends DefaultGateway

Then, you create a method that creates stacks. This method could do anything and could return anything you want. Here it
just creates new stacks, but it could access existing stacks too or anything you can think of.

.. code-block:: java

      public Stack createNewStack() {
          return new Stack();
      }

Then, you create a main method. This main method could be located in another class. The first thing you do in the main
method is to initialize a `GatewayServer <_static/javadoc/index.html?py4j/GatewayServer.html>`_ and link it to an
instance of our custom gateway. Essentially, you are saying that you want Python programs to access our custom gateway.

.. code-block:: java

    public static void main(String[] args) {
          GatewayServer gatewayServer = new GatewayServer(new StackGateway());

Finally, you need to start the gateway so it can accept incoming Python requests:

.. code-block:: java

      gatewayServer.start();

You are now ready to try your Java program. Just executes the StackGateway class in your favorite development environment and check that you see the message ``Gateway Server Started``

.. warning:: 
   
   When running your application, you may get a ``java.net.BindException: Address already in use`` exception. There are 
   two common causes: either you are already running another instance of your program or another program on your 
   computer is listening to the port 25333. To change the port, replace this line (use any port number):

   .. code-block:: java

     GatewayServer gatewayServer = new GatewayServer(new StackGateway());

   by this line:

   .. code-block:: java
     
     GatewayServer gatewayServer = new GatewayServer(new StackGateway(), 25334);
     
You are now done. Because your program will wait for connections, it will never exit. To terminate your program, you
have to kill it (e.g., Ctrl-C). If you initialize the GatewayServer in another method, you can also call
``gatewayServer.stop()``.

Writing the Python Program
--------------------------

You will now write the python program that will access your Java program. Start a Python interpreter and make sure that 
Py4J is in your PYTHONPATH.

The first step is to import the necessary Py4J class:

:: 

  >>> from py4j.java_gateway import JavaGateway

Next, initialize a :ref:`JavaGateway <api_javagateway>`. The default parameters are usually sufficient for common cases. When you create a :ref:`JavaGateway <api_javagateway>`, Python tries to connect to a JVM with a gateway (localhost on port 25333).

:: 

  >>> gateway = JavaGateway()

.. warning::

  If you receive the following error: ``socket.error: [Errno 111] Connection refused``, it means that there is no JVM
  waiting for a connection. Check that your Java program is still running, or if you did not start it, now would be a good
  time to do so :-)

From the gateway object, we can access the StackGateway by calling methods. Since StackGateway only declares one method, we can call it now:

:: 

  >>> stack = gateway.createNewStack()

The stack variable now contains a stack. Try to push and pop a few elements:

:: 

  >>> stack.push("First %s" % ('item'))
  >>> stack.push("Second item")        
  >>> stack.pop()                                        
  u'Second item'                                         
  >>> stack.pop()                                        
  u'First item'       

Now the stack is supposed to be empty. Here is what happens if you try to pop it again.

:: 
                                   
  >>> stack.pop()                                        
  Traceback (most recent call last):                     
    File "<stdin>", line 1, in <module>                  
    File "py4j/java_gateway.py", line 161, in __call__   
      return_value = get_return_value(answer, self.comm_channel, self.target_id, self.name)
    File "py4j/java_gateway.py", line 74, in get_return_value                              
      raise Py4JError('An error occurred while calling %s%s%s' % (target_id, '.', name))   
  py4j.java_gateway.Py4JError: u'An error occurred while calling o0.pop'                   

You get a :ref:`Py4JError <api_py4jerror>` because there was an exception on the JVM side. Actually, if you look at the
console of your JVM, you will see a bunch of logging sentences, including this exception:

.. code-block:: java 

  py4j.Py4JException: javax.script.ScriptException: sun.org.mozilla.javascript.internal.WrappedException: Wrapped java.lang.IndexOutOfBoundsException: Index: 0, Size: 0 (<Unknown source>#1) in <Unknown source> at line number 1

Now, you will experiment with lists. Add another element and get the internal list of the stack:

::

  >>> stack.push('First item')                                                             
  >>> internal_list = stack.getInternalList()
  >>> len(internal_list)                     
  1
  >>> internal_list[0]
  u'First item'
  >>> internal_list.append('Second item')
  >>> internal_list
  [u'First item', u'Second item']
  >>> stack.getInternalList()
  [u'First item', u'Second item']

As you can see, lists created on the JVM act like Python strings: you can use the ``[]`` operator and the usual list
methods like ``len`` and ``append``. Notice that when you change the list on the Python side, it is also changed on the
Java side. Now try to slice the list:

::

  >>> sliced_list = internal_list[0:1]
  >>> sliced_list
  [u'First item']
  >>> sliced_list.append('Third item')
  >>> sliced_list
  [u'First item', u'Third item']
  >>> internal_list
  [u'First item', u'Second item']
  >>> stack.getInternalList()
  [u'First item', u'Second item']
  >>> stack.pushAll(sliced_list)
  >>> stack.getInternalList()
  [u'Third item', u'First item', u'First item', u'Second item']

Slices act like real Python slices: they are a copy of the original list, no more, no less. This is why the original
list is not modified when you modify the slice. When you create a slice, Py4J first creates the slice on the JVM side so
you are really accessing a Java list contained in the JVM.

.. note::
  For the keen Java programmers among you, note that the slice operation is **NOT** implemented with the ``subList`` 
  method in Java, because ``subList`` returns a view, not a copy, of the list: when the original list changes, the view 
  generally becomes invalid.

In the previous example, you also tried to pass a list as a parameter of the pushAll method. See what happens if you try 
to pass a pure Python list that was not returned by the JVM:

::

  >>> stack.pushAll(['Fourth item'])
  Traceback (most recent call last):
    File "<stdin>", line 1, in <module>
    File "py4j/java_gateway.py", line 158, in __call__
      args_command = ''.join([get_command_part(arg) for arg in args])
    File "py4j/java_gateway.py", line 68, in get_command_part
      command_part = REFERENCE_TYPE + parameter.get_object_id()
  AttributeError: 'list' object has no attribute 'get_object_id'
  >>> stack.getInternalList()
  [u'Third item', u'First item', u'First item', u'Second item']

As of version 0.1, Py4J does not support the conversion from pure Python lists to Java list. This is a feature that will 
likely be implemented in version 0.2 or 0.3. Finally, Python has powerful introspection abilities that are slowly being
replicated by Py4J. For example, a JavaGateway always allow you to list all the methods available on an object:

:: 

  >>> gateway.getMethodNames(stack)
  [u'getClass', u'equals', u'notify', u'hashCode', u'toString', u'pushAll', u'pop', u'wait', u'push', u'notifyAll',u'getInternalList']
  
And in case you are wondering, here is how Py4J implement the Java objects in Python:

::

  >>> type(stack)
  <class 'py4j.java_gateway.JavaObject'>
  >>> type(internal_list)
  <class 'py4j.java_gateway.JavaList'>


Where to go from here
---------------------

* You can explore the :doc:`Py4J Python API <py4j_python>` or the :doc:`Py4J Java API <py4j_java>`.
* Look at the :doc:`FAQ <faq>`.


 