def __define_module():
  from ..type_value.builtin_builder import *
  from ..builtin_types import *
  import __builtin__
  module = Module(
    __builtin__,
    [
      Func('raw_input', ['|S'], 's', call_default=False),
      Func('int', ['s|i', 'i', 'f'], 'i'),
      Func('float', ['s', 'i', 'f'], 'f'),
      Value('True', BoolType(True)),
      Value('False', BoolType(False)),
    ]
  )
  export(globals(), module.build())

__define_module()
del __define_module
