Changelog
=========

The changelog describes in plain English the changes that occurred between Py4J releases.

Py4J 0.6
--------

- Added new exception ``Py4JJavaError`` that enables Python client programs to access
  instance of Java exception thrown in the Java client code.
- Improved Py4J setup: no more warnings displayed when installing Py4J.
- Bug fixes and API additions.
- `github 0.6 milestone
  <https://github.com/bartdag/py4j/issues/labels/v0.6>`_

Py4J 0.5
--------

- Added the ability to import packages (e.g., ``java_import(gateway.jvm, 'java.io.*')``)
- Added support for pattern filtering in ``JavaGateway.help()`` (e.g., ``gateway.help(obj,'get*Foo*Bar')``)
- Added support for automatic conversion of Python collections (list, set,
  dictionary) to Java collections. User ``JavaGateway(auto_convert=True)`` or
  an explicit convertor.  
- Created two Eclipse features: one embeds the Py4J
  Java library. The other
  provides a default GatewayServer that is started when Eclipse starts. Both
  features are available on the new Py4J Eclipse update site:
  ``http://py4j.sourceforge.net/py4j_eclipse`` 
- Redesigned the module decomposition of Py4J: there are no more mandatory circular dependencies among modules.
- `github 0.5 milestone
  <https://github.com/bartdag/py4j/issues/labels/v0.5>`_

Py4J 0.4
--------

- Polishing of existing features: fields can be set (not just read), None is accepted as a method parameter, methods are sorted alhabetically in gateway.help(), etc.
- Java Exception Stack Trace are now propagated to Python side.
- Changed **interfaces** member in Callback classes to **implements**.
- Internal refactoring to adopt clearer terminology and make Py4J protocol extensible.
- Many bug fixes: most are related to the callback feature.
- `github 0.4 milestone <https://github.com/bartdag/py4j/issues/labels/v0.4>`_

Py4J 0.3
--------

- Added support for Java arrays and set.
- Added support for callbacks: Java objects can now call back Python objects.
- Completely redesigned threading and connection model of Py4J to allow multiple threads and callbacks on both side.
- Refactored the memory management to ensure best effort garbage collection.
- `github 0.3 milestone <https://github.com/bartdag/py4j/issues/labels/v0.3>`_

Py4J 0.2
--------

- It is now possible to call constructors and reference static members: use the `jvm` member of a `JavaGateway` object.
- Java Map is converted to a Python Dictionary.
- Field access is supported through the ``get_field`` function or the ``auto_field=True`` member of `JavaGateway`.
- Obtain an interactive help page with ``JavaGateway.help(object)``.
- Set is only accessible through the Java Set interface for now.
- Arrays can be referenced, but individual items can only be accessed with this workaround: ``gateway.jvm.java.lang.reflect.Array.get(object,index)``.
- Complete rewrite of the reflection engine on the Java side for more flexibility.
- Improved memory model: no more memory leak caused by Py4J.
- New concurrency model: Py4J is now thread-safe.
- `github 0.2 milestone <https://github.com/bartdag/py4j/issues/labels/v0.2>`_

Py4J 0.1
--------

- This is the first release.
- Basic features like connecting to a JVM and calling methods are implemented.
- Java List is converted to a Python List.
- Field access, constructors, and static classes are **NOT** accessible yet.
- Dictionary and Set are only accessible through the Java Map and Set interface for now.
- Arrays can be referenced, but individual items cannot be accessed yet.
- `github 0.1 milestone <https://github.com/bartdag/py4j/issues/labels/v0.1>`_
