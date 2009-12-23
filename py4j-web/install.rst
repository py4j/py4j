.. _install_instructions:

Installing Py4J
===============

Installing Python 2.6+ 
----------------------

Py4J is a library written in Python and Java. Currently, Py4J has been tested with Python 2.6 only. You can install
Python by going to the `official Python download page <http://www.python.org/download/>`_.


Installing Java 6
-----------------

You also need to install a Java environment, version 6. You can install a Java environment by going to the `official Java
download page <http://java.sun.com/javase/downloads/index.jsp>`_ You will need to download the JDK if you plan to use
the Java compiler, but you only need the JRE if you are using another compiler, such as the one provide by the `Eclipse
Development Environment <http://www.eclipse.org>`_.


Installing Py4J
---------------

There are three ways to install Py4J:

Using easy_install
^^^^^^^^^^^^^^^^^^

To be done.

Using an official release
^^^^^^^^^^^^^^^^^^^^^^^^^

To be done.

Using the latest development source code
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

We will provide detailed instructions to build Py4J in future releases. Briefly, you need:

1. `Subversion <http://subversion.tigris.org/>`_ to download the latest source code. Execute the command line ``svn co
   https://py4j.svn.sourceforge.net/svnroot/py4j/trunk py4j`` to download the source code.
2. `Apache ant <http://ant.apache.org>`_ to build the Py4J Java library. Just execute the command line ``ant jar`` in the
   py4j-java project directory to build the code and create a jar file. 
3. `Sphinx <http://sphinx.pocoo.org/>`_ to build the documentation. Just execute the command line ``make html``  in the
   py4j-web project.
4. `Paver <http://www.blueskyonmars.com/projects/paver/>`_ to build the Py4J Python library. Execute the command line ``paver
   big_release`` in the py4j-python directory to create a tar.gz source distribution and an egg file. The ``big_release``
   target will also create the jar file and the documentation and will add them to the source distribution. This means that
   you need ant and Sphinx to build the Py4J Python library.