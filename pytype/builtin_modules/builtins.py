from ..type_value.builtin_builder import *
from ..builtin_types import *
from ..snapshot import BaseObject
from ..checker import raise_checker_error
import __builtin__

notgiven = object()

def builtin_sum(iter, start = notgiven):
  if start is notgiven:
    start = IntType.create_from_value(0)
  return sum(iter, start)

def builtin_len(obj):
  if not hasattr(type(obj), '__len__'):
    raise_checker_error(TypeError, \
        "object of type '%s' has no len()" % type(obj))
  v = obj.__len__()
  if not isinstance(v, IntType):
    raise_checker_error(TypeError, 'an integer is required')
  return v

def builtin_range(start, stop = notgiven, step = notgiven):
  v = None
  if stop is notgiven:
    stop = IntType(start)
    if is_determined(stop):
      v = range(get_determined_value(stop))
  else:
    start = IntType(start)
    stop = IntType(stop)
    if step is not notgiven:
      step = IntType(step)
    if is_determined((start, stop, step)):
      if step is notgiven:
        v = range(get_determined_value(start), get_determined_value(stop))
      else:
        v = range(*get_determined_value((start, stop, step)))
  if v is not None:
    ret = ListType()
    for x in v:
      ret.append(IntType.create_from_value(x))
    return ret
  else:
    ret = ListType([IntType.create_undetermined()])
    ret._to_undetermined()
    return ret

module = Module(
  __builtin__,
  [
    Func('raw_input', ['|S'], 's', call_default=False),
    Value('bool', bool),
    Value('int', IntType),
    Value('long', IntType),
    Value('float', FloatType),
    Value('str', StringType),
    Value('list', ListType),
    Value('dict', DictType),
    Value('type', type),
    Value('pow', pow),
    Value('isinstance', isinstance),
    Value('None', None),
    Value('True', True),
    Value('False', False),
    Value('object', BaseObject),
    Value('__import__', __builtin__.__import__),
    Value('StopIteration', StopIteration),
    Value('AssertionError', AssertionError),
    Value('len', builtin_len),
    Value('range', builtin_range),
    Value('sum', builtin_sum)
  ]
)
def export_module(g):
  export(g, module.build())

