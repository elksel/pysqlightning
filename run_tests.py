__author__ = 'corona'

import os, sys
import unittest

if os.path.exists("extended_setup.py"):
    print ("-" * 75)
    print ("You should not run the test suite from the pysqlite build directory.")
    print ("This does not work well because the extension module cannot be found.")
    print ("Just run the test suite from somewhere else, please!")
    print ("-" * 75)
    sys.exit(1)

from lib.test import dbapi, types, userfunctions, factory, transactions,\
    hooks, regression, dump, concurrency
from pysqlightning import dbapi2 as sqlite

def suite():
    tests = [dbapi.suite(), types.suite(), userfunctions.suite(), factory.suite(), transactions.suite(), hooks.suite(), regression.suite(), dump.suite()]
    # , concurrency.suite()]

    return unittest.TestSuite(tuple(tests))

runner = unittest.TextTestRunner()
runner.run(suite())
