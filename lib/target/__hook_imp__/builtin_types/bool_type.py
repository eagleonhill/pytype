from defs import *

for ops in ['and', 'xor', 'or']:
  BoolType.add_binary_operator('__' + ops + '__')
  BoolType.add_binary_operator('__r' + ops + '__')

for ops in ['add', 'sub', 'mul', 'div', 'floordiv', 'mod', 'pow',
    'lshift', 'rshift', 'and', 'xor', 'or']: 
  BoolType.add_binary_operator('__' + ops + '__', returnType=IntType)
  BoolType.add_binary_operator('__r' + ops + '__', returnType=IntType)

  BoolType.add_binary_operator('__' + ops + '__', otherType=IntType,
      returnType=IntType)
  BoolType.add_binary_operator('__r' + ops + '__', otherType=IntType,
      returnType=IntType)

def bool_coerce(left, right):
  x = left
  if match(BoolType, right):
    return (left, right)
  elif match(IntType, right):
    return (left, right)
  return NotImplemented

BoolType.add_stub_function('__coerce__', bool_coerce)

