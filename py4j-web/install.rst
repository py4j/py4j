.. _install_instructions:

Installing Py4J
===============

Installing Python 2.6+ 
----------------------

Py4J is a library written in Python and Java. Currently, Py4J has been tested
with Python 2.6 and Python 2.7 only. You can install
Python by going to the `official Python download page
<http://www.python.org/download/>`_.


Installing Java 6
-----------------

You also need to install a Java environment, version 6. You can install a Java
environment by going to the `official Java download page
<http://java.sun.com/javase/downloads/index.jsp>`_ You will need to download
the JDK if you plan to use the Java compiler, but you only need the JRE if you
are using another compiler, such as the one provided by the `Eclipse
Development Environment <http://www.eclipse.org>`_.


Installing Py4J
---------------

There are three ways to install Py4J:

Using easy_install
^^^^^^^^^^^^^^^^^^

1. Run ``easy_install Py4J`` (don't forget to prefix with sudo if you install
   Py4J system-wide on a \*NIX operating system).  
2. Py4J should now be in your PYTHONPATH.
3. The Py4J Java library is located in ``share/py4j/py4j0.x.jar``. The exact
   location depends on the platform and the installation type. Some likely
   locations are:
   
   1. ``/usr/share/py4j/py4j0.x.jar`` for system-wide install on Linux.
   2. ``{virtual_env_dir}/share/py4j/py4j0.x.jar`` for installation in a
      virtual environment.
   3. ``C:\python27\share\py4j\py4j0.x.jar`` for system-wide install on
      Windows.

Using an official release
^^^^^^^^^^^^^^^^^^^^^^^^^

1. Download the latest official release from `SourceForge
   <https://sourceforge.net/projects/py4j/files/>`_ or from `PyPI
   <http://pypi.python.org/pypi/Py4J>`_. If you are using a \*NIX OS, download
   the tar.gz file. If you are using Windows, download the zip file.
2. Untar/Unzip the file and navigate to the newly created directory, e.g., ``cd
   Py4J-0.x``.  
3. Run ``python setup.py install`` (don't forget to prefix with sudo if you
   install Py4J system-wide).
4. Py4J should now be in your PYTHONPATH.
5. The Py4J Java library is located under ``Py4J-0.x/py4j-java/py4j0.x.jar``.
   Add this library to your classpath when using Py4J in a Java program.

Using the latest development source code
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

We will provide detailed instructions to build Py4J in future releases.
Briefly, you need:

1. `Git <http://git-scm.com/>`_ to download the latest source code.
   Execute the command line ``git clone https://github.com/bartdag/py4j.git
   py4j`` to download the source code.
2. `Apache ant <http://ant.apache.org>`_ to build the Py4J Java library. Just
   execute the command line ``ant jar`` in the py4j-java project directory to
   build the code and create a jar file. 
3. `Sphinx <http://sphinx.pocoo.org/>`_ to build the documentation. Just
   execute the command line ``make html``  in the
   py4j-web project.
4. `Paver <http://paver.github.com/paver/>`_ to build the Py4J
   Python library. Execute the command line ``paver big_release`` in the
   py4j-python directory to create a tar.gz source distribution and an egg
   file. The ``big_release`` target will also create the jar file and the
   documentation and will add them to the source distribution. This means that
   you need ant and Sphinx to build the Py4J Python library.
