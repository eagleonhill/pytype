from defs import *
import defs
from ..checker import type_equal

class UndeterminedList:
  #__metaclass__ = GenericList
  def __init__(self, iterable = None):
    self._items = []
    self._types = []
    self._length = IntType.create_from_value(0)
    if isinstance(iterable, UndeterminedList):
      self._items = list(iterable._items)
      self._types = list(iterable._types)
      self._length = iterable._length
    else:
      for item in iterable:
        self.append(item)

  def __typeeq__(self, other):
    return len(other._types) == len(self._types) and\
        all(lambda x: other._has_type(x), self._types)

  def __getitem__(self, index):
    # TODO
    raise NotImplementedError()
    if is_determined(self._length) and is_determined(index):
      return self._items[index]

  def _has_type(self, element):
    return any(map(lambda x: type_equal(x, element), self._types))
  
  def __add__(self, other):
    new = List(self)
    new += other
    return new

  def __iadd__(self, other):
    if not isinstance(other, UndeterminedList):
      checker.type_error(other, UndeterminedList)
    self._items = self._items + other._items
    for t in other.types:
      if not self._has_type(t):
        self._types.append(t)
    self._length = self._length + other._length
    return self

  def append(self, element):
    if is_determined(self._length):
      self._items.append(element)
    self._add_type(element)
    self._length += IntType.create_from_value(1)

  def _add_type(self, element):
    if not self._has_type(element):
      self._types.append(element)
  
  def __len__(self):
    return self._length

  def _pytypecheck_is_determined(self):
    return len(self._types) == 0 and all(map(is_determined, self._items))

  def __repr__(self):
    return 'List(items=' + str(self._items) + ', types=' + str(self._types) +\
        ', len=' + str(self._length)

defs.ListType = UndeterminedList
