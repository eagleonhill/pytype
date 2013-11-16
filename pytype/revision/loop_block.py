from ..traced_frame import DecisionSet, TracedFrame
from ..checker import get_program_frame, get_revision_manager,\
    raise_checker_error, reraise_error
from .block import *

class LoopFrame(TracedFrame):
  def __init__(self, result=None):
    super(LoopFrame, self).__init__(result)
    self.starts = []
    self.starts_new = []
    self.cur_start = None
  def add_start_state(self, state):
    self.starts.append(state)
    self.starts_new.append(state)
    if self.cur_start is None:
      state.loop = 0
    else:
      state.loop = self.cur_start.loop + 1

  def next_path(self):
    while self.cur_start is None or not super(LoopFrame, self).next_path():
      if len(self.starts_new) == 0:
        self.finish()
        return False
      self.next_start()
    return True
  def on_finish(self):
    pass

  def next_start(self):
    sid = min(range(len(self.starts_new)),\
        key=lambda x: self.starts_new[x].loop)
    self.cur_start = self.starts_new.pop(sid)
    self.reset()

class LoopState(object):
  def __init__(self, rev):
    self.rev = rev
    self.loop = 0

class LoopFinished(Exception):
  pass

class LoopDecision(BlockDecision):
  def __init__(self):
    super(LoopDecision, self).__init__()
    self.need_new_state = True
  def on_exception(self, exc_type, exc_value, traceback):
    if exc_type is LoopFinished:
      self.finish()
      return True
    else:
      return super(LoopDecision, self).on_exception(exc_type, exc_value, traceback)
  def on_finish(self):
    self.need_new_state = True

def do_while(bid):
  if block_done(bid):
    return False
  def init():
    t = LoopFrame(LoopDecision())
    return t
  pf = get_program_frame()
  fi = FrameInfo.get_frameinfo(pf)
  f = fi.get_block(bid, init)
  if f.result.need_new_state:
    f.add_start_state(LoopState(get_revision_manager().commit_local()))
    f.result.need_new_state = False
  if f.next_path():
    get_revision_manager().set_local(f.cur_start.rev)
    return True
  else:
    fi.clear_block(bid)
    assert block_done(bid)
    return False

def do_for(bid, itergen):
  if block_done(bid):
    return False
  def init():
    from ..snapshot import Snapshotable, SGen
    t = LoopFrame(LoopDecision())
    it = itergen().__iter__()
    if not isinstance(it, Snapshotable):
      it = SGen(it)
    t.result.iterator = it
    return t
  pf = get_program_frame()
  fi = FrameInfo.get_frameinfo(pf)
  f = fi.get_block(bid, init)
  if f.result.need_new_state:
    f.add_start_state(LoopState(get_revision_manager().commit_local()))
    f.result.need_new_state = False
  if f.next_path():
    #print 'start', f.cur_start.loop, f.cur_start.rev
    get_revision_manager().set_local(f.cur_start.rev)
    return True
  else:
    fi.clear_block(bid)
    assert block_done(bid)
    return False

def for_next(bid):
  pf = get_program_frame()
  fi = FrameInfo.get_frameinfo(pf)
  f = fi.get_block(bid)
  return f.result.iterator.next()

def loop_break():
  raise_checker_error(LoopFinished)

