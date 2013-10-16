from defs import *
from ..builtin_builder import *
import __builtin__

intTypeBuilder = Type('int', [
  Func('__truediv__', ['i'], 'f'),
  Func('__rtruediv__', ['i'], 'f'),
  Func('__nonzero__', [''], 'b'),
])
intTypeBuilder.rebuild(IntType)

IntType.check_value = lambda x: isinstance(x, int) or isinstance(x, long)

for ops in ['add', 'sub', 'mul', 'div', 'floordiv', 'mod', 'pow',
    'lshift', 'rshift', 'and', 'xor', 'or']: 
  IntType.add_binary_operator('__' + ops + '__')
  IntType.add_binary_operator('__r' + ops + '__')
#IntType.add_binary_operator('__divmod__', returnType=lambda: (IntType, IntType))

def int_coerce(left, right):
  if match(IntType, right):
    return (left, right)
  else:
    return NotImplemented
IntType.add_stub_function('__coerce__', int_coerce)

