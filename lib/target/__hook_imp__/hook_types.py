import __hook_imp__.builtin_types as t

def num_const(value):
  if type(value) == float:
    return t.FloatType.create_from_value(value)
  else:
    return t.IntType.create_from_value(value)

def str_const(value):
  return t.StringType.create_from_value(value)

def list_const(value):
  return t.ListType(value)

def dict_const(key, value):
  d = t.DictType()
  for k, v in zip(key, value):
    d[k] = v
  return d

def dict_unkwargs(d):
  return t.DictType._from_kwargs(d)

def dict_kwargs(d):
  if not isinstance(d, t.DictType):
    checker.type_error(d, t.DictType)
  return d._to_kwargs()
