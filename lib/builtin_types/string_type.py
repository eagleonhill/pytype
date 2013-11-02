from defs import *
from .. import checker
from ..type_value.builtin_builder import *
import __builtin__

strType = Type('str', (str, ), [
  Func('__add__', ['s'], 's'),
  Func('__float__', [''], 'f'),
  Func('__mul__', ['i'], 's'),
  #Func('__getitem__', ['i'], 's'),
  Func('capitalize', [''], 's'),
  Func('center', ['i|s'], 's'),
  Func('count', ['s|LL'], 'i'),
  #decode
  #encode
  Func('endswith', ['s'], 'b'),
  Func('expandtabs', ['|i'], 's'),
  Func('find', ['s|LL'], 'i'),
  #format
  Func('index', ['s|LL'], 'i'),
  Func('isalnum', [''], 'b'),
  Func('isalpha', [''], 'b'),
  Func('isdigit', [''], 'b'),
  Func('islower', [''], 'b'),
  Func('isspace', [''], 'b'),
  Func('istitle', [''], 'b'),
  Func('isupper', [''], 'b'),
  #join
  Func('ljust', ['i|s'], 's'),
  Func('lower', [''], 's'),
  Func('lstrip', ['|S'], 's'),
  #partition
  Func('replace', ['ss|i'], 's'),
  Func('rfind', ['s|LL'], 'i'),
  #rsplit
  #rpartition
  Func('rindex', ['s|LL'], 'i'),
  Func('rjust', ['i|s'], 's'),
  Func('rstrip', ['|S'], 's'),
  #split
  #splitlines
  Func('startswith', ['s'], 'b'),
  Func('swapcase', [''], 's'),
  Func('title', [''], 's'),
  #translate
  Func('upper', [''], 's'),
  Func('zfill', ['i'], 's'),
])

strType.rebuild(StringType)

def str_coerce(left, right):
  if isinstance(right, StringType.get_type()):
    return (left, right)
  else:
    return NotImplemented

StringType.add_stub_function('__coerce__', str_coerce)

def str_nonzero(value):
  return value != StringType.create_from_value('')

StringType.add_stub_function('__nonzero__', str_nonzero)
