from defs import *
from .. import checker
from ..type_value.builtin_builder import *
from ..type_value import hooked_isinstance
from ..type_value.builtin_type import is_determined, get_determined_value

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
  if hooked_isinstance(right, bool):
    return (left, right)
  elif hooked_isinstance(right, (int, long)):
    return (left, right)
  return NotImplemented

BoolType.add_stub_function('__coerce__', bool_coerce)
BoolType.add_unary_operator('__int__', returnType=IntType)
BoolType.add_unary_operator('__long__', returnType=IntType)
BoolType.add_unary_operator('__float__', returnType=FloatType)
BoolType.add_stub_function('__nonzero__', lambda x:x)

