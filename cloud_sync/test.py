from src import *
import unittest

if __name__ == 'test':
    testsuite = unittest.TestLoader().discover('.', '*_test.py')
    unittest.TextTestRunner(verbosity=1).run(testsuite)
