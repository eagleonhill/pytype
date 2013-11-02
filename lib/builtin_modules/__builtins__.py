from ..type_value.builtin_builder import *
from ..builtin_types import *
from ..snapshot import BaseObject
import __builtin__
def bool_def(value=None):
  if isinstance(value, bool):
    return value
  if value is None:
    return False
  if hasattr(value, '__nonzero__'):
    return value.__nonzero__()
  return True

module = Module(
  __builtin__,
  [
    Func('raw_input', ['|S'], 's', call_default=False),
    Value('bool', bool_def),
    Value('int', IntType.get_type()),
    Value('long', IntType.get_type()),
    Value('float', FloatType.get_type()),
    Value('str', StringType.get_type()),
    Value('list', ListType),
    Value('dict', DictType),
    Value('None', None),
    Value('True', True),
    Value('False', False),
    Value('object', BaseObject),
    Value('__import__', __builtin__.__import__),
  ]
)
def export_module(g):
  export(g, module.build())

