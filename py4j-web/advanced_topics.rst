Advanced Topics
===============

Accessing Java collections and arrays from Python
-------------------------------------------------

Java collections are automatically mapped to Python collections so that standard Python operations such as slicing work
on Java collections. Here is the mapping of the collection:

=============== ====================== ====================================================
Java Collection Python Collection      Py4J Implementation
=============== ====================== ====================================================
Array           Sequence [#arraynote]_ :class:`JavaArray <py4j.java_collections.JavaArray>`
java.util.List  MutableSequence        :class:`JavaList <py4j.java_collections.JavaList>`
java.util.Set   MutableSet             :class:`JavaSet <py4j.java_collections.JavaSet>`
java.util.Map   MutableMapping         :class:`JavaMap <py4j.java_collections.JavaMap>`
=============== ====================== ====================================================

.. [#arraynote] Py4J allows elements to be modified, which is not the case of true immutable sequences like tuples.

Iterators are currently not automatically converted, except when accessed through a collection (e.g., `for i in list`). 
Java methods are still accessible when using the Python version of a Java collection. Here are some usage examples for
each collection class. These examples do not cover the entire API.

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


Enabling Java objects to call Python objects (callback)
-------------------------------------------------------

Since version 0.3, Py4J allows Java programs to call Python objects. In other words, Python classes can implement a 
Java interface and instances of these classes can be passed to a Java object. In the following example, we will play the
role of a Mad Scientist :sup:`TM` and we will create a program that invokes an operator with two or three random integers.

Here is the code of the main Java program:

.. code-block:: java

  package py4j.examples;

  import java.util.ArrayList;
  import java.util.List;
  import java.util.Random;

  import py4j.GatewayServer;

  public class OperatorExample {

	  public List<Integer> randomBinaryOperator(Operator op) {
		  Random random = new Random();
		  List<Integer> numbers = new ArrayList<Integer>();
		  numbers.add(random.nextInt());
		  numbers.add(random.nextInt());
		  numbers.add(op.doOperation(numbers.get(0), numbers.get(1)));
		  return numbers;
	  }
	  
	  public List<Integer> randomTernaryOperator(Operator op) {
		  Random random = new Random();
		  List<Integer> numbers = new ArrayList<Integer>();
		  numbers.add(random.nextInt());
		  numbers.add(random.nextInt());
		  numbers.add(random.nextInt());
		  numbers.add(op.doOperation(numbers.get(0), numbers.get(1), numbers.get(2)));
		  return numbers;
	  }
	  
	  public static void main(String[] args) {
		  GatewayServer server = new GatewayServer(new OperatorExample());
		  server.start();
	  }

  }


The programs has a main method starting a `GatewayServer`. The entry point, a `OperatorExample` instance, offers two
methods that take as a parameter an `Operator` instance. Each method calls the operator with two or three random 
integers and save the integers and the result in a list. Here is the declaration of `Operator`:


.. code-block:: java

  package py4j.examples;

  public interface Operator {

	  public int doOperation(int i, int j);
	  
	  public int doOperation(int i, int j, int k);
	  
  }


Now, because the Mad Scientist :sup:`TM` is, well, mad, he wants to define an Operator in Python. Here is his little Python 
program:

::

  from py4j.java_gateway import JavaGateway

  class Addition(object):
      def doOperation(self, i, j, k = None):
	  if k == None:
	      return i + j
	  else:
	      return i + j + k
	  
      class Java:
	  interfaces = ['py4j.examples.Operator']

  if __name__ == '__main__':
      gateway = JavaGateway()
      operator = Addition()
      numbers = gateway.entry_point.randomBinaryOperator(operator)
      print(numbers)
      numbers = gateway.entry_point.randomTernaryOperator(operator)
      print(numbers)
      gateway.shutdown()


The `Addition` class is a standard Python class that has one method, `doOperation`. The signature of the method contains 
two parameters and an optional third parameter: this maps with the two overloaded methods in the `Operator` Java 
interface. Each method implementing an overloaded method in a Java interface should accept all possible combinations of 
parameters, otherwise, an exception will be thrown if the Java program tries to call an unsupported method.

Py4J recognizes that the `Addition` class implements a Java interface because it declares an internal class called 
`Java`, which has a member named `interfaces`. This member is a list of string representing the fully qualified name of 
implemented Java interfaces.

Finally, the Python program contains a main method that starts a gateway, initializes an Addition operator and sends it
to the `OperatorExample` instance on the Java side. Py4J takes care of creating the necessary proxies: the `doOperation`
method of the `Addition` class is called in the Java VM, but the method is executed in the Python interpreter.

.. warning:: 
   
   Python classes can only implement Java interfaces. Abstract or concrete classes are not supported and there is no
   plan to support them in the near future because this would probably require instrumenting the bytecode at runtime.
   Java does not natively support dynamic proxies for classes. 

   As a workaround, a subclass of the abstract class could be created on the Java side. The methods of the subclass 
   would call the methods of a custom interface that a Python class could implement.

.. _adv_memory:

Py4J memory model
-----------------

**Java objects sent to the Python side**

Every time a Java object is sent to the Python side, a reference to the object is kept on the Java side (in the Gateway
class). Once the object is garbage collected on the Python VM (reference count == 0), the reference is removed on the
Java VM: if this was the last reference, the object will likely be garbage collected too. When a gateway is shut down,
the remaining references are also removed on the Java VM.

Because Java objects on the Python side are involved in a circular reference (:class:`JavaObject
<py4j.java_gateway.JavaObject>` and :class:`JavaMember <py4j.java_gateway.JavaMember>` reference each other), these
objects are not immediately garbage collected once the last reference to the object is removed (but they are guaranteed
to be eventually collected **if the Python garbage collector runs before the Python program exits**).

In doubt, users can always call the :func:`detach <py4j.java_gateway.JavaGateway.detach>` function on the Python
gateway to explicitly delete a reference on the Java side. A call to `gc.collect()` also usually works.

**Python objects sent to the Java side (callback)**

Every time a Python object is sent to the Java side, a reference to this object is kept on the Python side (by a
:class:`PythonProxyPool <py4j.java_callback.PythonProxyPool>`). Once a python object is garbage collected on the Java
side, a message is sent to the Python side to remove the reference to the Python object. When a gateway is shut down,
the remaining references are removed from the Python VM.

Unfortunately, there is no guarantee that the garbage collection message will ever be sent to the Python side (it
usually works on Sun/Oracle VM). It might thus be necessary to manually remove the reference to the Python objects. Some
helper functions will be developed in the future, but it is unlikely that garbage collection will be guarenteed because
of the specification of Java finalizers (which are surprisingly worse than Python finalizer strategies).

.. _adv_threading:

Py4J Threading and connection model
-----------------------------------

Py4J allocates one thread per connection. The design of Py4j is symmetrical on the Python and Java sides. A Python
communication channel communicates with the Java GatewayServer and is then associated with a GatewayConnection. A Java
communication channel (for callbacks) communicates with the Python CallbackServer and is then associated with a
CallbackConnection. Communication channels run in the calling thread.

And now, for the details:

**On the Python side**

Py4J explicitly creates a thread to run the :class:`CallbackServer<py4j.java_callback.CallbackServer`, which accepts
callback connection requests,  and a thread for each callback connection request. As long as there is no concurrent
callback on the Java side, the same callback connection/thread will be used.

Py4J on the Python side does not explicitly create a thread to call Java methods. When a method is called, a
communication channel (connection to the Java GatewayServer) is established in the calling thread. If multiple threads
are calling Java methods concurrently, Py4J will ensure that each thread has its own communication channel.

**On the Java side**

Py4J explicitly creates a thread to run the GatewayServer, which accepts connection requests (from a communication
channel), and a thread for each connection request. As long as there is no concurrent calls on the Python side, the same
connection/thread will be used.

Py4J on the Java side does not explicitly create a thread to make a callback to a Python object. When a callback is
called, a communication channel (connection to the CallbackServer) is established in the calling thread. If multiple
threads are calling Python callbacks concurrently, Py4J will ensure that each thread has its own communication channel.