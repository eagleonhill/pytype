from .defs import *
from .. import checker
from ..type_value.builtin_builder import *
from ..type_value.builtin_type import is_determined, get_determined_value

intTypeBuilder = Type('int', (int, long), [
  Func('__truediv__', ['i'], 'f'),
  Func('__rtruediv__', ['i'], 'f'),
  Func('__nonzero__', [''], 'b'),
  Func('__hash__', [''], 'i'),
])
intTypeBuilder.rebuild(IntTypeInternal)

for ops in ['add', 'sub', 'mul', 'div', 'floordiv', 'mod', 'pow',
    'lshift', 'rshift', 'and', 'xor', 'or']: 
  IntTypeInternal.add_binary_operator('__' + ops + '__')
  IntTypeInternal.add_binary_operator('__r' + ops + '__')
#IntTypeInternal.add_binary_operator('__divmod__', returnType=lambda: (IntTypeInternal, IntTypeInternal))

notGiven = object()
def int_new(cls, value, base = notGiven):
  if isinstance(value, StringType):
    if base is notGiven:
      base = 10
    if is_determined(value):
      return IntType.create_from_value(int(get_determined_value(value), base))
    else:
      return IntType.create_undetermined()
  elif hasattr(value, '__int__'):
    if base is not notGiven:
       checker.type_error("int() can't convert non-string with explicit base")
    return value.__int__()
  else:
    checker.convert_error(value, int)

def int_coerce(left, right):
  if isinstance(right, IntType):
    return (left, right)
  else:
    return NotImplemented

IntTypeInternal.add_stub_function('__coerce__', int_coerce)
IntTypeInternal.add_stub_function('__new__', int_new)

IntTypeInternal.add_unary_operator('__float__', returnType=FloatType)
IntTypeInternal.add_stub_function('__int__', lambda x: x)
IntTypeInternal.add_stub_function('__long__', lambda x: x)
def int_nonzero(value):
  return value != IntType.create_from_value(0)

IntTypeInternal.add_stub_function('__nonzero__', int_nonzero)
IntTypeInternal.add_default_compare()
IntTypeInternal.update_type(IntType)
