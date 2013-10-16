from ..type_value import BuiltinType, match, CanBeNone, getRealValue,\
    hasRealValue

IntType = BuiltinType(int)  # Include int and long
IndexType = BuiltinType(int)  # Accepts class with __index__
BoolType = BuiltinType(bool)
FloatType = BuiltinType(float)
StringType = BuiltinType(str)
NotImplementedType = BuiltinType(type(NotImplemented))
NoneType = BuiltinType(type(None))
NoneType._BuiltinObjInstance__has_value__ = lambda : True

def NumValue(value):
  if type(value) == float:
    return FloatType(value)
  else:
    return IntType(value)
