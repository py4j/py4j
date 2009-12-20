'''
Created on Dec 19, 2009

@author: barthelemy
'''
from paver.easy import *
import paver.doctools
from paver.setuputils import setup, find_package_data
from setuptools import find_packages

setup(
    name="Py4J",
    packages = ['py4j', 'py4j.tests'],
    package_dir = {'py4j':'src/py4j'},
    version="0.1",
    url="http://py4j.sourceforge.net/",
    author="Barthelemy Dagenais",
    author_email="barthe@users.sourceforge.net",
    license="BSD License",
    classifiers=[
          'Development Status :: 3 - Alpha',
          'Intended Audience :: by End-User Class :: Developers',
          'License :: OSI-Approved Open Source :: BSD License',
          'Operating System :: Grouping and Descriptive Categories :: OS Portable (Source code to work with many OS platforms)',
          'Programming Language :: Python',
          'Programming Language :: Java',
          'Topic :: Software Development :: Libraries',
          'Topic :: Software Development :: Object Brokering',
          'Topic :: Software Development :: Virtual Machines',
          'User Interface :: Non-interactive (Daemon)',
          ],

)

options(
    sphinx=Bunch(
        docroot="../py4j-web",
        builddir="_build"
    )
)

def scp_dir(source, dest):
    """Copy the source file to the destination."""
    sh("scp -r %s %s" % (source, dest))

@task
@needs('generate_setup', 'minilib', 'html', 'setuptools.command.sdist')
def sdist():
    """Overrides sdist to make sure that our setup.py is generated."""
    pass

@task
@needs('paver.doctools.html')
def html(options):
    """Build the docs and put them into our package."""
    destdir = path('docs')
    destdir.rmtree()
    builtdocs = path("../py4j-web") / options.builddir / "html"
    builtdocs.move(destdir)
    
@task
@needs('html')
def deploy():
    docdir = path('docs')
    docdir.symlink('htdocs')
    scp_dir('htdocs','barthe,py4j@web.sourceforge.net:/home/groups/p/py/py4j')
    htdocs = path('htdocs')
    htdocs.remove()
    
@task
@needs('paver.doctools.doc_clean','distutils.command.clean',)
def clean():
    distdir = path('dist')
    docdir = path('docs')
    build = path('build')
    eggdir = path('Py4J.egg-info')
    distdir.rmtree()
    docdir.rmtree()
    eggdir.rmtree()
    build.rmtree()
