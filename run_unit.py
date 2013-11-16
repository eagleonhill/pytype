from unittest import *
import sys

if len(sys.argv) == 2:
  pattern = 'test' + sys.argv[1]
else:
  pattern = 'test*.py'
suite = TestLoader().discover('unit', pattern, '..')
TextTestRunner(verbosity=2).run(suite)
