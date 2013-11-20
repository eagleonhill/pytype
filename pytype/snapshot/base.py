from abc import ABCMeta, abstractmethod
from types import InstanceType
from weakref import ref

class Snapshotable(object):
  __metaclass__ = ABCMeta
  @abstractmethod
  def __make__(self):
    return None

  @abstractmethod
  def __restore__(self, value, cur = None):
    pass

class Immutable(Snapshotable):
  def __make__(self):
    raise Exception, 'An immutable object is updating'
  def __restore__(self, value, cur = None):
    raise Exception, 'An immutable object is restoring'

Snapshotable.register(InstanceType)
Immutable.register(int)
Immutable.register(long)
Immutable.register(float)
Immutable.register(str)
Immutable.register(unicode)
Immutable.register(tuple)
Immutable.register(type(None))
Immutable.register(ref)

def snapshotable(obj):
  return isinstance(obj, Snapshotable) or type(obj) == InstanceType

def make_snapshot(obj):
  if hasattr(obj, '__make__'):
    # New style object
    s = obj.__make__()
  else:
    s = dict(obj.__dict__)
  if isinstance(s, dict):
    for attr, v in s.iteritems():
      assert snapshotable(v), \
          '%s \'s attribute %s of value %s is not snapshotable' %\
          (type(obj), attr, type(v))
  elif isinstance(s, list):
    for element in s:
      assert snapshotable(element), \
          '%s \'s element %s is not snapshotable' %\
          (type(obj), type(element))
  return s

def restore_snapshot(obj, value, cur = None):
  if hasattr(obj, '__restore__'):
    # New style object
    obj.__restore__(value, cur)
  elif type(obj) == InstanceType:
    obj.__dict__ = value
  else:
    restore_as_dict(obj, value, cur)

def restore_as_dict(obj, value, cur = None):
  for attr in set(obj.__dict__.keys()) - set(value.keys()):
    delattr(obj, attr)
  for key, v in value.iteritems():
    setattr(obj, key, v)

def create_object(mytype, cls, *args, **kwds):
  from ..traced_frame import TracedFrame, FunctionDecision
  curframe = TracedFrame.current(True)
  if not curframe:
    # This is possible when initialize. Will only create primitive values
    return super(mytype, cls).__new__(cls)
  if not curframe.has_more_decisions():
    result = FunctionDecision(sideeffect = False)
    result.add_return_value(super(mytype, cls).__new__(cls, *args, **kwds))
    curframe.add_decision(result)
  return curframe.get_next_call_decision()
