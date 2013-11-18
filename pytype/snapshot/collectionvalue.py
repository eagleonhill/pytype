from .metaclass import SnapshotableMetaClass
from .base import Snapshotable
from .slist import SList
from ..traced_frame import DecisionSet, TracedFrame
from ..checker import raise_checker_error, notify_update

AGGRESSIVE_LIMIT = 5
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
    cur_frame = TracedFrame.current()
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
  def __makefits__(self, other, context):
    if self.decision is not other.decision:
      context.fail()
    v = context.get_data(other)
    if v != self.may_stop_iter:
      context.fail()

class CollectionValue(object):
  def __init__(self, values=None):
    self.values = SList()
    self._flags = 0
    notify_update(self)
    if values:
      for v in values:
        self.addvalue(v)
  def _create_context(self):
    from ..makefits import FittingContext
    return FittingContext(self.flags)
  def update_flag(self, context):
    from ..makefits import FittingContext
    new_flag = self.flags
    if len(self.values) > AGGRESSIVE_LIMIT:
      new_flag |= FittingContext.FITS_LIST | \
          FittingContext.FITS_DICT | FittingContext.FITS_BUILTIN_VALUE
    type(self).flags.fset(self, new_flag, context)
  @property
  def flags(self):
    return self._flags

  @flags.setter
  def flags(self, value, context = None):
    if value != self._flags:
      self._flags = value
      notify_update(self)
      self.remerge_values(context)
  def remerge_values(self, context):
    v = list(self.values)
    self.values[:] = []
    for x in v:
      self.addvalue(x, context)
  def addvalue(self, value, context = None):
    if context is None:
      context = self._create_context()
      old_flag = context.flags
    else:
      self.flags |= context.flags
      old_flag = context.set_flags(self.flags)
    try:
      for v in self.values:
        if context.try_fit(v, value):
          return
      self.values.append(value)
      self.update_flag(context)
    finally:
      context.set_flags(old_flag)
  def deref(self):
    cur_frame = TracedFrame.current()
    assert cur_frame, 'Root frame is not set'
    if cur_frame.has_more_decisions():
      return cur_frame.get_next_decision(CollectionDerefDecision)
    cur_frame.add_decision(CollectionDerefDecision(self))
    return cur_frame.get_next_decision(CollectionDerefDecision)
  def iterator(self, nonempty):
    return CollectionGen(self, not nonempty)
  def clone(self):
    new = CollectionValue()
    new.values = SList(self.values)
  def __repr__(self):
    return '{ValueSet: %s}' % ', '.join(repr(x) for x in self.values)
  def __makefits__(self, other, context):
    if not isinstance(other, CollectionValue):
      context.fail()
    self.flags = self.flags | context.get_data(other)
    for v in context.get_data(other.values):
      self.addvalue(v, context)
  def __make__(self):
    return self.flags
  def __restore__(self, value, oldvalue = None):
    self.flags = value

Snapshotable.register(CollectionGen)
Snapshotable.register(CollectionValue)
__all__ = ['CollectionValue', 'CollectionGen', 'CollectionDerefDecision']
