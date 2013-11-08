from ..type_value.builtin_builder import *
from ..builtin_types import *
from ..snapshot import BaseObject
import __builtin__

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
  ]
)
def export_module(g):
  export(g, module.build())

