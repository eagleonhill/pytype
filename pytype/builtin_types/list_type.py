from .defs import *
from . import defs
from ..checker import type_equal, reraise_error, get_current_frame
from ..makefits import type_make_fit_internal, type_make_fit
from ..type_value import get_determined_value, is_determined
from ..snapshot import SList, SnapshotableMetaClass
from ..traced_frame import FunctionDecision

class UndeterminedList:
  __metaclass__ = SnapshotableMetaClass
  def __init__(self, iterable = None):
    self._items = SList()
    self._types = SList()
    self._length = IntType.create_from_value(0)
    self._maybeempty = False
    if isinstance(iterable, UndeterminedList):
      self._items = SList(iterable._items)
      self._types = SList(iterable._types)
      self._length = iterable._length
    else:
      for item in iterable:
        self.append(item)

  def __typeeq__(self, other):
    return len(other._types) == len(self._types) and\
        all(lambda x: other._has_type(x), self._types)

  def __getitem__(self, index):
    if is_determined(self._length) and is_determined(index):
      try:
        return self._items[index]
      except:
        reraise_error()
    if type(index) == slice:
      ret = UndeterminedList(self)
      ret._length = IntType.create_undetermined()
      return ret
    
    cur_frame = get_current_frame()
    if not cur_frame.has_more_decisions():
      d = FunctionDecision(sideeffect=False)
      for t in self._types:
        d.add_return_value(t)
      cur_frame.add_decision(d)
    return cur_frame.get_next_decision(FunctionDecision)

  def __iter__(self):
    if is_determined(self._length):
      return self._items.__iter__()
    else:
      return self._types.__iter__()

  def _has_type(self, element):
    return any(map(lambda x: type_equal(x, element), self._types))
  
  def __add__(self, other):
    new = UndeterminedList(self)
    new += other
    return new

  def __iadd__(self, other):
    if not isinstance(other, UndeterminedList):
      checker.type_error(other, UndeterminedList)
    self._items = self._items + other._items
    for t in other._types:
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
    return is_determined(self._length)\
        and all(map(is_determined, self._items))

  def _pytypecheck_get_value(self):
    return self._items.data

  def __repr__(self):
    return 'List(items=' + str(self._items) + ', types=' + str(self._types) +\
        ', len=' + str(self._length)

  def __nonzero__(self):
    if is_determined(self._length):
      return get_determined_value(self._items) > 0
    elif len(self._types) > 0 and not self._maybeempty:
      return True
    elif len(self._types) == 0:
      return False
    else:
      if checker.fork():
        # Make it empty
        self.__init__()
        return False
      else:
        # Make it non empty
        self._maybeempty = False
        return True

  def __makefits__(self, other):
    assert isinstance(other, UndeterminedList)
    type_make_fit_internal(self._length, other._length)
    if is_determined(self._length):
      if type_make_fit(self._items, other._items):
        # _type should fit both, no need to combine
        return
      else:
        # Though have the same length, cannot combine values
        # Fall back to accept both values
        self._length = IntType.create_undetermined()
    # List size is undetermined, adding won't make any change
    self += other

UndeterminedList.__name__ = 'list'

defs.ListType = UndeterminedList
