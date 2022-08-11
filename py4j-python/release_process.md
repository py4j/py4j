# Releasing Py4J on pypi and Sonatype

0. Update all versions (version.py, properties: gradle/ant, documentation, index.rst, pom.xml).
1. Write changelog; add new authors.
2. ./gradlew clean (at py4j/py4j-java)

3. close all bugs on github
4. tag the release on git

5. ./gradlew buildPython  (at py4j/py4j-java)
6. create signature using gpg (gpg --export --armor YOUR_KEY, also refer to
   'Preparing gpg key' in https://spark.apache.org/release-process.html)

7. upload to PyPI using twine (at py4j/py4j-python). For example:
    ```
    python setup.py sdist
    python setup.py bdist_wheel --universal
    twine upload dist/*
    ```

8. make sure you have 'settings.xml' under '~/.m2', see also
   https://central.sonatype.org/publish/publish-maven/#distribution-management-and-authentication

9. if you are a new user in Sonatype, you should replace the upload URL in
   pom.xml (at py4j/py4j-java). For example:

    ```
    # In Mac
    sed -i '' 's/oss.sonatype.org/s01.oss.sonatype.org/g' pom.xml
    # or in Linux OS
    sed 's/oss.sonatype.org/s01.oss.sonatype.org/g' pom.xml
    ```

10. mvn clean deploy (at py4j/py4j-java)

11. Deploy the update site by following the steps in
    release_process_for_eclipse.md
