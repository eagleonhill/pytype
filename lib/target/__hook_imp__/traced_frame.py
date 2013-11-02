import checker
from revision import get_revisions

class TracedFrame:
  """
  A function call frame which records all possible return values and errors
  that may be raised, and maintain all undetermined decisions during
  evaluations."""
  def __init__(self, back):
    self.throws = []
    self.back = back
    self.decision_list = []
    self.decision_made = 0
    self.total_decision = 0
    self.result = None
  def __enter__(self):
    self.running = True
    self.back = get_revisions().traced_frame
    get_revisions().traced_frame = self
  def __exit__(self, exc_type, exc_value, traceback):
    get_revisions().traced_frame = self.back
    self.running = False
    if exc_type is TracedFrame.DuplicatedPathError:
      return True
    elif exc_type is TracedFrame.ImpossiblePathError:
      return True
    elif exc_type:
      self.result.add_exception(exc_type, exc_value, traceback)
      return True
  def next_path(self):
    self.decision_made = 0
    if self.result is None:
      self.result = FunctionDecision()
      self.decision_list = []
      return True
    while len(self.decision_list) and\
        not self.decision_list[-1].has_next():
      self.decision_list.pop()
    if self.decision_list:
      self.decision_list[-1].goto_next()
      return True
    else:
      return False

  def get_next_bool_decision(self):
    if not self.has_more_decisions():
      self.add_decision(BooleanDecision())
    d = self.pop_decision()
    assert isinstance(d, BooleanDecision)
    return d.current()
  def get_next_call_decision(self):
    assert self.has_more_decisions()
    d = self.pop_decision()
    assert isinstance(d, FunctionDecision), 'Expecting function decision ' +\
        repr(d) + repr( self.decision_made) + repr(self.decision_list)
    return d.current()
  def add_decision(self, decision):
    assert not self.has_more_decisions()
    self.decision_list.append(decision)
  def impossible_path(self):
    raise TracedSection.ImpossiblePathError()
  def duplicated_path(self):
    raise TracedSection.DuplicatedPathError()
  def has_more_decisions(self):
    return self.decision_made < len(self.decision_list)
  def pop_decision(self):
    d = self.decision_list[self.decision_made]
    self.decision_made += 1
    return d
  class ImpossiblePathError(Exception):
    pass
  class DuplicatedPathError(Exception):
    pass

class DecisionSet:
  """ Abstract class of an undetermined decision"""
  def __init__(self):
    raise NotImplementedError('Abstract class')
  def has_next(self):
    pass
  def current(self):
    pass
  def goto_next(self):
    pass

class BooleanDecision(DecisionSet):
  def __init__(self):
    self.value = False
  def has_next(self):
    return self.value == False
  def goto_next(self):
    self.value = True
  def current(self):
    return self.value

class FunctionDecision(DecisionSet):
  def __init__(self):
    self.return_values = []
    self.start_revision = get_revisions().commit()
    self.exceptions = []
    self.index = 0
  def add_exception(self, exc_type, exc_value, traceback):
    revision = get_revisions().commit()
    self.exceptions.append((exc_type, exc_value, traceback, revision))
  def add_return_value(self, value):
    revision = get_revisions().commit()
    self.return_values.append((value, revision))
  def has_next(self):
    return self.index + 1 < len(self.return_values) + len(self.exceptions)
  def current(self):
    if self.index < len(self.return_values):
      ret, revision = self.return_values[self.index]
      get_revisions().discard()
      get_revisions().set_rev(revision)
      return ret
    else:
      i = self.index - len(self.return_values)
      exc_type, exc_value, traceback, revision = self.exceptions[i]
      get_revisions().discard()
      get_revisions().set_rev(revision)
      raise exc_type, exc_value, traceback
  def goto_next(self):
    self.index += 1
  def dump_return_values(self, target = None):
    if target is None:
      import sys
      target = sys.stderr
    if not self.return_values:
      print >> target, 'No return values'
    else:
      print >> target, 'Returns:'
      for x, rev in self.return_values:
        print >> target, '  ', repr(x)
  def dump_exceptions(self, target = None):
    if target is None:
      import sys
      target = sys.stderr
    if not self.exceptions:
      print >> target, 'No exceptions'
    else:
      print >> target, 'Exception:'
      first = True
      for exc_type, exc_value, tb, rev in self.exceptions:
        if first:
          first = False
        else:
          print >> target, '==========================================='
        import traceback
        traceback.print_exception(exc_type, exc_value, tb)
  def dump(self, target = None):
    if target is None:
      import sys
      target = sys.stderr
    self.dump_return_values(target)
    print >> target, '==========================================='
    self.dump_exceptions(target)

def TracedFunction(func):
  def traced_func_call(*args, **kargs):
    cur_frame = get_revisions().traced_frame
    assert cur_frame, 'Root frame is not set'
    if cur_frame.has_more_decisions():
      return cur_frame.get_next_call_decision()
    frame = TracedFrame(cur_frame)
    rev = get_revisions().cur_rev
    while frame.next_path():
      with frame:
        get_revisions().set_rev(rev)
        frame.result.add_return_value(func(*args, **kargs))

    cur_frame.add_decision(frame.result)
    return cur_frame.get_next_call_decision()
  return traced_func_call
