from base import Snapshotable
from types import GeneratorType
from ..checker import notify_update, reraise_error

class SGen(object):
  def __init__(self, gen):
    self.gen = gen
    self.dataset = []
    self.index = 0
    notify_update(self)
    print 'creating'

  def __iter__(self):
    return self

  def next(self):
    from ..traced_frame import DecisionSet, TracedFrame, FunctionDecision
    from ..revision import get_revisions
    cur_frame = TracedFrame.current()
    #print 'getting', self.index
    if cur_frame.has_more_decisions():
      #print 'other path'
      return cur_frame.get_next_call_decision()
    if self.index < len(self.dataset):
      #print 'reuse value'
      cur_frame.add_decision(self.dataset[self.index].clone())
      self.index += 1
      notify_update(self)
    else:
      #print 'new value'
      assert self.index == len(self.dataset), (self.index, len(self.dataset))
      new_frame = TracedFrame(FunctionDecision())
      rev = get_revisions().commit()
      self.index += 1
      notify_update(self)
      while new_frame.next_path():
        with new_frame:
          get_revisions().set_rev(rev)
          try:
            v = self.gen.next()
          except StopIteration:
            reraise_error()
          new_frame.result.add_return_value(v)
      self.dataset.append(new_frame.result.clone())
    return cur_frame.get_next_call_decision()

  def __make__(self):
    return self.index
  def __restore__(self, value, oldvalue = None):
    #print 'restore', self.index, value
    self.index = value
  def __makefits__(self, other):
    raise FittingFailedException

Snapshotable.register(SGen)
