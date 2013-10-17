from base import *
from .. import checker

# Implementation of type in C
class BuiltinType(TypeValue):
  def __new__(cls, name, base, defs):
    orig = defs.get('__new__')
    def create(cls, *args, **kargs):
      value = orig(cls, *args, **kargs)
      if not isinstance(value, BuiltinObjInstance):
        return BuiltinObjInstance(cls, value)
      else:
        return value
    defs['__new__'] = create

    t = super(BuiltinType, cls).__new__(cls, name, base, defs)
    return t
  def __init__(self, name, base, defs):
    real_type = defs['_' + name + '__real_type']
    self.attr = {}
    self.base = base
    self.real_type = real_type

  def check_value(self, value):
    return type(value) == self.real_type

  def get_attr(self, name):
    if name in self.attr:
      return self.attr[name]
    else:
      checker.attr_error(self, name)
      return BadType()

  def __call__(self, value = None):
    if isinstance(value, BuiltinObjInstance):
      value = getRealValue(value)
    return BuiltinObjInstance(self, value)

  def __repr__(self):
    return 'Instance of ' + self.real_type.__name__
  def __str__(self):
    return 'Instance of ' + self.real_type.__name__

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

  def __instancecheck__(self, instance):
    if issubclass(instance.__class__, int):
      return True
    if not isinstance(instance, BuiltinObjInstance):
      return False
    return typeEqual(getType(instance), self)

class BuiltinObjStatic(ValueInstance):
  def __init__(self, t):
    self.__type = t
  def __get_type__(self):
    return self.__type
  def __getattr__(self, name):
    if name == '__type':
      return self.__get_type__()
    elif name == '__value':
      return self.__get_type__().real_type
    elif name == '__has_value':
      return True
    from func_value import InstanceFunc, FuncValue
    val = self.__type.get_attr(name)
    if isinstance(val, FuncValue):
      val = InstanceFunc(val, self)
    return val

  def __call__(self, *args, **kargs):
    # TODO:Create an instance
    pass
  def __str__(self):
    return str((self.__type, self.__value))
  def __repr__(self):
    return repr((self.__type, self.__value))
      
# Instance of builtin type, contains no public values
class BuiltinObjInstance(ValueInstance):
  def __init__(self, t, value = None):
    if isinstance(value, BuiltinObjInstance):
      value = getRealValue(value)
    assert value == None or t.check_value(value), (t, value)
    self.__type = t
    self.__value = value
    self.__meta = None
  def __get_type__(self):
    return self.__type
  def __get_value__(self):
    return self.__value
  def __has_value__(self):
    return self.__value != None
  def __getattr__(self, name):
    if name == '__type':
      return self.__get_type__()
    elif name == '__value':
      return self.__get_value__()
    elif name == '__has_value':
      return self.__has_value__()
    return self.__get_type_attr(name)
  def __get_type_attr(self, name):
    from func_type import InstanceFunc, FuncValue
    val = self.__type.get_attr(name)
    if isinstance(val, FuncValue):
      val = InstanceFunc(val, self)
    return val
  def __str__(self):
    return str((self.__type, self.__value))
  def __repr__(self):
    return repr((self.__type, self.__value))
  def __nonzero__(self):
    try:
      l = self.__get_type_attr('__nonzero__')()
    except AttributeError as e:
      try:
        l = self.__len__()
      except AttributeError:
        return True
    if hasRealValue(l):
      return True if getRealValue(l) else False
    import os
    if os.fork():
      return True
    else:
      return False
