from distutils.core import setup
import os

DOC_DIR = 'doc'
DIST_DIR = 'dist'
VERSION = '0.7'
RELEASE = 'py4j-' + VERSION
JAR_FILE = 'py4j' + VERSION + '.jar'
JAR_FILE_PATH = os.path.join('py4j-java',JAR_FILE)

setup(
    name="py4j",
    packages=['py4j', 'py4j.tests'],
    package_dir={'':'src'},
    data_files=[('share/py4j',[JAR_FILE_PATH])],
    version=VERSION,
    description='Enables Python programs to dynamically access arbitrary Java objects',
    long_description='Py4J enables Python programs running in a Python interpreter to dynamically \
                    access Java objects in a Java Virtual Machine. Methods are called as if the Java \
                    objects resided in the Python interpreter and Java collections can be accessed \
                    through standard Python collection methods. Py4J also enables Java programs to \
                    call back Python objects.',
    url="http://py4j.sourceforge.net/",
    author="Barthelemy Dagenais",
    author_email="barthe@users.sourceforge.net",
    license="BSD License",
    classifiers=[
          'Development Status :: 4 - Beta',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: BSD License',
          'Operating System :: OS Independent',
          'Programming Language :: Python',
          'Programming Language :: Python :: 2',
          'Programming Language :: Python :: 2.6',
          'Programming Language :: Python :: 2.7',
          'Programming Language :: Python :: 3',
          'Programming Language :: Python :: 3.1',
          'Programming Language :: Python :: 3.2',
          'Programming Language :: Java',
          'Topic :: Software Development :: Libraries',
          'Topic :: Software Development :: Object Brokering',
          ],

)
