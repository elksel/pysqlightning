#-*- coding: ISO-8859-1 -*-
# setup.py: the distutils script
#
# Copyright (C) 2004-2007 Gerhard Häring <gh@ghaering.de>
#
# This file is part of pysqlite.
#
# This software is provided 'as-is', without any express or implied
# warranty.  In no event will the authors be held liable for any damages
# arising from the use of this software.
#
# Permission is granted to anyone to use this software for any purpose,
# including commercial applications, and to alter it and redistribute it
# freely, subject to the following restrictions:
#
# 1. The origin of this software must not be misrepresented; you must not
#    claim that you wrote the original software. If you use this software
#    in a product, an acknowledgment in the product documentation would be
#    appreciated but is not required.
# 2. Altered source versions must be plainly marked as such, and must not be
#    misrepresented as being the original software.
# 3. This notice may not be removed or altered from any source distribution.

import glob, os, re, sys
import urllib
import zipfile
import six
# from distutils.core import setup, Extension, Command
from setuptools import setup, Extension, Command
from distutils.command.build import build
from distutils.command.build_ext import build_ext
from distutils.spawn import find_executable

import cross_bdist_wininst

# If you need to change anything, it should be enough to change setup.cfg.

sqlite = "sqlite"

PYSQLITE_EXPERIMENTAL = False

if six.PY2:
    src = 'src'
else:
    src = 'src_py3'

sources = ["module.c", "connection.c", "cursor.c", "cache.c",
           "microprotocols.c", "prepare_protocol.c", "statement.c",
           "util.c", "row.c"]

if PYSQLITE_EXPERIMENTAL:
    sources.append("backup.c")

sources = [os.path.join(src, fname) for fname in sources]

include_dirs = ["sqlightning", "lmdb/libraries/liblmdb"]
if sys.platform == "win32":
    include_dirs.append("msinttypes-r26")
library_dirs = []
libraries = []
runtime_library_dirs = []
extra_objects = []
define_macros = []

long_description = \
"""Python interface to SQLite 3

pysqlite is an interface to the SQLite 3.x embedded relational database engine.
It is almost fully compliant with the Python database API version 2.0 also
exposes the unique features of SQLite."""

if sys.platform != "win32":
    define_macros.append(('MODULE_NAME', '"pysqlightning"'))
else:
    define_macros.append(('MODULE_NAME', '\\"pysqlightning\\"'))

class DocBuilder(Command):
    description = "Builds the documentation"
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        import os, shutil
        try:
            shutil.rmtree("build/doc")
        except OSError:
            pass
        os.makedirs("build/doc")
        rc = os.system("sphinx-build doc/sphinx build/doc")
        if rc != 0:
            six.print_("Is sphinx installed? If not, try 'sudo easy_install sphinx'.")

class AmalgamationBuilder(build):
    description = "Build a statically built pysqlite using the amalgamtion."

    def __init__(self, *args, **kwargs):
        MyBuildExt.amalgamation = True
        self._amalgamate_sqlightning()
        build.__init__(self, *args, **kwargs)

    def _amalgamate_sqlightning(self):
        import platform
        if sys.platform == "win32":
            if six.PY3:
                if not find_executable("nmake"):
                    vcvarsall = r'C:\Program Files (x86)\Microsoft Visual Studio 10.0\VC\vcvarsall.bat'
                    vcvars_cmd_x64 = r'call "%s" x64 &&' %(vcvarsall)
                    vcvars_cmd_x86 = r'call "%s" x86 &&' %(vcvarsall)
                else:
                    vcvars_cmd_x64 = ""
                    vcvars_cmd_x86 = ""
            else:
                vcvarsall = r'%LOCALAPPDATA%\Programs\Common\Microsoft\Visual C++ for Python\9.0\vcvarsall.bat'
                if not os.path.exists(os.path.expandvars(vcvarsall)):
                    vcvarsall = r'%COMMONPROGRAMFILES(X86)%\Microsoft\Visual C++ for Python\9.0\vcvarsall.bat'
                if not os.path.exists(os.path.expandvars(vcvarsall)):
                    raise Exception('"Visual C++ for Python" not found')
                
                vcvars_cmd_x64 = r'call "%s" x64 &&' %(vcvarsall)
                vcvars_cmd_x86 = vcvars_cmd_x64 + r' && call "%s" x86 &&' %(vcvarsall) # run vcvars_cmd_x64 first to get vcbuild.exe
        
            # Check for tcl
            if not find_executable("tclsh85"):
                raise Exception("Please ensure TCL 8.5 is installed and tclsh85 is on the path")
        
        currdir = os.path.abspath(os.curdir)
        os.chdir(os.path.join(os.path.dirname(__file__),'sqlightning'))
        if sys.platform == "win32":
            if platform.architecture()[0] == '32bit':
                vcvars_cmd = vcvars_cmd_x86
            else:
                vcvars_cmd = vcvars_cmd_x64
            os.system("%s nmake /f makefile.msc sqlite3.c" % vcvars_cmd)
        else:
            os.system("sh configure && make sqlite3.c")
        os.chdir(currdir)


class MyBuildExt(build_ext):
    amalgamation = False

    def build_extension(self, ext):
        if self.amalgamation:
            ext.define_macros.append(("SQLITE_ENABLE_FTS3", "1"))   # build with fulltext search enabled
            ext.define_macros.append(("SQLITE_ENABLE_RTREE", "1"))   # build with fulltext search enabled
            ext.sources.append("sqlightning/sqlite3.c")
        build_ext.build_extension(self, ext)

    def __setattr__(self, k, v):
        # Make sure we don't link against the SQLite library, no matter what setup.cfg says
        if self.amalgamation and k == "libraries":
            v = None
        self.__dict__[k] = v

def get_setup_args():

    PYSQLITE_VERSION = None

    version_re = re.compile('#define PYSQLITE_VERSION "(.*)"')
    f = open(os.path.join(src, "module.h"))
    for line in f:
        match = version_re.match(line)
        if match:
            PYSQLITE_VERSION = match.groups()[0]
            PYSQLITE_MINOR_VERSION = ".".join(PYSQLITE_VERSION.split('.')[:2])
            break
    f.close()

    if not PYSQLITE_VERSION:
        six.print_("Fatal error: PYSQLITE_VERSION could not be detected!")
        sys.exit(1)

    data_files = [("pysqlightning-doc",
                        glob.glob("doc/*.html") \
                      + glob.glob("doc/*.txt") \
                      + glob.glob("doc/*.css")),
                   ("pysqlightning-doc/code",
                        glob.glob("doc/code/*.py"))]

    py_modules = ["sqlite"]
    setup_args = dict(
            name = "pysqlightning",
            version = PYSQLITE_VERSION,
            description = "DB-API 2.0 interface for SQLightning",
            long_description=long_description,
            author = "Andrew Leech",
            author_email = "andrew@alelec.net",
            license = "The OpenLDAP Public License Version 2.8, 17 August 2003",
            platforms = "ALL",
            url = "https://github.com/andrewleech/pysqlightning",
            download_url = "https://pypi.python.org/pypi/pysqlightning",

            # Description of the modules and packages in the distribution
            package_dir = {"pysqlightning": "lib"},
            packages = ["pysqlightning", "pysqlightning.test"],
            scripts=[],
            data_files = data_files,

            ext_modules = [Extension( name="pysqlightning._sqlightning",
                                      sources=sources,
                                      include_dirs=include_dirs,
                                      library_dirs=library_dirs,
                                      runtime_library_dirs=runtime_library_dirs,
                                      libraries=libraries,
                                      extra_objects=extra_objects,
                                      define_macros=define_macros
                                      )],
            classifiers = [
            "Development Status :: 5 - Production/Stable",
            "Intended Audience :: Developers",
            "License :: OSI Approved :: zlib/libpng License",
            "Operating System :: MacOS :: MacOS X",
            "Operating System :: Microsoft :: Windows",
            "Operating System :: POSIX",
            "Programming Language :: C",
            "Programming Language :: Python",
            "Topic :: Database :: Database Engines/Servers",
            "Topic :: Software Development :: Libraries :: Python Modules"],
            cmdclass = {"build_docs": DocBuilder}
            )

    setup_args["cmdclass"].update({"build_docs": DocBuilder, "build_ext": MyBuildExt, "build_static": AmalgamationBuilder, "cross_bdist_wininst": cross_bdist_wininst.bdist_wininst})
    return setup_args

def main():
    setup(**get_setup_args())

if __name__ == "__main__":
    main()
