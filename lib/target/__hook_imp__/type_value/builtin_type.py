from base import *
from .. import checker

# Implementation of type in C
class BuiltinTypeInternal:
  def __init__(self, name, base):
    self.attr = {}
    self.base = base
    self.name = name
    self.export = None

  def check_value(self, value):
    return isinstance(value, self.base)

  def get_attr(self, name):
    if name in self.attr:
      return self.attr[name]
    else:
      checker.attr_error(self, name)
      return BadType()

  def create_from_value(self, value):
    assert self.check_value(value), \
        "{0} don't accept type {1}".format(self, value)
    return BuiltinObjDeterminedInstance(self, value)
  def create_undetermined(self):
    return BuiltinObjUndeterminedInstance(self)

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
  #__slots__ = ['_type']
  def __init__(self, *args, **kargs):
    raise NotImplementedError('Calling abstract method')
  def __getattr__(self, name):
    return self._get_type_attr(name)
  def _get_type_attr(self, name):
    from func_type import InstanceFunc, FuncValue
    val = self._type.get_attr(name)
    if isinstance(val, FuncValue):
      val = InstanceFunc(val, self)
    return val
  def _pytypecheck_is_determined(self):
    raise NotImplementedError()
  def __nonzero__(self):
    try:
      l = self._get_type_attr('__nonzero__')()
    except AttributeError as e:
      try:
        l = self.__len__()
      except AttributeError as e2:
        l = True
    if not hooked_isinstance(l, bool):
      checker.type_error(l, bool)
    if is_determined(l):
      return get_determined_value(l)
    import os
    if os.fork():
      return True
    else:
      return False

class BuiltinObjDeterminedInstance(BuiltinObjInstance):
  #__slots__ = ['_value']
  def __init__(self, t, value = None):
    if isinstance(value, BuiltinObjInstance):
      value = getRealValue(value)
    assert value == None or t.check_value(value), (t, value)
    self._type = t
    self._value = value
  def _pytypecheck_get_value(self):
    return self._value
  def _pytypecheck_is_determined(self):
    return True
  def __str__(self):
    return '(' + str(self._type) + ': ' + str(self._value) + ')'
  def __repr__(self):
    return '(' + str(self._type) + ': ' + str(self._value) + ')'

class BuiltinObjUndeterminedInstance(BuiltinObjInstance):
  #__slots__ = []
  def __init__(self, t):
    self._type = t
  def _pytypecheck_is_determined(self):
    return False
  def __str__(self):
    return '(Undetermined ' + str(self._type) + ')'
  def __repr__(self):
    return '(Undetermined ' + str(self._type) + ')'

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
