import __hook_imp__.builtin_types as t

def num_const(value):
  if type(value) == float:
    return t.FloatType.create_from_value(value)
  else:
    return t.IntType.create_from_value(value)

def str_const(value):
  return t.StringType.create_from_value(value)

def list_const(value):
  return t.ListType._create_from_real_list(value)
