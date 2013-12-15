import random
from itertools import chain
from ..traced_frame import DecisionSet, TracedFrame
from ..checker import get_program_frame, get_revision_manager,\
    raise_checker_error, reraise_error
from .block import *
from ..makefits import FittingContext

LOOP_MERGE = [
    (0, 0, 0),
    (3, 8, FittingContext.FITS_BUILTIN_VALUE),
    (5, 13, FittingContext.FITS_BUILTIN_VALUE | FittingContext.FITS_LIST),
    (7, 23, FittingContext.FITS_ALL),
]

class LoopFrame(TracedFrame):
  def __init__(self, result=None):
    super(LoopFrame, self).__init__(result)
    self.starts_old = []
    self.starts_new = []
    self.cur_start = None
    self.merge_level = 0
  def add_start_state(self, state):
    if self.cur_start is None:
      state.loop = 0
    else:
      state.loop = self.cur_start.loop + 1
    self.update_merge_level(state.loop, len(self.starts_old) +\
        len(self.starts_new))
    # Find exact same revs
    for s in reversed(self.starts_old):
      c = FittingContext(0)# LOOP_MERGE[self.merge_level][2])
      newrev = c.try_fit_local_rev(state.rev, s.rev)
      if newrev:
        return
    if self.merge_level != 0:
      # Update current rev with previous ones
      for s in self.starts_old:
        c2 = FittingContext(LOOP_MERGE[self.merge_level][2])
        newrev = c2.try_fit_local_rev(state.rev, s.rev)
        if newrev:
          state.rev = newrev
    new = []
    for s in self.starts_new:
      # If an uncomputed rev can fits current one, ignore it.
      c = FittingContext(LOOP_MERGE[self.merge_level][2])
      newrev = c.try_fit_local_rev(state.rev, s.rev)
      if newrev:
        state.rev = newrev
      else:
        new.append(s)
    self.starts_new[:] = new
    self.starts_new.append(state)

  def update_merge_level(self, loop, states):
    while self.merge_level + 1 < len(LOOP_MERGE):
      if loop >= LOOP_MERGE[self.merge_level + 1][0] or\
          states >= LOOP_MERGE[self.merge_level + 1][1]:
        self.merge_level += 1
      else:
        break

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
    self.starts_old.append(self.cur_start)
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
    self.key = None
  def on_exception(self, exc_type, exc_value, traceback):
    if exc_type is LoopFinished:
      if self.key is not None:
        pf = get_program_frame()
        del pf.f_locals[self.key]
      self.finish()
      return True
    else:
      return super(LoopDecision, self).on_exception(
          exc_type, exc_value, traceback)
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
  cur = TracedFrame.current()
  if cur.has_more_decisions():
    it = itergen().__iter__()
    cur.get_next_decision(BlockDecision)
    return False

  def init():
    from ..snapshot import Snapshotable, SGen
    t = LoopFrame(LoopDecision())
    t.bid = bid
    it = itergen().__iter__()
    if not isinstance(it, Snapshotable):
      it = SGen(it)
    t.result.iterator = it
    key = '__pytype__%dit%derator' %(bid, random.randint(1, 100000))
    t.result.key = key
    # Make a reference to iterator on stack, so fitting locals with fit 
    # the iterator.
    pf.f_locals[key] = it
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

