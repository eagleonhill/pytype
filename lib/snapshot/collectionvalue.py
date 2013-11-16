from .metaclass import SnapshotableMetaClass
from .base import Immutable
from .slist import SList
from ..traced_frame import DecisionSet, TracedFrame
from ..checker import raise_checker_error, notify_update
from ..makefits import type_make_fit

class CollectionDerefDecision(DecisionSet):
  def __init__(self, collection = None):
    self.index = 0
    self.may_stop_iter = False
    self.values = list(collection.values) if collection else []
  def has_next(self):
    return self.index + 1 < len(self.values) + int(self.may_stop_iter)
  def goto_next(self):
    self.index += 1
  def current(self):
    if self.index == len(self.values) and self.may_stop_iter:
      raise_checker_error(StopIteration)
    return self.values[self.index]
  def clone(self):
    c = CollectionDerefDecision()
    c.values = self.values
    return c

class CollectionGen(object):
  def __init__(self, collection, may_stop_iter = True):
    self.decision = CollectionDerefDecision(collection)
    self.may_stop_iter = may_stop_iter
  def __iter__(self):
    return self
  def next(self):
    if cur_frame.has_more_decisions():
      return cur_frame.get_next_decision(CollectionDerefDecision)
    c = self.decision.clone()
    c.may_stop_iter = self.may_stop_iter
    self.may_stop_iter = True
    notify_update(self)
    cur_frame.add_decision(c)
    return cur_frame.get_next_decision(CollectionDerefDecision)
  def __make__(self):
    return self.may_stop_iter
  def __restore__(self, value, oldvalue=None):
    self.may_stop_iter = value

class CollectionValue(object):
  def __init__(self, values=None):
    self.values = SList()
    if values:
      for v in values:
        self.addvalue(v)
  def addvalue(self, value):
    for v in self.values:
      if type_make_fit(v, value):
        return
    self.values.append(value)
  def deref(self):
    cur_frame = TracedFrame.current()
    assert cur_frame, 'Root frame is not set'
    if cur_frame.has_more_decisions():
      return cur_frame.get_next_decision(CollectionDerefDecision)
    cur_frame.add_decision(CollectionDerefDecision(self))
    return cur_frame.get_next_decision(CollectionDerefDecision)
  def gen(self, nonempty):
    return CollectionGen(self.values, not nonempty)

Immutable.register(CollectionValue)
__all__ = ['CollectionValue', 'CollectionGen', 'CollectionDerefDecision']
