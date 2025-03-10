# Releasing Py4J on pypi and Sonatype

0. Update all versions (py4j-java/ant.properties, py4j-java/build.gradle, py4j-java/gradle.properties, py4j-java/pom.xml, py4j-python/src/py4j/version.py).
1. Write changelog (with milestone created); add new authors.
2. ./gradlew clean (at py4j/py4j-java)
3. close all bugs on github
4. tag the release on git
5. check out the source code from the tag
6. remove py4j/py4j-python/dist/*
7. ./gradlew buildPython  (at py4j/py4j-java)
8. create gpg key and send it to key server (refer to 'Preparing gpg key' in
   https://spark.apache.org/release-process.html)
9. upload to PyPI using twine (at py4j/py4j-python). For example:
    ```
    twine upload dist/*
    ```
10. make sure you have 'settings.xml' under '~/.m2', see also
    https://central.sonatype.org/publish/publish-maven/#distribution-management-and-authentication
11. if you are a new user in Sonatype, you should replace the upload URL in
    pom.xml (at py4j/py4j-java). For example:
    ```
    # In Mac
    sed -i '' 's/oss.sonatype.org/s01.oss.sonatype.org/g' pom.xml
    # or in Linux OS
    sed 's/oss.sonatype.org/s01.oss.sonatype.org/g' pom.xml
    ```
12. mvn clean deploy (at py4j/py4j-java)
13. Deploy the update site by following the steps in
    release_process_for_eclipse.md
