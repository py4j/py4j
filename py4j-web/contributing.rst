Contributing to Py4J
====================

.. contents:: Summary
   :backlinks: entry
   :local:


General Conventions
-------------------

Contributions to Py4J are always welcome, but to accelerate the review process,
make sure that your contribution includes:

1. At least one unit test in Python and/or Java.
2. A docstring or javadoc comment if you create new public classes, methods or
   functions.
3. Some code examples in the py4j-web documentation subproject if you are
   introducing new features.

.. _python_conventions:

Python Coding Conventions
-------------------------

We follow pep8 rather stricly:

1. We use spaces instead of tab.
2. We use four-space indents.
3. Line length is 80
4. Code must pass the default flake8 tests (pep8 + pyflakes)

Code must be compatible with from Python 2.6 to the newest released version of
Python.

If external libraries must be used, they should be wrapped in a mechanism that
by default does not require them (e.g., conditional imports, graceful
degradation, etc.).

Libraries used for testing and contributing (flake8, nose, tox) can be
installed with pip:


.. code-block:: bash

  pip install -r py4j-python/requirements-test.txt

  # Run flake8
  flake8


.. _java_conventions:

Java Coding Conventions
-----------------------

We use Eclipse code formatting conventions (see `py4j.formatter.xml
<https://raw.githubusercontent.com/bartdag/py4j/master/py4j-java/py4j.formatter.xml>`_
and `py4j.importorder
<https://raw.githubusercontent.com/bartdag/py4j/master/py4j-java/py4j.importorder>`)
that can be used in Eclipse and IntelliJ IDEs.

In summary we use:

1. We use tabs rather than spaces to indent the Java code.
2. Most expressions (conditionals, loops, try/catch) are always wrapped with
   curly brackets.

You can format your code using gradle and Java 8:

.. code-block:: bash

  ./gradlew spotlessJavaApply

We use `FindBugs <http://findbugs.sourceforge.net/>`_ on the main source code
(not the test source code) and any warnings must be corrected before a pull
request will be accepted.


Testing Python Code
-------------------

On the Python side, we use nose and tox:

.. code-block:: bash

  # make sure that the jar file is created
  cd  py4j-java
  ./gradlew clean
  ./gradlew assemble

  # install test requirements
  cd py4j-python
  pip install -r py4j-python/requirements-test.txt

  # Run the full test suite
  nosetests

  # Run only one particular test
  nosetests py4j.tests.java_gateway_test:GatewayLauncherTest.testRedirectToDeque

  # Run all tests on all supported pythons:
  tox

  # Run flake8 checks
  flake8

New code or bug fix should ideally be accompanied by a test case.

Because we start a JVM for most test cases, it may happen that some test fails
because the process was not ready to receive a request. This is a problem we
have been working on for some time now and it has been a few months since the
test suite failed because of synchronization issues. If your tests constantly
fail, then something is wrong with your test!

Testing Java Code
-----------------

We use JUnit to write test cases.

.. code-block:: bash

  cd py4j-java
  ./gradlew clean
  ./gradlew check


.. _license_and_copyrights:

License and Copyrights
----------------------

Py4J does not have an official Contributor License Agreement (CLA), but it is
assumed that as soon as you make a contribution (patch, code suggestion through
any medium, pull requests) to Py4J, you accept that your code will be
redistributed under the current license used by Py4J, i.e., the new BSD
license. This is an irrevocable right to ensure that developers can use Py4J
without the fear of seeing parts removed in the future.

You maintain the full copyrights for your contributions: you are only providing
a license to distribute your code without further restrictions.

The copyright statement in the License has been standardized to:

``Copyright (c) 2009-2016, Barthelemy Dagenais and individual contributors. All
rights reserved.```

Individual contributors are identified in the AUTHORS file. If you have
contributed to Py4J and your name is not in AUTHORS, please open a pull
request!

If you are working for a company while contributing to Py4J, make sure that the
code is yours or that your company agrees with this implied CLA.

This approach is heavily inspired from the `Django Contributor License
Agreement.  <https://www.djangoproject.com/foundation/cla/faq/>`_.

If you have any question, do not hesitate to contact the founder of the
project, `Barthelemy <mailto:barthelemy@infobart.com>`_.
