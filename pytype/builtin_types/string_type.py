from .defs import *
from .. import checker
from ..type_value.builtin_builder import *
from ..type_value import is_determined, get_determined_value

strType = Type('str', (str, ), [
  Func('__add__', ['s'], 's'),
  Func('__float__', [''], 'f'),
  Func('__hash__', [''], 'i'),
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

strType.rebuild(StringTypeInternal)

def str_mod(s, var):
  if is_determined(s) and is_determined(var):
    return StringType.create_from_value(
        get_determined_value(s) % get_determined_value(var))
  return StringType.create_undetermined()

StringTypeInternal.add_stub_function('__mod__', str_mod)

def str_coerce(left, right):
  if isinstance(right, StringType):
    return (left, right)
  else:
    return NotImplemented

StringTypeInternal.add_stub_function('__coerce__', str_coerce)

def str_nonzero(value):
  return value != StringType.create_from_value('')

StringTypeInternal.add_stub_function('__nonzero__', str_nonzero)
StringTypeInternal.add_default_compare()
StringTypeInternal.update_type(StringType)
