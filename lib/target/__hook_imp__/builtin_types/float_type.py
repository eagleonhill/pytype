from defs import *
from .. import checker
from ..type_value.builtin_builder import *
from ..type_value import hooked_isinstance
from ..type_value.builtin_type import is_determined, get_determined_value

floatTypeBuilder = Type('float', (float, ), [
  Func('__nonzero__', [''], 'b'),
])

floatTypeBuilder.rebuild(FloatType)

for ops in ['add', 'sub', 'mul', 'div', 'floordiv', 'mod', 'pow']: 
  FloatType.add_binary_operator('__' + ops + '__')
  FloatType.add_binary_operator('__r' + ops + '__')

def float_coerce(left, right):
  if hooked_isinstance(right, float) or \
      hooked_isinstance(right, (int, long)):
    t = FloatType.get_type()(right)
    return  (left, t)
  else:
    return NotImplemented

FloatType.add_stub_function('__coerce__', float_coerce)

def float_new(cls, value):
  assert type(value) != float, 'Got a constant float in runtime'
  if hasattr(value, '__float__'):
    return value.__float__()
  else:
    checker.convert_error(value, float)

FloatType.add_stub_function('__new__', float_new)

FloatType.add_unary_operator('__int__', returnType=IntType)
FloatType.add_unary_operator('__long__', returnType=IntType)
FloatType.add_unary_operator('__nonzero__', returnType=BoolType)
FloatType.add_stub_function('__float__', lambda x:x)
