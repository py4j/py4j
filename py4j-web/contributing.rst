Contributing to Py4J
====================

.. contents:: Summary
   :backlinks: entry
   :local:

Thanks a lot for using Py4J and wanting to contribute! Your help is greatly
appreciated!

The following is a set of guidelines for contributing to Py4J. These are just
guidelines, not rules, use your best judgment and feel free to propose changes
to this document in a pull request.

These guidelines have evolved since Py4J started and past commits may not
always follow them.

In general, if your contribution does not follow these guidelines, we will
review your contribution, but expect that we will ask you for some changes and
refer you to specific parts of this guide!

General Conventions
-------------------

Contributions to Py4J are always welcome. To accelerate the review process,
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

Libraries used for testing and contributing (flake8, nose, tox, Sphinx) can be
installed with pip:


.. code-block:: bash

  pip install -r requirements.txt

  # Run flake8
  flake8


.. _java_conventions:

Java Coding Conventions
-----------------------

We use Eclipse code formatting conventions (see `py4j.formatter.xml
<https://raw.githubusercontent.com/bartdag/py4j/master/py4j-java/py4j.formatter.xml>`_
and `py4j.importorder
<https://raw.githubusercontent.com/bartdag/py4j/master/py4j-java/py4j.importorder>`_)
that can be used in Eclipse and IntelliJ IDEs.

In summary:

1. We use tabs rather than spaces to indent the Java code.
2. Most expressions (conditionals, loops, try/catch) are always wrapped with
   curly brackets.

You can format your code using gradle and Java 8:

.. code-block:: bash

  # To check Java coding conventions:
  ./gradlew spotlessCheck

  # To format your code:
  ./gradlew spotlessJavaApply

We use `FindBugs <http://findbugs.sourceforge.net/>`_ on the main source code
(not the test source code) and any warnings must be corrected before a pull
request will be accepted.

.. code-block:: bash

  # To run findbugs
  ./gradlew findbugsMain


Testing Python Code
-------------------

On the Python side, we use nose to run the test suite and tox to run the test
suite across the supported python versions.

.. code-block:: bash

  # make sure that the jar file is created
  cd py4j-java
  ./gradlew clean
  ./gradlew assemble

  # install test requirements
  cd py4j-python
  pip install -r requirements.txt

  # Run the full test suite
  nosetests

  # Run only one particular test
  nosetests py4j.tests.java_gateway_test:GatewayLauncherTest.testRedirectToDeque

  # Run all tests on all supported pythons.
  # Typically only do this if the automated build failed
  # on one version of python.
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
  ./gradlew test


Code Coverage
-------------

We have started to keep track of code coverage on both the Python and Java
libraries. Unfortunately, most of the Java code is being tested by the Python
library so the reported code coverage is smaller than the actual coverage.

When reviewing a contribution, we will always require that both the Java code
and the Python code are tested, but it does not matter if the Java code is
tested by the Python code.


Branch name and commit message format
-------------------------------------

In general, it is best to first open an issue and then, refer to the issue in
your commit:

1. Your branch should have the format ``issue-XYZ-branch-name`` where XYZ is
   the issue number and branch-name is a short description.

2. Commits that refer to an issue will have the format ``refs #XYZ -- message``
   where XYZ is the issue number.

3. Once a pull request is approved, we ask you to rebase your changes against
   the master branch and squash your commits into one
   meaningful commit (see below for tips on how to do this). The format of the
   commit would be:

   .. code-block:: text

        fixes #XYZ -- short description below 72 characters

        Longer description that lists all the changes that occured
        on multiple lines of 79 characters.


Squashing commits and git
^^^^^^^^^^^^^^^^^^^^^^^^^

To squash your commits, you can use the git rebase command:

.. code-block:: bash

  # Squash the last three commits into 1
  git rebase -i HEAD~3
  # An editor will open. Change the word "pick" to "squash"
  # except for the very first commit at the top of the list.
  # After you save and exit, you will be prompted again to
  # change the commit message of the squashed commit.

The Django contributing guide has a `good tutorial on using git to contribute
<https://docs.djangoproject.com/en/1.9/internals/contributing/writing-code/working-with-git/>`_
and in particular, `squashing commits
<https://docs.djangoproject.com/en/1.9/internals/contributing/writing-code/working-with-git/#rebasing-branches>`_.


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
