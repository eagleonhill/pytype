from type_value import BuiltinType, match
from func_value import StubFunc

IntType = BuiltinType(int)  # Include int and long
IntType.check_value = lambda x: isinstance(x, int) or isinstance(x, long)
IndexType = BuiltinType(int)  # Accepts class with __index__
BoolType = BuiltinType(bool)
FloatType = BuiltinType(float)
StringType = BuiltinType(str)
NotImplementedType = BuiltinType(NotImplemented)

def addUnaryOperator(c, op, returnType = None)
  if returnType is None: 
    returnType = c
  c.add_builtin_call_pattern(op, [], returnType)

def addBinaryOperator(c, op, returnType = None, otherType = None): 
  if returnType is None: 
    returnType = c
  if otherType is None: 
    otherType = c
  c.add_builtin_call_pattern(op, [otherType], returnType)

def addFunction(c, op, args, returnType, optionalArgs = None)
  c.add_builtin_call_pattern(op, [otherType], returnType, optionalArgs)

def BoolCoerce(left, right):
  x = left
  if match(BoolType, right):

for ops in ['add', 'sub', 'mul', 'div', 'floordiv', 'mod', 'pow',
    'lshift', 'rshift', 'and', 'xor', 'or']: 
  addBinaryOperator(IntType, '__' + ops + '__')
  addBinaryOperator(IntType, '__' + ops + '__')
  addBinaryOperator(IntType, '__i' + ops + '__')
#addBinaryOperator(IntType, '__divmod__', returnType=lambda: (IntType, IntType))
addBinaryOperator(IntType, '__truediv__', returnType=FloatType)
addBinaryOperator(IntType, '__itruediv__', returnType=FloatType)

def IntCoerce(left, right):
  if match(IntType, right):
    return (left, right)
  else:
    return NotImplemented

for ops in ['add', 'sub', 'mul', 'div', 'floordiv', 'mod', 'pow', 'truediv']: 
  addBinaryOperator(FloatType, '__' + ops + '__')
  addBinaryOperator(FloatType, '__r' + ops + '__')
  addBinaryOperator(FloatType, '__i' + ops + '__')

def FloatCoerce(left, right):
  value = getRealValue(right)
  if match(FloatType, right) or match(BoolType, right) or match(IntType, right):
    if value is not None:
      value = float(value)
    return (left, FloatType(value))
  else:
    return NotImplemented

FloatType.attr['__coerce__'] = StubFunc(FloatCoerce)

addBinaryOperator(StringType, '__add__')
addBinaryOperator(StringType, '__mul__', otherType=IntType)
addFunction(StringType, 'find', [StringType], IntType, 
    [CanBeNone(IntType), CanBeNone(IntType)])
