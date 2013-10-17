from ..type_value import BuiltinType, CanBeNone, getRealValue,\
    hasRealValue

__metaclass__ = BuiltinType

class IntType:  # Include int and long
  __real_type = int
  def __new__(cls, val = None, base = 10):
    return val

class IndexType(IntType):  # Accepts class with __index__
  __real_type = int

class BoolType(IntType):
  __real_type = bool

class FloatType:
  __real_type = float
  def __new__(cls, val = None, base = 10):
    return val

class StringType:
  __real_type = str
  def __new__(cls, val = None):
    return val

class NotImplementedType:
  __real_type = type(NotImplemented)

class NoneType:
  __real_type = type(None)

NoneType._BuiltinObjInstance__has_value__ = lambda : True

ListType = None
DictType = None

def NumValue(value):
  if type(value) == float:
    return FloatType(value)
  else:
    return IntType(value)
