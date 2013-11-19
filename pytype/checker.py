import sys
def raise_checker_error(exc_type, exc_value = None, traceback=None):
  # If traceback is given, raise_checker_error is not in traceback
  do_raise_checker_error(exc_type, exc_value, traceback)
def do_raise_checker_error(exc_type, exc_value = None, traceback=None):
  raise exc_type, exc_value, traceback
def reraise_error():
  import sys
  exc_info = sys.exc_info()
  raise_checker_error(*exc_info)
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
    if t.tb_frame.f_code is raise_checker_error.func_code:
      return False
    t = t.tb_next
  if is_internal_frame(t.tb_frame):
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
  from . import revision
  return revision.get_revisions()
def get_current_frame():
  from .traced_frame import TracedFrame
  return TracedFrame.current()
def get_program_frame(start = None):
  if start is None:
    start = sys._getframe(0)
  while is_internal_frame(start):
    start = start.f_back
  return start
def fork():
  return get_current_frame().get_next_bool_decision()

def impossible_path():
  get_current_frame().impossible_path()

def duplicated_path():
  get_current_frame().duplicated_path()

def notify_update(obj):
  get_revision_manager().notify_update(obj)

def assume(x):
  if not x:
    impossible_path()
