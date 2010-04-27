'''
Created on Dec 19, 2009

@author: barthelemy
'''
from paver.easy import *
import paver.doctools
from paver.setuputils import setup, find_package_data

DOC_DIR = 'doc'
DIST_DIR = 'dist'
VERSION = '0.3'
RELEASE = 'py4j-' + VERSION
JAR_FILE = 'py4j' + VERSION + '.jar'

setup(
    name="Py4J",
    packages=['','py4j', 'py4j.tests'],
    package_dir={'':'src'},
    include_package_data = True,
    package_data = {'':['*.jar']},
    version="0.3",
    url="http://py4j.sourceforge.net/",
    author="Barthelemy Dagenais",
    author_email="barthe@users.sourceforge.net",
    license="BSD License",
    zip_safe = True,
    classifiers=[
          'Development Status :: 4 - Beta',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: BSD License',
          'Operating System :: OS Independent',
          'Programming Language :: Python',
          'Programming Language :: Java',
          'Topic :: Software Development :: Libraries',
          'Topic :: Software Development :: Object Brokering',
          ],

)

options(
    sphinx=Bunch(
        docroot="../py4j-web",
        builddir="_build"
    ),
    minilib=Bunch(
        extra_files = ['doctools'],
    )
)

def scp_dir(source, dest):
    """Copy the source file to the destination."""
    sh("scp -r %s %s" % (source, dest))

@task
@needs('generate_setup', 'minilib', 'html_complete', 'py4j_java', 'setuptools.command.sdist')
def sdist():
    """Generate source distribution with documentation."""
    pass

@task
@needs('py4j_java')
def set_jar():
    """Move jar file in python source folder (for distribution)."""
    jar = path('../py4j-java/dist') / RELEASE / JAR_FILE
    jar.copy('src/' + JAR_FILE)

@task
@needs('set_jar','setuptools.command.bdist_egg')
def bdist_egg():
    """Generate binary (egg) distribution with jar file."""
    pass

@task
@needs('generate_setup', 'minilib', 'html_complete', 'py4j_java', 'setuptools.command.sdist','bdist_egg','soft_clean')
def big_release():
    """Generate source distribution with documentation and binary distribution."""
    # Don't forget to run with --formats=zip,gztar
    pass

@task
@needs('html')
def html_complete():
    """Build Py4J documentation: python documentation, web site, and javadoc. Put documentation into our py4j-python/doc."""
    sh('ant clean-doc', False, False, '../py4j-java')
    sh('ant javadoc', False, False, '../py4j-java')
    
    print('Moving javadoc')
    # HACK: path must be relative to symlink, not to current directory. Wow...
    javadoc = path('../py4j-java/javadoc')
    javadoc.copytree('doc/_static/javadoc')

@task
def py4j_java():
    """Generate Java source distribution (source files and jar)."""
    sh('ant clean-dist', False, False, '../py4j-java')
    sh('ant dist', False, False, '../py4j-java')
    
    print('Moving py4j-java')
    py4j_java = path('../py4j-java/dist') / RELEASE
    py4j_java.copytree('py4j-java')
    
@task
@needs('paver.doctools.html')
def html(options):
    """Build the py4j web site and put them into python distribution."""
    destdir = path(DOC_DIR)
    destdir.rmtree()
    builtdocs = path("../py4j-web") / options.builddir / "html"
    builtdocs.move(destdir)
    
@task
@needs('html_complete')
def deploy():
    """Deploy web site on sourceforge."""
    docdir = path(DOC_DIR)
    docdir.symlink('htdocs')
    scp_dir('htdocs', 'barthe,py4j@web.sourceforge.net:/home/groups/p/py/py4j')
    htdocs = path('htdocs')
    htdocs.remove()
    
# You can also deploy to sourceforge:
# scp Py4J-0.1-py2.6.egg barthe,py4j@frs.sourceforge.net:/home/frs/project/p/py/py4j/0.1

    
@task
@needs('paver.doctools.doc_clean', 'distutils.command.clean','soft_clean')
def clean():
    """Remove the whole distribution directory."""
    distdir = path(DIST_DIR)
    distdir.rmtree()
    
@task
def soft_clean():
    """Remove the temp directories, i.e., build, egg, doc, py4j-java, and jar directory."""
    docdir = path(DOC_DIR)
    build = path('build')
    eggdir = path('Py4J.egg-info')
    docdir.rmtree()
    eggdir.rmtree()
    build.rmtree() 
    py4j_java = path('py4j-java')
    py4j_java.rmtree()
    jar = path('src') / JAR_FILE
    jar.remove()
    egg_info = path('src/Py4J.egg-info')
    egg_info.rmtree()
    
    
