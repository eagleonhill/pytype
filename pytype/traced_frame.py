from . import checker
from .checker import raise_checker_error, get_revision_manager
from threading import local
from functools import wraps

class TracedFrame(object):
  """
  A function call frame which records all possible return values and errors
  that may be raised, and maintain all undetermined decisions during
  evaluations."""
  _frame_local = local()
  _frame_local.current = None
  @staticmethod
  def current(canbeempty = False):
    c = TracedFrame._frame_local.current
    if not canbeempty:
      assert c, 'Top frame is not set'
    return c

  @staticmethod
  def set_current(value):
    TracedFrame._frame_local.current = value
  def __init__(self, result = None, topmost=False):
    self.decision_list = None
    self.decision_made = 0
    self.result = result
    self.back = self.current(topmost)
    if topmost:
      assert self.back is None
  def __enter__(self):
    assert self.current(True) == self.back
    self.running = True
    self.set_current(self)
  def __exit__(self, exc_type, exc_value, traceback):
    self.set_current(self.back)
    self.running = False
    return self.onexit(exc_type, exc_value, traceback)
  def onexit(self, exc_type, exc_value, traceback):
    if exc_type is TracedFrame.DuplicatedPathError:
      return True
    elif exc_type is TracedFrame.ImpossiblePathError:
      return True
    elif exc_type:
      if checker.is_internal_error(exc_type, exc_value, traceback):
        return False
      if self.result:
        return self.result.on_exception(exc_type, exc_value, traceback)
      else:
        return False
    elif self.result:
      self.result.on_finish()
  def next_path(self):
    self.decision_made = 0
    if self.decision_list is None:
      self.decision_list = []
      return True
    while len(self.decision_list) and\
        not self.decision_list[-1].has_next():
      self.decision_list.pop()
    if self.decision_list:
      self.decision_list[-1].goto_next()
      return True
    else:
      self.on_finish()
      return False
  def reset(self):
    self.decision_list = None
    self.decision_made = 0
  def on_finish(self):
    self.finish()
  def finish(self):
    if self.back and self.result:
      self.back.add_decision(self.result)
  def get_next_decision(self, typecheck = None):
    assert self.has_more_decisions()
    d = self.pop_decision()
    if typecheck is not None:
      assert isinstance(d, typecheck)
    return d.current()
  def get_next_bool_decision(self):
    if not self.has_more_decisions():
      rev = get_revision_manager().commit()
      self.add_decision(BooleanDecision(rev))
    return self.get_next_decision(BooleanDecision)
  def get_next_call_decision(self):
    return self.get_next_decision(FunctionDecision)
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

class ReturnValue(Exception):
  def __init__(self, value):
    self.value = value

def return_value(value):
  raise_checker_error(ReturnValue, value)

class DecisionSet(object):
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
  def __init__(self, rev):
    self.value = False
    self.rev = rev
  def has_next(self):
    return self.value == False
  def goto_next(self):
    self.value = True
  def current(self):
    get_revision_manager().set_rev(self.rev)
    return self.value

class FunctionDecision(DecisionSet):
  def __init__(self, sideeffect = True):
    self.return_values = []
    self.exceptions = []
    self.sideeffect = sideeffect
    if self.sideeffect:
      self.start_revision = get_revision_manager().commit()
    self.index = 0
  @classmethod
  def from_values(cls, values):
    self = cls(sideeffect = False)
    for v in values:
      self.add_return_value(v)
    return self
  def clone(self):
    other = FunctionDecision()
    other.return_values = self.return_values
    other.exceptions = self.exceptions
    other.sideeffect = self.sideeffect
    other.index = 0
    return other
  def on_finish(self):
    """ revision will be added when adding return value"""
    pass
  def on_exception(self, exc_type, exc_value, traceback):
    if exc_type is ReturnValue:
      self.add_return_value(exc_value.value)
      return True
    revision = self.get_rev()
    self.exceptions.append((exc_type, exc_value, traceback, revision))
    return True
  def add_return_value(self, value):
    revision = self.get_rev()
    self.return_values.append((value, revision))
  def has_next(self):
    return self.index + 1 < len(self.return_values) + len(self.exceptions)
  def current(self):
    if self.index < len(self.return_values):
      ret, revision = self.return_values[self.index]
      self.set_rev(revision)
      return ret
    else:
      i = self.index - len(self.return_values)
      exc_type, exc_value, traceback, revision = self.exceptions[i]
      self.set_rev(revision)
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
  def dump_exceptions(self, target = None, hide_internal=False):
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
        target.write(''.join(
            checker.format_traceback(tb, hide_internal) + \
            traceback.format_exception_only(exc_type, exc_value)))
  def dump(self, target = None):
    if target is None:
      import sys
      target = sys.stderr
    self.dump_return_values(target)
    print >> target, '==========================================='
    self.dump_exceptions(target)

  def get_rev(self):
    if self.sideeffect:
      return get_revision_manager().commit()
    else:
      return None
  def set_rev(self, revision):
    if self.sideeffect:
      get_revision_manager().set_rev(revision)

def TracedFunction(func):
  @wraps(func)
  def traced_func_call(*args, **kargs):
    cur_frame = TracedFrame.current()
    assert cur_frame, 'Root frame is not set'
    if cur_frame.has_more_decisions():
      return cur_frame.get_next_call_decision()
    frame = TracedFrame(FunctionDecision())
    rev = get_revision_manager().commit()
    while frame.next_path():
      with frame:
        get_revision_manager().set_rev(rev)
        frame.result.add_return_value(func(*args, **kargs))

    return cur_frame.get_next_call_decision()
  return traced_func_call
