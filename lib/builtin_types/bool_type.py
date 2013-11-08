from defs import *
from .. import checker

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
