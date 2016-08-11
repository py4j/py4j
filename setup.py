try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup
import os
import subprocess
import sys


DOC_DIR = os.path.join("py4j-python", "doc")
DIST_DIR = os.path.join("py4j-python", "dist")
VERSION_PATH = os.path.join("py4j-python", "src", "py4j", "version.py")
# For Python 3 compatibility, we can't use execfile; this is 2to3's conversion:
exec(compile(open(VERSION_PATH).read(),
     VERSION_PATH, "exec"))
VERSION = __version__  # noqa
RELEASE = "py4j-" + VERSION
JAR_FILE = "py4j" + VERSION + ".jar"

os.chdir("py4j-java")
if os.name == "nt":
    subprocess.call("./gradlew.bat buildPython", shell=True)
else:
    subprocess.call("./gradlew buildPython", shell=True)
os.chdir("..")

JAR_FILE_PATH = os.path.join("py4j-python", "py4j-java", JAR_FILE)

test_requirements = [
    "pytest~=2.9.2",
]

if sys.version_info[0:2] <= (3, 3):
    test_requirements.append("mock~=2.0.0")

setup(
    name="py4j",
    packages=["py4j", "py4j.tests"],
    package_dir={"": "py4j-python/src"},
    data_files=[("share/py4j", [JAR_FILE_PATH])],
    version=VERSION,
    description="Enables Python programs to dynamically access arbitrary "
                "Java objects",
    long_description="Py4J enables Python programs running in a Python "
                     "interpreter to dynamically "
                     "access Java objects in a Java Virtual Machine. "
                     "Methods are called as if the Java "
                     "objects resided in the Python interpreter and Java "
                     "collections can be accessed "
                     "through standard Python collection methods. Py4J also "
                     "enables Java programs to call back Python objects.",
    url="https://www.py4j.org/",
    author="Barthelemy Dagenais",
    author_email="barthelemy@infobart.com",
    license="BSD License",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.6",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Java",
        "Topic :: Software Development :: Libraries",
        "Topic :: Software Development :: Object Brokering",
    ],
    test_require=test_requirements,

)
