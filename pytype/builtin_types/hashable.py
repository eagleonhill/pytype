from .defs import *
from ..checker import raise_checker_error
class Hash(object):
  __slots__ = ['hash', 'value']
  def __init__(self, obj):
    hashf = type(obj).__hash__
    if not callable(hashf):
      raise_checker_error(TypeError, 'unhashable type %s' % t)
    h = hashf(obj)
    assert type(h) == IntType, 'Hashing an internal object'
    if is_determined(h):
      self.hash = get_determined_value(h)
      self.value = obj
    else:
      self.hash = None
      self.value = obj
  def __eq__(self, other):
    return self.value == other.value
  def __hash__(self):
    return self.hash
  def __repr__(self):
    return repr(self.value)
  def __str__(self):
    return str(self.value)
