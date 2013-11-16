from .base import *
from .. import checker
from ..snapshot import SnapshotableMetaClass, Snapshotable, Immutable,\
    BaseObject

# Implementation of type in C
class BuiltinTypeInternal(Immutable):
  def __init__(self, name, base):
    self.attr = {}
    self.base = base
    self.name = 'hook' + name
    self.export = None

  def check_value(self, value):
    return isinstance(value, self.base)

  def get_attr(self, name):
    from . import compare_func
    if name in self.attr:
      return self.attr[name]
    else:
      checker.attr_error(self, name)
      return BadType()

  def add_unary_operator(self, op, returnType = None):
    if returnType is None:
      returnType = self.create_type()
    self.add_function(op, [], returnType)

  def add_default_compare(self):
    from .compare_func import default_cmp
    self.attr.update(default_cmp)

  def add_binary_operator(self, op, returnType = None, otherType = None): 
    if returnType is None: 
      returnType = self.create_type()
    if otherType is None: 
      otherType = self.create_type()
    self.add_function(op, [otherType], returnType)

  def add_function(self, op, args, returnType, optionalArgs = None):
    self.get_function(op).add_pattern(args, optionalArgs, returnType)

  def get_function(self, op):
    from .func_type import BuiltinFunc
    if op not in self.attr:
      self.attr[op] = BuiltinFunc(op)
    return self.attr[op]

  def add_function_format(self, op, args, returnType):
    self.get_function(op).add_from_format_str(args, returnType)

  def add_stub_function(self, op, func):
    from .func_type import StubFunc
    self.attr[op] = StubFunc(func)

  def match(self, other):
    return self is other

  def update_type(self, t):
    for key in self.attr:
      setattr(t, key, self.attr[key])
    # t can't be changed any more
    t._pytype_make_internal_type()

  def create_type(self):
    if self.export is None:
      self.export = SnapshotableMetaClass(\
          self.name, (BuiltinObjInstance,), \
          {'_internal': self})
    return self.export

# Instance of builtin type, contains no public values
class BuiltinObjInstance(BaseObject):
  __metaclass__ = SnapshotableMetaClass
  def _pytypecheck_get_value(self):
    return self._value
  def _pytypecheck_is_determined(self):
    return self._value is not None
  # Should be removed, for debugging only at this stage
  def __str__(self):
    if is_determined(self):
      return '(' + type(self).__name__ + ': ' + str(self._value) + ')'
    else:
      return '(Undetermined ' + type(self).__name__ + ')'
  def __repr__(self):
    if is_determined(self):
      return '(' + type(self).__name__ + ': ' + str(self._value) + ')'
    else:
      return '(Undetermined ' + type(self).__name__ + ')'
  def _make_determined(self, value):
    assert not is_determined(self), 'Already have a value'
    assert type(self)._internal.check_value(value),\
        "Not accepting " + repr(value)
    self._value = value
  def __makefits__(self, value):
    # Discard all compare history
    if is_determined(self) and is_determined(value):
      if self._value != value._value:
        self._value = None
      else:
        return
    self._value = None
    try:
      del self._CompareHistory__comparer
    except AttributeError:
      pass
  @classmethod
  def create_from_value(cls, value):
    assert cls._internal.check_value(value), \
        "{0} don't accept type {1}".format(cls, value)
    v = super(BuiltinObjInstance, cls).__new__(cls)
    v._value = value
    return v
  @classmethod
  def create_undetermined(cls):
    v = super(BuiltinObjInstance, cls).__new__(cls)
    v._value = None
    return v

def is_determined(obj):
  if isinstance(obj, slice):
    return is_determined(obj.start) and is_determined(obj.stop) \
        and is_determined(obj.step)
  elif isinstance(obj, tuple):
    return all(is_determined(x) for x in obj)
  elif not hasattr(obj, '_pytypecheck_is_determined'):
    return True
  return obj._pytypecheck_is_determined()

def get_determined_value(obj):
  assert is_determined(obj), repr(obj) + ' is not determined'
  if hasattr(obj, '_pytypecheck_get_value'):
    return obj._pytypecheck_get_value()
  elif isinstance(obj, slice):
    return slice(obj.start, obj.stop, obj.step)
  elif isinstance(obj, tuple):
    return tuple(get_determined_value(x) for x in obj)
  else:
    return obj
