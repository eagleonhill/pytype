from defs import *
from .. import checker
from ..type_value.builtin_builder import *
from ..type_value.builtin_type import is_determined, get_determined_value

floatTypeBuilder = Type('float', (float, ), [
  Func('__nonzero__', [''], 'b'),
])

floatTypeBuilder.rebuild(FloatTypeInternal)

for ops in ['add', 'sub', 'mul', 'div', 'floordiv', 'mod', 'pow']: 
  FloatTypeInternal.add_binary_operator('__' + ops + '__')
  FloatTypeInternal.add_binary_operator('__r' + ops + '__')
  FloatTypeInternal.add_binary_operator('__' + ops + '__', otherType=IntType)
  FloatTypeInternal.add_binary_operator('__r' + ops + '__', otherType=IntType)

def float_coerce(left, right):
  if isinstance(right, FloatType) or \
      isinstance(right, IntType):
    t = FloatType(right)
    return  (left, t)
  else:
    return NotImplemented

FloatTypeInternal.add_stub_function('__coerce__', float_coerce)

def float_new(cls, value):
  assert type(value) != float, 'Got a constant float in runtime'
  if hasattr(value, '__float__'):
    return value.__float__()
  else:
    checker.convert_error(value, float)

FloatTypeInternal.add_stub_function('__new__', float_new)

FloatTypeInternal.add_unary_operator('__int__', returnType=IntType)
FloatTypeInternal.add_unary_operator('__long__', returnType=IntType)
def float_nonzero(value):
  return value != FloatType.create_from_value(0.0)

FloatTypeInternal.add_stub_function('__nonzero__', float_nonzero)
FloatTypeInternal.add_stub_function('__float__', lambda x:x)
FloatTypeInternal.add_default_compare()
FloatTypeInternal.update_type(FloatType)
