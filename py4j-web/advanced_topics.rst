Advanced Topics
===============

Accessing Java collections and arrays from Python
-------------------------------------------------

Java collections are automatically mapped to Python collections so that
standard Python operations such as slicing work on Java collections. Here is
the mapping of the collection:

=================== ====================== ==========================================================
Java Collection     Python Collection      Py4J Implementation
=================== ====================== ==========================================================
Array               Sequence [#arraynote]_ :class:`JavaArray <py4j.java_collections.JavaArray>`
java.util.List      MutableSequence        :class:`JavaList <py4j.java_collections.JavaList>`
java.util.Set       MutableSet             :class:`JavaSet <py4j.java_collections.JavaSet>`
java.util.Map       MutableMapping         :class:`JavaMap <py4j.java_collections.JavaMap>`
java.util.Iterator  *Iterator Protocol*    :class:`JavaIterator <py4j.java_collections.JavaIterator>`
=================== ====================== ==========================================================

.. [#arraynote] Py4J allows elements to be modified (like a real Java array), which is not the case of true
   immutable sequences like tuples.

Java methods are still accessible when using the Python version of a Java
collection. Here are some usage examples for each collection class. These
examples do not cover the entire API.

It is possible to change this default mapping by registering an output
converter with :func:`register_output_converter
<py4j.protocol.register_output_converter>`

Array
^^^^^

::

  >>> gateway = JavaGateway()
  >>> int_class = gateway.jvm.int
  >>> int_array = gateway.new_array(int_class,2)
  >>> int_array[0] = 1
  >>> int_array[1] = 2
  >>> int_array[0]
  1
  >>> int_array[2]
  Traceback (most recent call last):
  ...
  IndexError: list index out of range
  >>> for i in int_array:
  ...     print(i)
  ...
  1
  2
  >>> sarray = gateway.new_array(gateway.jvm.java.lang.String,2,3)
  >>> len(sarray)
  2
  >>> len(sarray[0])
  3
  >>> sarray[0][1] = 'hello'
  >>> sarray[0][1]
  u'hello'
  >>> sarray[0][0] == None
  True


List
^^^^

::

  >>> l = gateway.jvm.java.util.ArrayList()
  >>> l.append(1) # calling Python interface
  >>> l.add('hello') # calling Java interface
  >>> for elem in l:
  ...     print elem
  ...
  1
  hello
  >>> l[0] = 2
  >>> l.append(3)
  >>> str(l)
  "[2, u'hello', 3]"
  >>> l2 = l[0:-1]
  >>> l2[0] = 999
  >>> l
  [2, u'hello', 3]
  >>> l2 # l2 is a copy of l and not a view so a change in l2 does not affect l
  [999, u'hello']
  >>> del(l[0])
  >>> l
  [u'hello', 3]


Set
^^^

::

  >>> s = gateway.jvm.java.util.HashSet()
  >>> s.add(1)
  >>> s.add('hello')
  >>> s
  set([1, u'hello'])
  >>> 1 in s
  True
  >>> s.remove(u'hello')
  >>> s
  set([1])


Map
^^^

::

  >>> m = gateway.jvm.java.util.HashMap()
  >>> m["a"] = 0
  >>> m.put("b",1)
  >>> m
  {u'a': 0, u'b': 1}
  >>> u"b" in m
  True
  >>> del(m["a"])
  >>> m
  {u'b': 1}
  >>> m["c"] = 2
  >>> for key in m:
  ...     print("%s:%i" % (key,m[key]))
  ...
  b:1
  c:2


Byte array (byte[])
-------------------

Since version 0.7, Py4J automatically passes Java byte array (i.e., `byte[]`)
by value and convert them to Python bytearray (2.x) or bytes (3.x) and vice
versa. The rationale is that byte array are often used for binary processing
and are often immutable: a program reads a series of byte from a data source
and interpret it (or transform it into another byte array).

Prior to 0.7, a Python program could interact with a Java byte[] but each
access to a byte required a call between the Python and the Java interpreter
(i.e., the Python program only had a reference to the array).

In summary:

* If from Java, you return a byte[], Py4J will convert the byte[] to a
  bytearray (Python 2.x) or bytes (Python 3.x) variable in Python.

* If from Python, you pass a bytearray or bytes variable to the Java side,
  Py4J will convert it to a byte[].

* If you pass a byte[] from Java to Python, both arrays are disconnected: a
  change to the array on one side will not be reflected on the other side.

* If you want to pass an array by reference, use a `Byte[]` instead of a
  `byte[]` or you can use  `Bytes.asList
  <http://guava-libraries.googlecode.com/svn/trunk/javadoc/com/google/common/primitives/Bytes.html#asList(byte...)>`_
  from `Guava <http://code.google.com/p/guava-libraries/>`_ to obtain a list
  backed by a byte array.


Implementing Java interfaces from Python (callback)
---------------------------------------------------

Since version 0.3, Py4J allows Python classes to implement Java interfaces so
that the JVM can call back Python objects. In the following example, a Python
class implements a Java listener interface.

Here is the code of listener interface:

.. code-block:: java

  // py4j/examples/ExampleListener.java
  package py4j.examples;

  public interface ExampleListener {

      Object notify(Object source);

  }


Here is the code of the main Java application.  The program has a main method
starting a `GatewayServer`. The entry point, a `ListenerApplication` instance,
has two methods, one to register listeners, the other to notify all listeners.
Start this program before running the Python code below.

.. code-block:: java

  // py4j/examples/ListenerApplication.java
  package py4j.examples;

  import py4j.GatewayServer;

  import java.util.ArrayList;
  import java.util.List;

  public class ListenerApplication {

      List<ExampleListener> listeners = new ArrayList<ExampleListener>();

      public void registerListener(ExampleListener listener) {
          listeners.add(listener);
      }

      public void notifyAllListeners() {
          for (ExampleListener listener: listeners) {
              Object returnValue = listener.notify(this);
              System.out.println(returnValue);
          }
      }

      @Override
      public String toString() {
          return "<ListenerApplication> instance";
      }

      public static void main(String[] args) {
          ListenerApplication application = new ListenerApplication();
          GatewayServer server = new GatewayServer(application);
          server.start(true);
      }
  }


Here is the Python program that implements the Java interface and calls the
ListenerApplication to notify all listeners. Then multiple exchanges between
Java and Python occurs (e.g., Python calls System.out.println on the Java
side).

::


  from py4j.java_gateway import JavaGateway, CallbackServerParameters


  class PythonListener(object):

      def __init__(self, gateway):
          self.gateway = gateway

      def notify(self, obj):
          print("Notified by Java")
          print(obj)
          gateway.jvm.System.out.println("Hello from python!")

          return "A Return Value"

      class Java:
          implements = ["py4j.examples.ExampleListener"]

  if __name__ == "__main__":
      gateway = JavaGateway(
          callback_server_parameters=CallbackServerParameters())
      listener = PythonListener(gateway)
      gateway.entry_point.registerListener(listener)
      gateway.entry_point.notifyAllListeners()
      gateway.shutdown()


The `PythonListener` class is a standard Python class that has one method,
`notify`. The signature of the method contains one parameter. When interfaces
contain overloaded methods, the python method must accept all possible
combinations of parameters (with `*args` and `**kwargs` or with default
parameters).

Py4J recognizes that the `PythonListener` class implements a Java interface
because it declares an internal class called `Java`, which has a member named
`implements`. This member is a list of string representing the fully qualified
name of implemented Java interfaces.

Finally, the Python program contains a main method that starts a gateway,
initializes a PythonListener instance and registers it to the
`ListenerApplication` instance on the Java side. Then, it calls the
`notifyAllListeners()` method, which will notify all listeners. Py4J takes care
of creating the necessary proxies: the `notify` method of the `PythonListener`
class is called in the Java VM, but the method is executed in the Python
interpreter.


.. warning::

   Python classes can only implement Java interfaces. Abstract or concrete
   classes are not supported because Java does not natively support dynamic
   proxies for classes. Extending classes may be supported in future releases
   of Py4J.

   As a workaround, a subclass of the abstract class could be created on the
   Java side. The methods of the subclass would call the methods of a custom
   interface that a Python class could implement.


.. warning::

   If you want to implement an interface declared in a class (i.e., an
   internal class), you need to prefix the name of the interface with
   a dollar sign. For example, if the interface `Operator` is declared
   in the class `package1.MyClass`, you will have to write:

   `implements = ['package1.MyClass$Operator']`


.. _clientserver:

Using Single Threading Model (pinned thread)
--------------------------------------------

The multi threading model
^^^^^^^^^^^^^^^^^^^^^^^^^

When you use a `JavaGateway` and a `CallbackServer`, Py4J will create a new
thread every time a command **is received** and **there is no thread
available**.  This can lead to the creation of many threads if there are
recursive calls between Python and Java. For example, let's consider this code:


.. code-block:: python

  class PythonPlayer(object):

      def start(self, player):
          return player.firstPing(self)

      def firstPong(self, player):
          return player.secondPing(self)

      def secondPong(self, player):
          return "Success"

      class Java:
          implements = ["py4j.examples.PongPlayer"]

  # Start the JVM with "java -cp py4j.jar py4j.examples.ExampleApplication"
  from py4j.java_gateway import JavaGateway, CallbackServerParameters
  gateway = JavaGateway(
      callback_server_parameters=CallbackServerParameters())
  ping_player = java_gateway.jvm.py4j.examples.PingPlayer()
  pong_player = PongPlayer()
  print(pong_player.start(ping_player))


.. code-block:: java

  // PongPlayer.java
  package py4j.examples;

  public interface PongPlayer {

      String firstPong(PingPlayer player);

      String secondPong(PingPlayer player);

  }

  // PingPlayer.java
  package py4j.examples;

  public class PingPlayer {

      public String firstPing(PongPlayer player) {
          return player.firstPong(this);
      }

      public String secondPing(PongPlayer player) {
          return player.secondPong(this);
      }

  }



When this code is executed, the Python side creates 2 threads and the
Java side creates two threads (note that the Java and Python sides both start
with an implicit thread so there are a minimum of three threads on either
side).

1. The Python client initiates the conversation by calling firstPing()
   and waits for a response.

2. The Java server receives the call and creates Java Thread 1 to execute the
   code. Java then calls firstPong and waits for a response.

3. The Python server receives the call and creates Python Thread 1 to execute
   the code. Python then calls secondPing and waits for a response.

4. The Java server receives the call and creates Java Thread 2 to execute the
   code. Java then calls secondPong and waits for a response.

5. The Python server receives the call and creates Python Thread 2 to execute
   the code. Python then returns the response ``"Success"``. Python Thread 2
   can now be used to execute other calls.

6. Java Thread 2 (secondPing) receives a response and sends back the
   response to the Python side. Java Thread 2 can now be used to execute other
   calls.

7. Python Thread 1 (firstPong) receives a response and sends back the response
   to the Java side. Python Thread 1 can now be used to execute other calls.

8. Java Thread 1 (firstPing) receives a response and sends back the response to
   the Python side. Java Thread 1 can now be used to execute other calls.

9. The Python side receives the response and prints it.


The single threading model
^^^^^^^^^^^^^^^^^^^^^^^^^^

Although the multi threading model is sound and has been used by many
distributed systems (e.g., Java RMI), it has two main issues: (1) it creates a
lot of threads when the Java and Python sides exchange many calls such as when
there is indirect recursion between the two sides, and (2) it is not possible
to control in which thread the code will be executed. The first issue can
severely impact performance and the second issue limits the usefulness of Py4J
in certain applications (e.g., GUI applications).

To work around these limitations, the :mod:`py4j.clientserver` module
implements a single threading model also called *pinned thread model* that
ensures that callbacks received from the other side will be executed in the
initiating thread. For example, if we modify the previous code with this one:


.. code-block:: python

  # Start the JVM with "java -cp py4j.jar py4j.examples.SingleThreadApplication"
  from py4j.clientserver import ClientServer, JavaParameters, PythonParameters
  gateway = ClientServer(
      java_parameters=JavaParameters(),
      python_parameters=PythonParameters())
  ping_player = gateway.jvm.py4j.examples.PingPlayer()
  pong_player = PongPlayer()
  print(pong_player.start(ping_player))

Only one Java Thread will be created and no Python thread will be created:

1. The Python client initiates the conversation from Python Thread 1 by calling
   firstPing() and waits for **either a response or a call to execute**.

2. The Java server receives the call and creates Java Thread 1 to execute the
   code. Java then calls firstPong and waits for a response or a call to
   execute.

3. Python Thread 1 receives the call and calls secondPing. It waits for a
   response or a call.

4. Java Thread 1 receives the call and then call secondPong.  It waits for a
   response or a call.

5. Python Thread 1 receives the call responds with ``"Success"``.

6. Java Thread 1 (secondPing) receives the response and sends the response to the Python
   side.

7. Python Thread 1 (firstPong) receives the response and sends the response to
   the Java side.

8. Java Thread 1 (firstPing) receives the response and sends the response to
   the Python side.

9. Python Thread 1 (start) receives the response and prints it.

In total, only one thread was created (on the Java side). If for whatever
reason multiple threads are created on the Python side and they each call the
Java side, a corresponding Java thread will be created. For example, if three
threads from the Python side are calling the Java side, three Java threads will
be created.



.. _python_entry_point:

Initiating the communication from the Java side
-----------------------------------------------

All the previous examples assume that you want to initiate the communication
between Python and Java from the Python side. What if you want to start calling
Python from the Java side?

If you want Java to call Python first, you need to:

1. Start the Python process and create either a JavaGateway or a ClientServer.
2. Pass a Python instance implementing a Java interface as a
   ``python_server_entry_point`` parameter.
3. Start a GatewayServer or ClientServer on the Java side.
4. Call ``getPythonServerEntryPoint`` by providing the list of interfaces the
   Python entry point is expected to implement.


Using the traditional JavaGateway/GatewayServer
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: java

  // IHello.java
  package py4j.examples;

  public interface IHello {
      public String sayHello();

      public String sayHello(int i, String s);
  }

  // ExampleClientApplication.java
  package py4j.examples;

  import py4j.GatewayServer;

  public class ExampleClientApplication {

      public static void main(String[] args) {
            GatewayServer.turnLoggingOff();
            GatewayServer server = new GatewayServer();
            server.start();
            IHello hello = (IHello) server.getPythonServerEntryPoint(new Class[] { IHello.class });
            try {
                hello.sayHello();
                hello.sayHello(2, "Hello World");
            } catch (Exception e) {
                e.printStackTrace();
            }
            server.shutdown();
      }
  }

.. code-block:: python

  class SimpleHello(object):

      def sayHello(self, int_value=None, string_value=None):
          print(int_value, string_value)
          return "Said hello to {0}".format(string_value)

      class Java:
          implements = ["py4j.examples.IHello"]

  # Make sure that the python code is started first.
  # Then execute: java -cp py4j.jar py4j.examples.SingleThreadClientApplication
  from py4j.java_gateway import JavaGateway, CallbackServerParameters
  simple_hello = SimpleHello()
  gateway = JavaGateway(
      callback_server_parameters=CallbackServerParameters(),
      python_server_entry_point=simple_hello)


Using ClientServer
^^^^^^^^^^^^^^^^^^

In the following example, the Java side is initiating the conversation by
making the first call to the Python side. If the call is initiated from a UI
thread, then all subsequent call from Python to Java will be executed in the
Java UI thread.


.. code-block:: java

  // IHello.java
  package py4j.examples;

  public interface IHello {
      public String sayHello();

      public String sayHello(int i, String s);
  }

  // SingleThreadClientApplication.java
  package py4j.examples;

  import py4j.ClientServer;
  import py4j.GatewayServer;

  public class SingleThreadClientApplication {

      public static void main(String[] args) {
          ClientServer clientServer = new ClientServer(null);
          // We get an entry point from the Python side
          IHello hello = (IHello) clientServer.getPythonServerEntryPoint(new Class[] { IHello.class });
          // Java calls Python without ever having been called from Python
          System.out.println(hello.sayHello());
          System.out.println(hello.sayHello(2, "Hello World"));
          clientServer.shutdown();
      }
  }


.. code-block:: python

  class SimpleHello(object):

      def sayHello(self, int_value=None, string_value=None):
          print(int_value, string_value)
          return "Said hello to {0}".format(string_value)

      class Java:
          implements = ["py4j.examples.IHello"]

  # Make sure that the python code is started first.
  # Then execute: java -cp py4j.jar py4j.examples.SingleThreadClientApplication
  from py4j.clientserver import ClientServer, JavaParameters, PythonParameters
  simple_hello = SimpleHello()
  gateway = ClientServer(
      java_parameters=JavaParameters(),
      python_parameters=PythonParameters(),
      python_server_entry_point=simple_hello)



.. _dynamic_ports:

Using Py4J without pre-determined ports (dynamic port number)
-------------------------------------------------------------

If you do not want to use Py4J's default port (25333 on the Java side and 25334
on the Python side to receive callback), you can use the port 0 and Py4J will
use the next available port. Once a port is assigned, the other side needs to
be aware of this port. Here is one way to do it:


.. code-block:: python

  from py4j.java_gateway import (
      JavaGateway, CallbackServerParameters, GatewayParameters,
      launch_gateway)
  # launch Java side with dynamic port and get back the port on which the
  # server was bound to.
  port = launch_gateway()

  # connect python side to Java side with Java dynamic port and start python
  # callback server with a dynamic port
  gateway = JavaGateway(
      gateway_parameters=GatewayParameters(port=port),
      callback_server_parameters=CallbackServerParameters(port=0))

  # retrieve the port on which the python callback server was bound to.
  python_port = gateway.get_callback_server().get_listening_port()

  # tell the Java side to connect to the python callback server with the new
  # python port. Note that we use the java_gateway_server attribute that
  # retrieves the GatewayServer instance.
  gateway.java_gateway_server.resetCallbackClient(
      gateway.java_gateway_server.getCallbackClient().getAddress(),
      python_port)

  # Test that callbacks work
  from py4j.tests.java_callback_test import IHelloImpl
  hello = IHelloImpl()
  example = gateway.jvm.py4j.examples.ExampleClass()
  example.callHello(hello)


.. _collections_conversion:

Converting Python collections to Java Collections
-------------------------------------------------

If you try to pass a Python collection to a method that expects a Java
collection, an error will be thrown:

::

  >>> my_list = [3,2,1]
  >>> gateway.jvm.java.util.Collections.sort(my_list)
  Traceback (most recent call last):
    File "<stdin>", line 1, in <module>
    File "py4j/java_gateway.py", line 347, in __call__
      args_command = ''.join([get_command_part(arg, self.pool) for arg in new_args])
    File "py4j/protocol.py", line 195, in get_command_part
      command_part = REFERENCE_TYPE + parameter._get_object_id()
  AttributeError: 'list' object has no attribute '_get_object_id'


You can explicitly convert Python collections using one of the following
converter located in the `py4j.java_collections` module: `SetConverter`,
`MapConverter`, `ListConverter`.

::

  >>> from py4j.java_collections import SetConverter, MapConverter, ListConverter
  >>> java_list = ListConverter().convert(my_list, gateway._gateway_client)
  >>> gateway.jvm.java.util.Collections.sort(java_list)
  >>> java_list
  [1, 2, 3]
  >>> my_list
  [3, 2, 1]

Note that the Python list is totally disconnected from the Java list. The Java
List is actually a copy. You can also ask Py4J to automatically convert Python
collections to Java Collections when calling a Java method: just set
``auto_convert=True`` when creating a `JavaGateway`:

::

  >>> gateway = JavaGateway(gateway_parameters=GatewayParameters(auto_convert=True))
  >>> my_list
  [3, 2, 1]
  >>> gateway.jvm.java.util.Collections.sort(my_list)
  >>> my_list # The python list is not sorted!
  [3, 2, 1]
  >>> gateway.jvm.java.util.Collections.frequency(my_list,2)
  1

Again, note that my_list is not sorted because when calling
`Collections.sort()`, Py4J only makes a copy of the Python list. Still, a copy
can be useful if you do not expect the list to be modified by the Java method
like in the call to ``frequency()``.

**Order of Automatic Conversion**

When ``auto_convert=True``, Py4J will attempt to automatically convert Python
objects that are not an instance of ``basestring`` or ``JavaObject``. By
default, Py4J performs the following checks and conversions:

1. If the Python object is an instance of `collections.Set`, it is converted to
   a `HashSet`.
2. If the object has the methods `keys()` and `__getitem__`, it is converted to
   a `HashMap`
3. If the object is iterable, it is converted to an `ArrayList`.
4. Otherwise, standard Py4J primitive type conversion is attempted (e.g., bool to boolean).

It is possible to add custom converters by calling
:func:`register_input_converter()
<py4j.protocol.register_input_converter>`. Look at the source code of the
default converters for an example. Note that automatic conversion makes calling
Java methods slightly less efficient because in the worst case, Py4J needs to
go through all registered converters for all parameters. This is why automatic
conversion is disabled by default.


.. _py4j_exceptions:

Py4J Exceptions
---------------

Py4J can raise three exceptions on the Python side:

* :class:`Py4JJavaError <py4j.protocol.Py4JJavaError>`. This exception is
  raised when an exception occurs in the Java client code. For example, if you
  try to pop an element from an empty stack. The instance of the Java exception
  thrown is stored in the `java_exception` member.

* :class:`Py4JNetworkError <py4j.protocol.Py4JNetworkError>`. This exception is
  raised when a problem occurs during network transfer (e.g., connection lost).

* :class:`Py4JError <py4j.protocol.Py4JError>`. This exception is raised when
  any other error occurs such as when the client program tries to access an
  object that no longer exists on the Java side.

Both `Py4JJavaError` and `Py4JNetworkError` inherits from `Py4JError` so it is
possible to catch all related Py4J errors with one except clause:

.. code-block:: python

  try:
    java_object.doSomething()
  except Py4JError:
    traceback.print_exc()

If a Py4J Exception wraps another exception, the original exception will be
available in the ``clause`` field.


.. code-block:: python

  try:
    java_object.doSomething()
  except Py4JError as e:
    if e.cause:
        print(e.cause)


.. _jvm_views:

Importing packages with JVM Views
---------------------------------

Py4J allows you to import packages so that you don't have to type the fully
qualified name of the classes you want to instantiate. The `java.lang` package
is always automatically imported.

::

  >>> from py4j.java_gateway import JavaGateway
  >>> gateway = JavaGateway()
  >>> from py4j.java_gateway import java_import
  >>> java_import(gateway.jvm,'java.util.*')
  >>> jList = gateway.jvm.ArrayList()
  >>> jMap = gateway.jvm.HashMap()
  >>> gateway.jvm.java.lang.String("a")
  u'a'
  >>> gateway.jvm.String("a")
  u'a'

As opposed to Java where import statements do not cross compilation units (java
source files), the jvm instance can be shared across multiple Python modules: in
other words, import statements are global.

The recommended way to use import statements is to use one :class:`JVMView
<py4j.java_gateway.JVMView>` instance per Python module. Here is an example on
how to create and use a `JVMView`:

::

  >>> module1_view = gateway.new_jvm_view()
  >>> module2_view = gateway.new_jvm_view()
  >>> jList2 = module1_view.ArrayList()
  Py4JError: Trying to call a package.
  ...
  >>> java_import(module1_view,'java.util.ArrayList')
  >>> jList2 = module1_view.ArrayList()
  >>> jList3 = module2_view.ArrayList()
  Py4JError: Trying to call a package.
  ...

As you can see from the previous example, the import of `java.util.ArrayList`
only affects `module1_view`.

.. note::
  In fact, the `gateway.jvm` member is also an instance of :class:`JVMView
  <py4j.java_gateway.JVMView>`. It is automatically created when a gateway is
  initialized.

.. _eclipse_features:

Using Py4J with Eclipse
-----------------------

Py4J can be used with Eclipse like any normal Java program. A plug-in needs to
instantiate and start a GatewayServer. By default, the GatewayServer will only
be able to access the classes declared in the plug-in or one of its
dependencies.

Unless they have specific needs, users are encouraged to use the Eclipse
plug-ins provided by Py4J available on the following update site:

``http://eclipse.py4j.org/``

The plug-in `org.py4j.py4j-java` contains the same code as the production jar
published on maven or pypi and it also contains a OSGi MANIFEST.MF. See the
:ref:`build instructions <build_instructions>` to build the OSGi bundle
locally.

You can also use legacy plug-ins that will eventually be moved to the new build
process on the following update site:

``http://eclipse-legacy.py4j.org/``

The first plug-in, `net.sf.py4j`, provides all the Py4J Java classes such as
`GatewayServer`. The plug-in comes with the source and the javadoc. The plug-in
also declares a `global` buddy policy which allows the `GatewayServer` to
access any class declared in any plug-in loaded with Eclipse.

The second plug-in, `net.sf.py4j.defaultserver`, instantiates a GatewayServer
and starts it as soon as Eclipse is started (no lazy loading). The ports used
by the default server can be changed in the Py4J Preferences page. The server
is also accessible at runtime:


.. code-block:: java

  import net.sf.py4j.defaultserver.DefaultServerActivator;

  ...

  GatewayServer server = DefaultServerActivator.getDefault().getServer();


Here is a short example of what you could do with Py4J and Eclipse:

::

  >>> from py4j.java_gateway import JavaGateway, java_import
  >>> gateway = JavaGateway()
  >>> jvm = gateway.jvm
  >>> java_import(jvm, 'org.eclipse.core.resources.*')
  >>> workspace_root = jvm.ResourcesPlugin.getWorkspace().getRoot()
  >>> gateway.help(workspace_root,'*Projects*')
  Help on class WorkspaceRoot in package org.eclipse.core.internal.resources:

  WorkspaceRoot extends org.eclipse.core.internal.resources.Container implements org.eclipse.core.resources.IWorkspaceRoot {
  |
  |  Methods defined here:
  |
  |  getProjects() : IProject[]
  |
  |  getProjects(int) : IProject[]
  |
  |  ------------------------------------------------------------
  |  Fields defined here:
  |
  |  ------------------------------------------------------------
  |  Internal classes defined here:
  |
  }
  >>> project_names = [project.getName() for project in workspace_root.getProjects()]
  >>> print(project_names)
  [u'test2', u'testplugin', u'testplugin2']

Support for Eclipse was introduced in Py4J 0.5 and more features may be added
in the future.


Listening to server events
--------------------------

On the Java side, it is possible to listen to GatewayServer events by
registering an instance of ``py4j.GatewayServerListener`` with
``GatewayServer.addListener``.

On the Python side, it is possible to listen to CallbackServer events using
signals. Recognizing that signals may be a foreign concept to Java developers,
here is a full example:


.. code-block:: python

    from py4j.java_gateway import (
        server_connection_started, server_connection_stopped,
        server_started, server_stopped, pre_server_shutdown, post_server_shutdown,
        JavaGateway, GatewayParameters, CallbackServerParameters)

    def started(sender, **kwargs):
        server = kwargs["server"]
        # do something

    def connection_started(sender, **kwargs):
        connection = kwargs["connection"]
        # do something

    def connection_stopped(sender, **kwargs):
        connection = kwargs["connection"]
        # do something

    def stopped(sender, **kwargs):
        server = kwargs["server"]
        # do something

    def pre_shutdown(sender, **kwargs):
        server = kwargs["server"]
        # do something

    def post_shutdown(sender, **kwargs):
        server = kwargs["server"]
        # do something

    # Because the server is created and started at the same time,
    # you must listen to all started signals. You will receive the server
    # instance that was started as a parameter and sender.
    server_started.connect(started)
    gateway = JavaGateway(
        gateway_parameters=GatewayParameters(),
        callback_server_parameters=CallbackServerParameters())
    server_stopped.connect(
        stopped, sender=gateway.get_callback_server())
    server_connection_started.connect(
        connection_started,
        sender=gateway.get_callback_server())
    server_connection_stopped.connect(
        connection_stopped,
        sender=gateway.get_callback_server())
    pre_server_shutdown.connect(
        pre_shutdown, sender=gateway.get_callback_server())
    post_server_shutdown.connect(
        post_shutdown, sender=gateway.get_callback_server())

You can read more information about the :mod:`signals <py4j.signals>` module or
the :ref:`Py4J signals <api_signals>`.


.. _adv_memory:

Py4J Memory model
-----------------

**Java objects sent to the Python side**

Every time a Java object is sent to the Python side, a reference to the object
is kept on the Java side (in the Gateway class). Once the object is garbage
collected on the Python VM (reference count == 0), the reference is removed on
the Java VM: if this was the last reference, the object will likely be garbage
collected too. When a gateway is shut down, the remaining references are also
removed on the Java VM.

Because Java objects on the Python side are involved in a circular reference
(:class:`JavaObject <py4j.java_gateway.JavaObject>` and :class:`JavaMember
<py4j.java_gateway.JavaMember>` reference each other), these objects are not
immediately garbage collected once the last reference to the object is removed
(but they are guaranteed to be eventually collected **if the Python garbage
collector runs before the Python program exits**).

In doubt, users can always call the :func:`detach
<py4j.java_gateway.JavaGateway.detach>` function on the Python gateway to
explicitly delete a reference on the Java side. A call to `gc.collect()` also
usually works.

**Python objects sent to the Java side (callback)**

Every time a Python object is sent to the Java side, a reference to this object
is kept on the Python side (by a :class:`PythonProxyPool
<py4j.java_callback.PythonProxyPool>`). Once a python object is garbage
collected on the Java side, a message is sent to the Python side to remove the
reference to the Python object. When a gateway is shut down, the remaining
references are removed from the Python VM.

Unfortunately, there is no guarantee that the garbage collection message will
ever be sent to the Python side (it usually works on Sun/Oracle VM). It might
thus be necessary to manually remove the reference to the Python objects. Some
helper functions will be developed in the future, but it is unlikely that
garbage collection will be guarenteed because of the specifications of Java
finalizers (which are surprisingly worse than Python finalizer strategies).

.. _adv_threading:

Py4J Threading and connection model
-----------------------------------

In its default mode, Py4J allocates one thread per connection. The design of
Py4j is symmetrical on the Python and Java sides. A Python GatewayClient
communicates with the Java GatewayServer and is then associated with a
GatewayConnection. A Java CallbackClient (for callbacks) communicates with the
Python CallbackServer and is then associated with a CallbackConnection. A
connection runs in the calling thread.

And now, for the details:

**On the Python side: calling Java**

Py4J on the Python side does not explicitly create a thread to call Java
methods. When a method is called, a connection to the Java GatewayServer is
established in the calling thread. If multiple threads are calling Java methods
concurrently, Py4J will ensure that each thread has its own connection by
requesting more connections.

To be extra clear: if you only call Java, Py4J on the Python side will never
create a thread.

To be extra extra clear: Py4J is thread-safe so if you use a JavaGateway from
multiple threads that **you created**, Py4J will make manage the network
resources appropriately.

**On the Python side: receiving callbacks from Java**

Py4J explicitly creates a thread to run the
:class:`CallbackServer <py4j.java_gateway.CallbackServer>`, which accepts
callback connection requests, and a thread for each callback connection
request. As long as there is no concurrent callback from the Java side, the
same callback connection/thread will be used.

These threads are necessary to prevent deadlocks. For example, if we only had a
single thread to handle callbacks from Java, Py4J would deadlock as soon as it
would encounter an indirect recursion between Java and Python functions. Early
versions of Py4J made this mistake :-)

**On the Java side: receiving calls from Python**

Py4J explicitly creates a thread to run the GatewayServer, which accepts
connection requests (from a GatewayClient), and a thread for each connection
request. As long as there is no concurrent call from the Python side, the same
connection/thread will be used.

**On the Java side: calling back Python**

Py4J on the Java side does not explicitly create a thread to make a callback to
a Python object. When a callback is called, a connection to the CallbackServer
is established in the calling thread. If **you created** multiple threads in
Java to call back Python concurrently, Py4J will ensure that each thread has
its own CallbackConnection.

**Alternative threading model**

If both sides are making multiple calls to each other (e.g., indirect
recursion), or if you want to control which thread will execute the calls, you
should use the :ref:`single threading model <clientserver>`, which provide a
more efficient threading model.

.. _security:

TLS
---

Py4J supports TLS for both connections from Python to the JVM and the callback
connections to Python. This requires configuring both Java and Python:

**On the Python side**

Use Python's `ssl` module to create an `ssl.SSLContext`. Note that this was
added in Python 2.7, so if you want to use TLS on 2.6 you should investigate
the backports on PyPI. For the connection to the JVM you'll need something
like:

.. code-block:: python

  client_ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLSv1)
  client_ssl_context.verify_mode = ssl.CERT_REQUIRED
  client_ssl_context.check_hostname = True
  client_ssl_context.load_verify_locations(cafile='/path/to/pem/ca/certs')

This `ssl.SSLContext` should be set as the `ssl_context` parameter when
constructing an instanceof of `GatewayParameters`. If you're setting
`check_hostname` to `True` like the code above then the `address` parameter
of the `GatewayParameters` must match (one of) the hostnames in the certificate
the Java `GatewayServer` presents.

For the socket listening for callbacks from the JVM, you'll need something
like:

.. code-block:: python

  server_ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLSv1)
  server_ssl_context.load_cert_chain(
    '/path/to/pem/private/key',
    password='key-password')

This `ssl.SSLContext` should be set as the `ssl_context` parameter when
constructing an instance of `CallbackServerParameters`. You can see a full
example in the test file `py4j-python/src/tests/java_tls_test.py`.

**On the Java side**

Use the `GatewayServer` constructor that takes a `ServerSocketFactory`, and
pass an instance of type `SSLServerSocketFactory`. The easiest way of
constructing one of these is using `SSLServerSocketFactory.getDefault()`,
however for more control construct a `SSLContext`.

To add TLS to callbacks, create a `CallbackClient` with the constructor that
takes a `SSLSocketFactory`. You can get an instance of this via `getDefault()`
or a `SSLContext` instance similarly.

A runnable example is in `py4j.examples.ExampleSSLApplication`.

Authentication
--------------

By default, Py4J does not authenticate client connections. This allows any
user who can open a connection to the Py4J daemons to potentially execute
code as the user running those daemons.

Authentication can be enabled by providing an authentication token to the
different servers. See the API documentation for how to provide the
authentication token through the API.

Py4J leaves it to the application to generate and distribute the authentication
tokens to all the needed processes.

The authentication protocol transfers the token over the socket connection,
so it relies on transport-level encryption for secrecy. This means that for
proper security, connections should use loopback addresses, or use TLS.

Boxing
------

Boxed Java primitives, such as `java.lang.Integer` are unboxed in the JVM and
transmitted as primitives, so they will appear as Python `int`s, not
`JavaObjects`.


Performance
-----------

We track performance with each new release by running a `benchmark suite
<https://github.com/bartdag/py4j-benchmark>`_ that tests various features of
Py4J.

The benchmark data and performance evolution charts generated by `CircleCI, our
continuous integration server
<https://circleci.com/gh/bartdag/py4j-benchmark/>`_, are made `available as
google charts
<https://docs.google.com/spreadsheets/d/14ljMYIESFbOBFe4o_Fy6WirI2P5iCQuTP9fA1BuLMAI/edit?usp=sharing>`_.

The following chart illustrates the progress Py4J made so far for transferring
1 MB byte arrays.

.. raw:: html

    <iframe width="600" height="371" seamless frameborder="0" scrolling="no"
    src="https://docs.google.com/spreadsheets/d/14ljMYIESFbOBFe4o_Fy6WirI2P5iCQuTP9fA1BuLMAI/pubchart?oid=935988429&amp;format=interactive"></iframe>


