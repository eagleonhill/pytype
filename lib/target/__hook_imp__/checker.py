def type_error(value, expected_type):
  raise TypeError(value, expected_type)
def convert_error(f, t):
  raise TypeError('Cannot convert ' + repr(f) + ' to ' + str(t))
def attr_error(value, attr):
  raise AttributeError(value, attr)
def argument_error(args, pattern):
  raise TypeError(args, pattern)
