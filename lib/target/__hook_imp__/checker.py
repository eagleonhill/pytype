def type_error(value, expected_type):
  raise TypeError(value, expected_type)
def convert_error(f, t):
  raise TypeError('Cannot convert ' + repr(f) + ' to ' + str(t))
def attr_error(value, attr):
  raise AttributeError(value, attr)
def argument_error(args, pattern):
  raise TypeError(args, pattern)

def uncomparable_warning(x, y):
  pass

def type_equal(val1, val2):
  if hasattr(val1, '__typeeq__'):
    return val1.__typeeq__(val2)
  elif hasattr(val2, '__typeeq__'):
    return val2.__typeeq__(val1)
  else:
    return val1.__class__ is val2.__class__

def get_revision_manager():
  import revision
  return revision.get_revisions()
def get_current_frame():
  return get_revision_manager().traced_frame
def fork():
  return get_current_frame().get_next_bool_decision()

def impossible_path():
  get_current_frame().impossible_path()

def duplicated_path():
  get_current_frame().duplicated_path()

def notify_update(obj):
  get_revision_manager().notify_update(obj)
