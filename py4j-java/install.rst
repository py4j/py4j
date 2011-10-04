Maven install
=============

As for now maven allows installation of java part of py4j.

To build this use standard maven procedure:

      mvn install

since as of today some tests one may disable them:

     mvn -Dmaven.test.skip=true install

Builded binaries will be in target/py4j-0.7.jar.