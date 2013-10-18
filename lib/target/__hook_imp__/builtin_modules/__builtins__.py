def __define_module():
  from ..type_value.builtin_builder import *
  from ..builtin_types import *
  import __builtin__
  module = Module(
    __builtin__,
    [
      Func('raw_input', ['|S'], 's', call_default=False),
      Value('int', IntType.get_type()),
      Value('long', IntType.get_type()),
      Value('float', FloatType.get_type()),
      Value('bool', BoolType.get_type()),
      Value('str', StringType.get_type()),
      Value('True', BoolType.create_from_value(True)),
      Value('False', BoolType.create_from_value(False)),
    ]
  )
  export(globals(), module.build())

__define_module()
del __define_module
