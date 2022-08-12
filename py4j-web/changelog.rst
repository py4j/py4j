Changelog
=========

The changelog describes in plain English the changes that occurred between Py4J
releases.

Py4J 0.10.9.7
-------------

- Release date: August 12th 2022
- Python side: Detach Java objects only when _detach method exists
- Java side: Add support for Java 11/17
- `tickets closed for 0.10.9.7 release
  <https://github.com/bartdag/py4j/milestone/33?closed=1>`_

Py4J 0.10.9.6
-------------

- Release date: August 11th 2022
- Python side: Migrate nosetest to pytest
- `tickets closed for 0.10.9.6 release
  <https://github.com/bartdag/py4j/milestone/32?closed=1>`_

Py4J 0.10.9.5
-------------

- Release date: March 18th 2022
- Python side: added the official support of Python 3.10
- `tickets closed for 0.10.9.5 release
  <https://github.com/bartdag/py4j/milestone/31?closed=1>`_

Py4J 0.10.9.4
-------------

- Release date: March 16th 2022
- Python side: clean leaked connections in pinned thread mode when threads are finished.
- Python side: enforced documentation build have no warnings.
- Automated documentation build with publising.
- Fixed all tests that are flaky in GitHub Actions.
- `tickets closed for 0.10.9.4 release
  <https://github.com/bartdag/py4j/milestone/30?closed=1>`_

Py4J 0.10.9.3
-------------

- Release date: November 20th 2021
- Python side: added Python 3.8 and 3.9 to supported versions.
- Python side: catch KeyboardInterrupt to prevent connection and memory leaks.
  Thanks to Hyukjin Kwon for the thorough investigation and fix.
- Java side: upgrade JUnit version.
- Switched from Travis CI to Github Actions. Many thanks to Josh Rosen for
  saving the CI pipeline of Py4J!
- Removed professional services.
- `tickets closed for 0.10.9.3 release
  <https://github.com/bartdag/py4j/milestone/29?closed=1>`_

Py4J 0.10.9.2
-------------

- Release date: February 27th 2021
- Python side: add use_shell parameter in launch_gateway
- Python side: fixed documentation of CallbackServerParameters &
  PythonParameters
- `tickets closed for 0.10.9.2 release
  <https://github.com/bartdag/py4j/milestone/28?closed=1>`_

Py4J 0.10.9.1
-------------

- Release date: September 7th 2020
- Java side: fixed a regression in GatewayServer that ignored the passed port.
- `tickets closed for 0.10.9.1 release
  <https://github.com/bartdag/py4j/milestone/27?closed=1>`_


Py4J 0.10.9
-----------

- Release date: January 25th 2019
- Python side: launch_gateway can now optionally returns the Popen process
  object.
- Python side: launch_gateway can now set the current working directory.
- Python side: improved support for Python 3.7 by importing from
  collections.abc.
- Python side: improved support for Python 3.7 by correctly escaping special
  characters in docstrings.
- Python side: magic members such as __name__ are no longer sent to the Java
  side. An AttributeError exception is instead raised.
- Java side: set explicit Gradle version and use gradlew to avoid issues with
  more recent versions of Gradle.
- Java side: the GatewayServer CLI no longer requires an explicit port and can
  listen to the default port.
- Java side: Travis no longer tries to build Py4J with Java 6 and 7. These
  versions are no longer available in default images.
- Java side: array elements can be set to None/null for non-primitive arrays.
- `tickets closed for 0.10.9 release
  <https://github.com/bartdag/py4j/issues?q=is%3Aissue+milestone%3A0.10.9+is%3Aclosed>`_

Py4J 0.10.8 and Py4J 0.10.8.1
-----------------------------

- Release date: October 21st 2018
- Python side: Py4J now supports Python 3.7.
- Python side: Py4J no longer supports Python 2.6. Thanks to @hugovk for the
  patch.
- Python side: The Python ClientServer now uses a mix of deque + sleep instead
  of a Queue to send garbage collection requests to the Java side. This solved
  a subtle deadlock issue that could occur because of a `bug in CPython
  <https://bugs.python.org/issue14976>`_. This CPython bug has existed for many
  years and was finally fixed in Python 3.7. Because Py4J supports Python 2.7+,
  we had to use an alternative to Queue.
- Python side: Python Entry Point can no longer be accidentally garbage
  collected. This matches the behavior of GatewayServer entry point that could
  never be accidentally garbage collected. Thanks to `App Orchid
  <https://www.apporchid.com/>`_ for funding the work through our professional
  services program.
- Python side: exceptions should no longer escape garbage collection calls. In
  the past, Py4J was trying to log exceptions that occurred during garbage
  collection, but the logger can itself be already garbage collected. If this
  occurs, the exception will be caught instead of being propagated into the
  user program. Thanks to `Thermo-Calc Software <https://www.thermocalc.com/>`_
  for funding the work through our professional services program.
- Python side: added a note in the docstring that str(py4j_java_error) may
  fail in Python 2.7 if unicode is returned. Thanks to @HyukjinKwon for the
  patch.
- Java side: Java 6 is no longer included in the test suite considering the
  difficulty in managing the dependencies and requirements of the build
  toolchain (e.g., gradle, TravisCI). We will accept patches from anyone
  wanting to continue supporting Java 6 for the foreseeable future. Java 6 will
  be officially dropped along with Java 7 when Java 8 will become the minimum
  version required by Py4J (no date yet, but please make yourself heard if you
  require Java 7!).
- Project: we switched again from CircleCI to TravisCI following the end of
  life of CircleCI 1.0.
- `tickets closed for 0.10.8 release
  <https://github.com/bartdag/py4j/milestone/25?closed=1>`_


Py4J 0.10.7
-----------

- Release date: April 30th 2018
- Both sides: Python exception trace is now propagated to the Java side as a
  string. If the Python exception is caused by a Java exception it is possible
  to rethrow the Java exception on the Java side, making it easy to implement
  Java protocols in Python (e.g., Iterator protocol). Because this could break
  backward compatibily, Java exceptions are only rethrown if
  propagate_java_exceptions is True in CallbackServerParameters. Thanks to
  @batterseapower for the patch.
- Both sides: small fixes to the code examples on documentation front page.
- Both sides: added optional authentication method that requires a token at the
  start of every connection. Thanks to @vanzin for initial patch and follow up.
- Python side: support for Python 3.6
- Python side: removed two spurious line breaks in sub commands.
- Java side: as part of the addition of the authentication method, made
  protocol stricter: unknown commands now raise an exception and stops a
  connection.
- Java side: ClientServer now uses the passed SocketFactory in
  PythonClient instead of always falling back to the default socket factory.
- Java side: support for Gradle 4.x
- `tickets closed for 0.10.7 release
  <https://github.com/bartdag/py4j/milestone/24?closed=1>`_


Py4J 0.10.6
-----------

- Release date: July 5th 2017
- Python side: refactored memory management in ClientServer. Garbage collection
  requests are now handled by a dedicated thread, i.e., when a JavaObject is no
  longer used on the Python side, a garbage collection request is sent to a
  queue and a management thread is responsible for sending these requests to
  the Java side.
- Java side: surrounded connection array access in ClientServer with lock to
  prevent concurrent modification.
- Java side: fixed deep inheritance argument resolution
- Java side: fixed regression where Python proxy tried to convert null values.
- Java side: added a GatewayServer constructor that accepts a Gateway instance.
- `tickets closed for 0.10.6 release
  <https://github.com/bartdag/py4j/milestone/23?closed=1>`_


Py4J 0.10.5
-----------

- Release date: May 28th 2017
- Python side: added path for pip install --user
- Python side: doubles are no longer truncated in Python 2.7
- Python side: passing integers larger than Long.MAX_VALUE no longer stalls
  connection.
- Java side: spurious server error signal no longer sent when GatewayServer is
  shutting down.
- Java side: allow disabling automatic connection cleanup in CallbackClient.
- Java side: return types of Python proxies are correctly converted to the
  expected type (e.g., a double can be converted to a float)
- `tickets closed for 0.10.5 release
  <https://github.com/bartdag/py4j/milestone/22?closed=1>`_


Py4J 0.10.4
-----------

- Release date: October 14th 2016
- Setting a value in a Java array now correctly converts the Python type to
  Java type. For example, it is now possible to set a value in a java float
  array. Before that change, Python type and Java Array value type had to
  exactly match.
- Java side: the serverError callback in the GatewayServerListener is no longer
  called when "java.net.SocketException: Socket closed" exception is raised
  when the GatewayServer is shutting down. The server_connection_error signal
  on the Python side was already ignoring that spurious error.
- `tickets closed for 0.10.4 release
  <https://github.com/bartdag/py4j/milestone/21?closed=1>`_


Py4J 0.10.3
-----------

- Release date: July 31st 2016
- Python side: Added java_path option in launch_gateway. If None, will detect
  whether JAVA_HOME is set and use ``JAVA_HOME/bin/java`` instead of ``java``
  to launch the JVM.
- Python side: added ``create_new_process_group`` in ``launch_gateway``. If
  True, will launch the JVM in a new process group which (1) prevents signals
  sent to the parent Python process to propagate to the child JVM process, and
  (2) does not kill the Java process if the Python process dies. This is a
  useful option if you want to interrupt a long-running Java method call from
  Python and you launched the JVM using launch_gateway. Such interruption has
  always been possible if you launched the JVM outside of Python.
- Python side: introduced a small signals library. Users can now connect to
  signals emitted by the CallbackServer, which mirrors the events sent by
  GatewayServer on the Java side.
- Python side: added ``get_java_class`` function which returns the
  java.lang.Class of a JavaClass. Equivalent to calling .class in Java, but
  from Python.
- Python side: fixed the project root setup.py, which allows users to install
  Py4J with pip from the git repository. The root setup.py relied on compiled
  jars that are no longer provided. It now uses gradlew to build the required
  jars during the installation. Works on both Linux and Windows :-)
- Python side: fixed type conversion when passing a large negative integer.
- Java side: added defensive programming to prevent concurrent modification of
  the listeners list (in case a listener removes itself after receiving an
  event).
- Both sides: added more memory leak tests and fixed a potential memory leak
  related to listeners.
- Both sides: added support for IPv6.
- Created an official `benchmark program
  <https://github.com/bartdag/py4j-benchmark>`_ to track Py4J speed. The
  results are available as a `Google sheet and charts
  <https://docs.google.com/spreadsheets/d/14ljMYIESFbOBFe4o_Fy6WirI2P5iCQuTP9fA1BuLMAI/edit?usp=sharing>`_.
- Eclipse: Replaced ``Eclipse-BuddyPolicy: global`` by ``DynamicImport-Package:
  *`` for greater compatibility with other OSGi frameworks.
- `tickets closed for 0.10.3 release
  <https://github.com/bartdag/py4j/issues?q=milestone%3A0.10.3+is%3Aclosed>`_

Py4J 0.10.2.1
-------------

- Release date: June 20th 2016
- Python side: re-added missing parameter in GatewayClient constructor.
- `tickets closed for 0.10.2.1 release
  <https://github.com/bartdag/py4j/issues?q=milestone%3A0.10.2.1+is%3Aclosed>`_


Py4J 0.10.2
-----------

- Release date: June 19th 2016
- Both sides: added memory management options to disable garbage collection.
  This is useful if you create many short-lived py4j client/server pairs.
- Both sides: fixed ClientServer to allow users to creater multiple
  ClientServer instances. Thanks to @jonahkichwacoders for reporting the bug
  and helping diagnosing the issue.
- Both sides: it is now possible to specify a python entry point when creating
  a CallbackServer. The CallbackClient on the Java side can then access the
  python entry point and drive the conversation. See the :ref:`advanced topics
  guide <python_entry_point>` for more information.
- Both sides: fixed memory leak issue with ClientServer and potential deadlock
  issue by creating a memory leak test suite.
- Both sides: fixed retry logic by only retrying if an error occurs on write
  (send command). Thanks to @jonahkichwacoders for raising the issue.
- Both sides: the assemble gradle task, the Java test suite and the Python test
  suite now runs correctly on Windows.
- Java side: added GatewayServerBuilder and ClientServerBuilder to ease the
  creation of these instances with many options. Thanks to @jonahkichwacoders.
- A link to the contributing guide now appears when opening pull requests or
  issues.
- `tickets closed for 0.10.2 release
  <https://github.com/bartdag/py4j/issues?q=milestone%3A0.10.2+is%3Aclosed>`_

Py4J 0.10.1
-----------

- Release date: May 11th 2016
- Major performance fix: the Python side is now using default buffering when
  reading responses from the Java side. This is particularly important if you
  transfer large parameters (large strings or byte arrays). A simple benchmark
  found that repeatedly sending 10 MB strings went from 99 seconds to 1 second.
  Thanks to @kaytwo for finding this bug and suggesting a fix.
- Both the Java and the Python libraries are now available as OSGi bundles.
  Thanks to `kichwacoders <https://kichwacoders.com/>`_ for
  funding the work.
- The 0.10.0 jar uploaded to PyPI wrongly required Java 8. The Java
  compatibility has been restored to 1.6. Thansk to @agronholm for finding this
  bug.
- Added the __version__ attribute in the py4j package to conform to PEP396.
  Thanks to @lessthanoptimal for reporting this bug.
- `tickets closed for 0.10.1 release
  <https://github.com/bartdag/py4j/issues?q=milestone%3A0.10.1+is%3Aclosed>`_

Py4J 0.10.0
-----------

- Release date: April 18th 2016
- Added a new threading model that is more efficient with indirect recursion
  between Java and Python and that enables users to control which thread will
  execute calls. Thanks to `kichwacoders <https://kichwacoders.com/>`_ for
  funding the implementation and providing the initial idea.
- Added TLS support to encrypt the communication between both sides. Thanks to
  @njwhite.
- Added initial byte stream support so Python can consume Java byte streams
  more efficiently. Support is still preliminary and subject to change in the
  future, but it provides a good base to build on. See these `Python unit test
  <https://github.com/bartdag/py4j/blob/9d3a520d9a31ea39534d2d290eaa7da5dc683ed5/py4j-python/src/py4j/tests/java_gateway_test.py#L547>`_
  and `Java example class
  <https://github.com/bartdag/py4j/blob/9d3a520d9a31ea39534d2d290eaa7da5dc683ed5/py4j-java/src/test/java/py4j/examples/ExampleClass.java#L192>`_
  for a small example. Thanks to @njwhite.
- Java side: converted build script from ant to gradle. Introduced Java coding
  conventions and static code analysis. See :ref:`Java Coding Conventions
  <java_conventions>` for more details.
- Java side: it is now possible to build a osgi bundle and an Eclipse update
  site from Py4J source. See :ref:`using Py4J with Eclipse <eclipse_features>`
- `tickets closed for 0.10.0 release
  <https://github.com/bartdag/py4j/issues?q=milestone%3A0.10+is%3Aclosed>`_

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
- `tickets closed for 0.9.2 release
  <https://github.com/bartdag/py4j/issues?q=milestone%3A0.9.2>`_

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
