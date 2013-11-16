from . import builtin_types as t
from .traced_frame import TracedFunction, return_value
from .revision.block import do_block, frame
from .revision.loop_block import do_while, loop_break, do_for, for_next

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
