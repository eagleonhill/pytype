from defs import *
from ..builtin_builder import *

floatTypeBuilder = Type('float', [
  Func('__nonzero__', [''], 'b'),
])

floatTypeBuilder.rebuild(FloatType)

for ops in ['add', 'sub', 'mul', 'div', 'floordiv', 'mod', 'pow']: 
  FloatType.add_binary_operator('__' + ops + '__')
  FloatType.add_binary_operator('__r' + ops + '__')

def float_coerce(left, right):
  value = getRealValue(right)
  if match(FloatType, right) or match(BoolType, right) or match(IntType, right):
    if value is not None:
      value = float(value)
    return (left, FloatType(value))
  else:
    return NotImplemented

FloatType.add_stub_function('__coerce__', float_coerce)

