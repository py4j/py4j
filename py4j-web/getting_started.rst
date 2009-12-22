Getting Started with Py4J
=========================

This short tutorial assumes that you have already :ref:`installed <install_instructions>` Py4J and that you are using
the latest version. In this tutorial, we will write a simple Stack class in Java and then, we will write a Python
program that accesses the stack.

Writing the Java Program
------------------------

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


.. code-block:: java

  package py4j.examples;

  import py4j.DefaultGateway;
  import py4j.GatewayServer;

  public class StackGateway extends DefaultGateway {

	  public Stack createNewStack() {
		  return new Stack();
	  }
	  
	  public void main(String[] args) {
		  GatewayServer gateway = new GatewayServer(new StackGateway());
		  gateway.start();
		  System.out.println("Gateway Server Started");
	  }
	  
  }

.. warning:: 
   
   if you encounter java.net.BindException: Address already in use


Writing the Python Program
--------------------------

:: 

  >>> from py4j.java_gateway import JavaGateway
  >>> gateway = JavaGateway()
  >>> stack = gateway.createNewStack()
  >>> stack.push("First %s" % ('item'))
  >>> stack.push("Second item")        
  >>> stack.pop()                                        
  u'Second item'                                         
  >>> stack.pop()                                        
  u'First item'                                          
  >>> stack.pop()                                        
  Traceback (most recent call last):                     
    File "<stdin>", line 1, in <module>                  
    File "py4j/java_gateway.py", line 161, in __call__   
      return_value = get_return_value(answer, self.comm_channel, self.target_id, self.name)
    File "py4j/java_gateway.py", line 74, in get_return_value                              
      raise Py4JError('An error occurred while calling %s%s%s' % (target_id, '.', name))   
  py4j.java_gateway.Py4JError: u'An error occurred while calling o0.pop'                   
  >>> stack.push('First item')                                                             
  >>> internal_list = stack.getInternalList()
  >>> len(internal_list)                     
  1
  >>> internal_list.append('Second item')
  >>> internal_list
  [u'First item', u'Second item']
  >>> stack.getInternalList()
  [u'First item', u'Second item']
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
  >>> gateway.getMethodNames(stack)
  [u'getClass', u'equals', u'notify', u'hashCode', u'toString', u'pushAll', u'pop', u'wait', u'push', u'notifyAll', u'getInternalList']

.. note:: 

   If the logging information in the java console drives you crazy, you can...