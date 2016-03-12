Changelog
=========

The changelog describes in plain English the changes that occurred between Py4J
releases.

Py4J 0.9.2
----------

- Release date: March 12th 2016
- Python side: added a guard condition in object finalization to prevent
  exceptions when the program exits (long standing bug!).
- Java side: Py4J will use the current thread's classloader instead of the root
  classloader to load a class from a fully qualified name. This behavior is
  configurable globally in py4j.reflection.ReflectionUtil. thanks to
  @JoshRosen.
- Documentation: made a simpler and easier to understand example of callback
  (Java calling Python)

Py4J 0.9.1
----------

- Release date: January 9th 2016
- Python side: it is now possible to retrieve the listening address and port of
  the CallbackServer. This is useful if CallbackServer is bound to port 0.
- Python side: The daemonize_redirect flag is not set to True by default to
  preserve backward compatibility prior to 0.9.
- Python side: JavaGateway.shutdown() no longer raises unecessary NoneType
  exceptions.
- Python side: if you attempt to access an inexistent object on the Java side,
  you will receive a more meaningful exception.
- Python side: the callback server was not correctly closing sockets and it was
  possible to leak sockets until no more were available. This has been fixed.
- Java side: the finalization code telling the Python side that it can garbage
  collect a python proxy should not longer block (major bug fix).
- Java side: After GatewayServer is launched, it is :ref:`now possible to
  change the address:port where the CallbackClient connects <dynamic_ports>`.
- Added a comment in an empty init file so 7zip does not report on error on
  Windows (go figure :-) )
- We moved from Travis CI to Circle CI and the automated tests now reliably
  pass.
- `tickets closed for 0.9.1 release
  <https://github.com/bartdag/py4j/issues?q=is%3Aissue+milestone%3A0.9.1+is%3Aclosed>`_


Py4J 0.9
--------

- Release date: July 25th 2015
- Python side: constructor parameters have been deprecated in favor of
  GatewayParameters and CallbackServerParameters. This was necessary because
  the number of configuration options is growing fast. Old parameters will be
  supported until Py4J 1.0 (at least two more minor versions).
- Python side: IDEs and interactive interpreters such as IPython can now get
  help text/autocompletion for Java classes, objects, and members. This makes
  Py4J an ideal tool to explore complex Java APIs (e.g., the Eclipse API).
  Thanks to @jonahkichwacoders
- Python side: the callback gateway server (necessary for Java to call back
  Python functions) can be daemonized and can be started after the main
  JavaGateway is started.
- Python side: py4j.java_gateway.launch_gateway has now a cleaner
  implementation that discards stdout and stderr output by default. It is also
  possible to redirect the output from these channels to separate files,
  deques, or queues. Thanks to @davidcsterratt for finding the root cause and
  work on the fix.
- It is now possible to install Py4J from git with pip: pip install
  git+https://github.com/bartdag/py4j.git
- The Eclipse components of Py4J have been moved to another repository. Existing
  forks and pull requests can still use the @before-eclipse-split branch until
  Py4J reaches 1.0. Fixes won't be backported to this branch, but pull requests
  will be merged by the main maintainer to @master if requested.
- Major cleanup of Python source code to make it fully flake8 (pep8 + pyflakes)
  compliant. This should be easier to contribute now.
- Major test cleanup effort to make Python tests more reliable. Testing Py4J is
  difficult because there are many versions of Python and Java to test and
  Python 2.6 lacks many interesting test features. Effort to make tests even
  more robust will continue in the next milestone.
- We introduced a :doc:`contributing guide and an implicit contributor license
  agreement </contributing>` that indicates that anyone contributing to Py4J
  keeps the copyright of the contribution but gives a non-revokable right to
  license the code using Py4J's license (3-clause BSD). The copyright statement
  has been changed to "Copyright (c) 2009-2015, Barthelemy Dagenais and
  individual contributors.  All rights reserved." to make it clear that
  individual contributors retain copyrights of their contributions. An
  AUTHORS.txt file has been added to the repository to keep track of
  contributors: if your name is not in the file and you have contributed to
  Py4J, do not hesitate to write on the mailing list or open a pull request.
- Cleaned up the doc that was referring to broken links or refactored classes.
  Long-time users may want to review the :doc:`advanced topics
  </advanced_topics>` page.
- Added support for `Python Wheels <https://pypi.python.org/pypi/wheel>`_.
- We have a new website: `https://www.py4j.org <https://www.py4j.org>`_
- We have a new blog: `https://blog.py4j.org <https://blog.py4j.org>`_
- Eclipse features have moved to: `http://eclipse.py4j.org
  <http://eclipse.py4j.org>`_
- We have a `new mailing list
  <https://groups.google.com/a/py4j.org/forum/#!forum/py4j/join>`_.
- `github 0.9 milestone
  <https://github.com/bartdag/py4j/issues?q=is%3Aissue+milestone%3A0.9+is%3Aclosed>`_

Py4J 0.8.2.1
------------

- Release date: July 27th 2014
- Fixed a test that used an assert method that does not exist in Python 2.6

Py4J 0.8.2
----------

- Release date: July 27th 2014
- Fixed constructors not being able to pass proxy (python classes implementing
  Java interfaces)
- Java 6 compatibility was restored in compiled jar file.
- Fixed unit tests for JDK 8
- Added a few extra paths to find_jar_path
- `github 0.8.2 milestone
  <https://github.com/bartdag/py4j/issues?milestone=11&state=closed>`_


Py4J 0.8.1
----------

- Release date: December 26th 2013
- Fixed a bug in type inference when interface hierarchy is deeper than
  abstract class hierarchy.
- Added a utility method ``is_instance_of`` in py4j.java_gateway to determine
  if a JavaObject is an instance of a class.
- Released Py4J in central Maven repository.
- `github 0.8.1 milestone
  <https://github.com/bartdag/py4j/issues?milestone=8&page=1&state=closed>`_


Py4J 0.8
--------

- Release date: June 15th 2013
- Major fix to the Java byte[] support. Thanks to @agronholm for spotting
  this subtle but major issue and thanks to @fdinto from The Atlantic for
  providing a patch!
- Ability to fail early if the py4j.java_gateway.JavaGateway cannot connect to
  the JVM.
- Added support for long primitives, BigDecimal, enum types, and inner classes
  on the Java side.
- Set saner log levels
- Many small bug fixes and API enhancements (backward compatible).
- Wrote a section in the FAQ about security concerns and precautions with Py4J.
- Added support of `Travis-CI <https://travis-ci.org/bartdag/py4j>`_ and
  cleaned up the test suite to remove hardcoded paths.
- `github 0.8 milestone
  <https://github.com/bartdag/py4j/issues?milestone=7&page=1&state=closed>`_

Py4J 0.7
--------

- Release date: June 2nd 2011
- Major refactoring to support Python 3. Thanks to Alex Grönholm for his
  patch.
- The build and setup files have been totally changed. Py4J no longer requires
  Paver to build and everything is done through ant. The setup.py file only
  uses distutils.
- Added support for Java byte[]: byte array are passed by value and converted
  to bytearray or bytes.
- Py4J package name changed from Py4J to py4j.
- Bug fixes in the Python callback server and unicode support.
- `github 0.7 milestone
  <https://github.com/bartdag/py4j/issues/labels/v0.7>`_

Py4J 0.6
--------

- Release date: February 17th 2011
- Added new exception ``Py4JJavaError`` that enables Python client programs to access
  instance of Java exception thrown in the Java client code.
- Improved Py4J setup: no more warnings displayed when installing Py4J.
- Bug fixes and API additions.
- `github 0.6 milestone
  <https://github.com/bartdag/py4j/issues/labels/v0.6>`_

Py4J 0.5
--------

- Release date: November 30th 2010
- Added the ability to import packages (e.g., ``java_import(gateway.jvm, 'java.io.*')``)
- Added support for pattern filtering in ``JavaGateway.help()`` (e.g., ``gateway.help(obj,'get*Foo*Bar')``)
- Added support for automatic conversion of Python collections (list, set,
  dictionary) to Java collections. User ``JavaGateway(auto_convert=True)`` or
  an explicit convertor.
- Created two Eclipse features: one embeds the Py4J
  Java library. The other
  provides a default GatewayServer that is started when Eclipse starts. Both
  features are available on the new Py4J Eclipse update site:
  ``http://www.py4j.org/py4j_eclipse``
- Redesigned the module decomposition of Py4J: there are no more mandatory circular dependencies among modules.
- `github 0.5 milestone
  <https://github.com/bartdag/py4j/issues/labels/v0.5>`_

Py4J 0.4
--------

- Release date: September 19th 2010
- Polishing of existing features: fields can be set (not just read), None is accepted as a method parameter, methods are sorted alhabetically in gateway.help(), etc.
- Java Exception Stack Trace are now propagated to Python side.
- Changed **interfaces** member in Callback classes to **implements**.
- Internal refactoring to adopt clearer terminology and make Py4J protocol extensible.
- Many bug fixes: most are related to the callback feature.
- `github 0.4 milestone <https://github.com/bartdag/py4j/issues/labels/v0.4>`_

Py4J 0.3
--------

- Release date: April 27th 2010
- Added support for Java arrays and set.
- Added support for callbacks: Java objects can now call back Python objects.
- Completely redesigned threading and connection model of Py4J to allow multiple threads and callbacks on both side.
- Refactored the memory management to ensure best effort garbage collection.
- `github 0.3 milestone <https://github.com/bartdag/py4j/issues/labels/v0.3>`_

Py4J 0.2
--------

- Release date: February 11th 2010
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

- Release date: December 23rd 2009
- This is the first release.
- Basic features like connecting to a JVM and calling methods are implemented.
- Java List is converted to a Python List.
- Field access, constructors, and static classes are **NOT** accessible yet.
- Dictionary and Set are only accessible through the Java Map and Set interface for now.
- Arrays can be referenced, but individual items cannot be accessed yet.
- `github 0.1 milestone <https://github.com/bartdag/py4j/issues/labels/v0.1>`_
