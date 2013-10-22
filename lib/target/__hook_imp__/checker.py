def type_error(value, expected_type):
  raise TypeError(value, expected_type)
def convert_error(f, t):
  raise TypeError('Cannot convert ' + repr(f) + ' to ' + str(t))
def attr_error(value, attr):
  raise AttributeError(value, attr)
def argument_error(args, pattern):
  raise TypeError(args, pattern)

def type_equal(val1, val2):
  if hasattr(val1, '__typeeq__'):
    return val1.__typeeq__(val2)
  elif hasattr(val2, '__typeeq__'):
    return val2.__typeeq__(val1)
  else:
    return val1.__class__ is val2.__class__
