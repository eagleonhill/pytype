def raise_checker_error(exc_type, exc_value = None, traceback=None):
  raise exc_type, exc_value, traceback
def type_error(value, expected_type):
  raise_checker_error(TypeError(value, expected_type))
def convert_error(f, t):
  raise_checker_error(TypeError('Cannot convert ' + repr(f) + ' to ' + str(t)))
def attr_error(value, attr):
  raise_checker_error(AttributeError(value, attr))
def argument_error(args, pattern):
  raise_checker_error(TypeError(args, pattern))
def key_error(key):
  raise_checker_error(KeyError(key))

def is_internal_error(exc_type, exc_value, traceback):
  t = traceback
  while t.tb_next is not None:
    t = t.tb_next
  if is_internal_frame(t.tb_frame) and\
      t.tb_frame.f_code != raise_checker_error.func_code:
    return True
  return False

def is_internal_frame(frame):
  return not bool(frame.f_restricted)

def format_traceback(tb, hide_internal = False):
  import traceback
  l = []
  while tb:
    if not hide_internal or not is_internal_frame(tb.tb_frame):
      l.append(traceback.extract_tb(tb, 1)[0])
    tb = tb.tb_next
  return traceback.format_list(l)

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
