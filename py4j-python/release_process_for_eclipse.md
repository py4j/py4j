# Releasing Py4J for Eclipse

1. Assuming that you already ran gradle buildPython (in py4j/py4j-java/)
2. gradle updateSite (in py4j/py4j-java)
3. In py4j/py4j-java/build/updatesite, modify artifacts and content jar files:
    ```
    jar -xf artifacts.jar
    rm artifacts.jar
    sed -i "s/repository name='file:[^']*'/repository name='Py4J p2 Repository'/g" artifacts.xml
    jar cf artifacts.jar artifacts.xml
    rm artifacts.xml
    jar -xf content.jar
    rm content.jar
    sed -i "s/repository name='file:[^']*'/repository name='Py4J p2 Repository'/g" content.xml
    sed -i "s/unit id='file:[^']*'/unit id='version.Py4J'/g" content.xml
    sed -i "s/name='file:[^']*'/name='version.Py4J'/g" content.xml 
    jar cf content.jar content.xml
    rm content.xml
    ```
4. Assuming that you have cloned the py4j-eclipse-udpate-site project to
    /path/py4j-eclipse-udpate-site
    ```
    cp -r py4j/py4j-java/build/updatesite/* /path/py4j-eclipse-udpate-site
    ```
5. commit and push the files to the py4j-eclipse-udpate-site repository


# About gradle updateSite

1. For this to work, you need an old version of Eclipse and Java 8.
2. Download Eclipse Classic 3.6.2 (newer versions not tested) at
   https://www.eclipse.org/downloads/packages/release/helios/sr2/eclipse-classic-362
3. Unzip it to /some/path/eclipse/3.6
4. In your ~/.gradle/gradle.properties, set
   eclipseHomePath=/some/path/eclipse/3.6/

# About the Py4J Eclipse update site

The py4j-eclipse-udpate-site repository is hosted on
https://py4j.github.io/py4j-eclipse-udpate-site/ 2. 

The eclipse.py4j.org is hosted on Bart Dagenais's server and it redirects
(302) requests for artifacts.jar, content.jar, features/, plugins/ to
https://py4j.github.io/py4j-eclipse-udpate-site$request_uri
