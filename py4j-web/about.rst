About Py4J
==========

Py4J is developed by `Barthélémy Dagenais <http://bart.prologique.com>`_. The goal is to enable developers to program in
Python and benefit from easy to use libraries such as `lxml <http://codespeak.net/lxml/>`_ while being able to reuse
useful Java libraries and frameworks such as `PPA <http://www.sable.mcgill.ca/ppa/>`_ and `Eclipse
<http://www.eclipse.org>`_.


Alternatives to Py4J
====================

As opposed to `Jython <http://www.jython.org/>`_, Py4J does not run in the JVM so it does not need to reimplement the
Python language and developers can use any libraries supported by their Python interpreter. Py4J is more focused than
`JPype <http://jpype.sourceforge.net/index.html>`_ because it only supports calls and field references and it does not
attempt to support subclassing of Java types or linking Python threads with Java threads. JPype uses JNI to communicate
with the JVM while Py4J uses plain old sockets, which is more portable in practice.

In terms of performance, Py4J has a bigger overhead than both of the previous solutions, but if performance is critical
to your application, accessing Java objects from Python programs might not be the best idea :-) We plan to evaluate the
performance overhead of Py4J once we have a stable release.


How to get Help
===============

If you want...

* to report a bug or request a feature, create a ticket in `Trac <https://sourceforge.net/apps/trac/py4j/wiki>`_.
* to ask a question, send an email to our `mailing list <https://lists.sourceforge.net/lists/listinfo/py4j-users>`_.
* to contribute to the code, the documentation or anything else, contact Barthélémy Dagenais at *barthe at users dot sourceforge dot net*.
