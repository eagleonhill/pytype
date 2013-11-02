from defs import *
from .. import checker
from ..type_value.builtin_builder import *
from ..type_value import hooked_isinstance
from ..type_value.builtin_type import is_determined, get_determined_value

def bool_create_undetermined():
  if checker.fork():
    return True
  else:
    return False

BoolType.create_undetermined = bool_create_undetermined
  
def create_from_bool(value):
  assert isinstance(value, bool), repr(value) + ' is not bool'
  return value
BoolType.create_from_value = create_from_bool
