from defs import *
import defs
from ..type_value.meta_type import *

class List:
  __metaclass__ = MetaType
  def __init__(self, iterable = None):
    self.items = []
    self.types = []
    self.length = IntType(0)
    self.basetype = ListType
    if isinstance(iterable, List):
      self.items = list(iterable.items)
      self.types = list(iterable.types)
      self.length = IntValue(iterable.length)
    else:
      self.items = list(iterable)
      self.length = IntType(len(iterable))

  def __add__(self, other):
    if not isinstance(other, list):
      checker.type_error(other, ListType)
    meta2 = getMeta(other)
    newmeta = List()
    newmeta.items = self.items + meta2.items
    newmeta.types = self.types
    for t in meta2.types:
      if any(map(lambda x: typeequal(t, x), self.types)):
        continue
      newmeta.types.append(t)
    newmeta.length = self.length + meta2.length
    return newmeta

  def __len__(self):
    return self.length

  def __str__(self):
    return 'List(items=' + str(self.items) + ', types=' + str(self.types) +\
        ', len=' + str(self.length)

defs.ListType = List
