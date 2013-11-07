from base import *
from .. import checker
from ..snapshot import SnapshotableMetaClass, Snapshotable, Immutable

# Implementation of type in C
class BuiltinTypeInternal(Immutable):
  def __init__(self, name, base):
    self.attr = {}
    self.base = base
    self.name = name
    self.export = None

  def check_value(self, value):
    return isinstance(value, self.base)

  def get_attr(self, name):
    import compare_func
    if name in self.attr:
      return self.attr[name]
    elif name in compare_func.default_cmp:
      return compare_func.default_cmp[name]
    else:
      checker.attr_error(self, name)
      return BadType()

  def create_from_value(self, value):
    assert self.check_value(value), \
        "{0} don't accept type {1}".format(self, value)
    return BuiltinObjInstance(self, value)
  def create_undetermined(self):
    return BuiltinObjInstance(self)

  def __repr__(self):
    return 'hooked class of ' + self.name
  def __str__(self):
    return 'class of ' + self.name

  def add_unary_operator(self, op, returnType = None):
    if returnType is None:
      returnType = self
    self.add_function(op, [], returnType)

  def add_binary_operator(self, op, returnType = None, otherType = None): 
    if returnType is None: 
      returnType = self
    if otherType is None: 
      otherType = self
    self.add_function(op, [otherType], returnType)

  def add_function(self, op, args, returnType, optionalArgs = None):
    self.get_function(op).add_pattern(args, optionalArgs, returnType)

  def get_function(self, op):
    from func_type import BuiltinFunc
    if op not in self.attr:
      self.attr[op] = BuiltinFunc(op)
    return self.attr[op]

  def add_function_format(self, op, args, returnType):
    self.get_function(op).add_from_format_str(args, returnType)

  def add_stub_function(self, op, func):
    from func_type import StubFunc
    self.attr[op] = StubFunc(func)

  def match(self, other):
    return self is other

  def get_type(self):
    if self.export == None:
      self.export = BuiltinType(self)
    return self.export

  def __str__(self):
    return 'type ' + self.name

class BuiltinType(type):
  def __new__(cls, t):
    val = super(BuiltinType, cls).__new__(cls, t.name, (t.base[0], ), {})
    val.__type = t
    t.export = val
    return val
  def __getattr__(self, name):
    from func_value import InstanceFunc, FuncValue
    val = self.__type.get_attr(name)
    if isinstance(val, FuncValue):
      val = InstanceFunc(val, self)
    return val

  def __call__(self, *args, **kargs):
    val = self.__type.get_attr('__new__')(self, *args, **kargs)
    return val

# Instance of builtin type, contains no public values
class BuiltinObjInstance:
  __metaclass__ = SnapshotableMetaClass
  #__slots__ = ['_type']
  def __init__(self, t, value = None):
    self._type = t
    self._value = value
  def __getattr__(self, name):
    return self._get_type_attr(name)
  def _get_type_attr(self, name):
    from func_type import InstanceFunc, FuncValue
    val = self._type.get_attr(name)
    if isinstance(val, FuncValue):
      val = InstanceFunc(val, self)
    return val
  def __typeeq__(self, other):
    if not isinstance(other, BuiltinObjInstance):
      return False
    return self._type is other._type
  def _pytypecheck_get_value(self):
    return self._value
  def _pytypecheck_is_determined(self):
    return self._value is not None
  def __str__(self):
    if is_determined(self):
      return '(' + str(self._type) + ': ' + str(self._value) + ')'
    else:
      return '(Undetermined ' + str(self._type) + ')'
  def __repr__(self):
    if is_determined(self):
      return '(' + str(self._type) + ': ' + str(self._value) + ')'
    else:
      return '(Undetermined ' + str(self._type) + ')'
  def _make_determined(self, value):
    assert not is_determined(self), 'Already have a value'
    assert self._type.check_value(value), "Not accepting " + repr(value)
    self._value = value
  def __makefits__(self, value):
    from ..makefits import FittingFailedException
    if self._type is not value._type:
      raise FittingFailedException
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

def is_determined(obj):
  if not hasattr(obj, '_pytypecheck_is_determined'):
    return True
  return obj._pytypecheck_is_determined()

def get_determined_value(obj):
  assert is_determined(obj), repr(obj) + ' is not determined'
  if hasattr(obj, '_pytypecheck_get_value'):
    return obj._pytypecheck_get_value()
  else:
    return obj
