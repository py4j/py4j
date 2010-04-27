Changelog
=========

The changelog describes in plain English the changes that occurred between Py4J releases. Please look at the `roadmap
<http://sourceforge.net/apps/trac/py4j/roadmap?show=all>`_ for more detailed information. 

Py4J 0.3
--------

- Added support for Java arrays and set.
- Added support for callbacks: Java objects can now call back Python objects.
- Completely redesigned threading and connection model of Py4J to allow multiple threads and callbacks on both side.
- Refactored the memory management to ensure best effort garbage collection.
- `Trac 0.3 milestone <http://sourceforge.net/apps/trac/py4j/milestone/0.3>`_

Py4J 0.2
--------

- It is now possible to call constructors and reference static members: use the `jvm` member of a `JavaGateway` object.
- Java Map is converted to a Python Dictionary.
- Field access is supported through the `get_field` function or the `auto_field=True` member of `JavaGateway`.
- Obtain an interactive help page with `JavaGateway.help(object)`.
- Set is only accessible through the Java Set interface for now.
- Arrays can be referenced, but individual items can only be accessed with this workaround: `gateway.jvm.java.lang.reflect.Array.get(object,index)`.
- Complete rewrite of the reflection engine on the Java side for more flexibility.
- Improved memory model: no more memory leak caused by Py4J.
- New concurrency model: Py4J is now thread-safe.
- `Trac 0.2 milestone <http://sourceforge.net/apps/trac/py4j/milestone/0.2>`_

Py4J 0.1
--------

- This is the first release.
- Basic features like connecting to a JVM and calling methods are implemented.
- Java List is converted to a Python List.
- Field access, constructors, and static classes are **NOT** accessible yet.
- Dictionary and Set are only accessible through the Java Map and Set interface for now.
- Arrays can be referenced, but individual items cannot be accessed yet.
- `Trac 0.1 milestone <http://sourceforge.net/apps/trac/py4j/milestone/0.1>`_