from ..traced_frame import DecisionSet, TracedFrame
from ..checker import get_program_frame, get_revision_manager

class FrameInfo(object):
  identifier = '__pytype_frame_info'
  def __init__(self, frame):
    self.block_frames = {}
    self.frame = frame
  @classmethod
  def get_frameinfo(cls, frame):
    l = frame.f_locals
    if cls.identifier in l:
      return l[cls.identifier]
    v = cls(frame)
    l[cls.identifier] = v
    return v
  def get_block(self, bid, init = None):
    if bid in self.block_frames:
      return self.block_frames[bid]
    assert init, 'Block not found'
    v = init()
    self.block_frames[bid] = v
    return v
  def clear_block(self, bid):
    del self.block_frames[bid]

class BlockDecision(DecisionSet):
  def __init__(self):
    self.result = []
    self.index = 0
  def on_finish(self):
    self.finish()
  def finish(self):
    rev = self.get_rev()
    #print 'finish block', rev
    self.result.append((None, None, None, rev))
  def on_exception(self, exc_type, exc_value, traceback):
    revision = self.get_rev()
    self.result.append((exc_type, exc_value, traceback, revision))
    return True
  def get_rev(self):
    return get_revision_manager().commit_local()
  def has_next(self):
    return self.index + 1 < len(self.result)
  def goto_next(self):
    self.index += 1
  def current(self):
    exc_type, exc_value, traceback, revision = self.result[self.index]
    get_revision_manager().discard()
    #print 'set local', revision
    get_revision_manager().set_local(revision)
    if exc_type:
      raise exc_type, exc_value, traceback

def block_done(bid):
  cur = TracedFrame.current()
  if cur.has_more_decisions():
    #print 'block_done'
    cur.get_next_decision(BlockDecision)
    return True

def do_block(bid):
  if block_done(bid):
    return False
  def init():
    t = TracedFrame(BlockDecision())
    t.start_rev = get_revision_manager().commit_local()
    #print 'commiting', t.start_rev
    return t
  pf = get_program_frame()
  fi = FrameInfo.get_frameinfo(pf)
  f = fi.get_block(bid, init)
  if f.next_path():
    #print 'next_path', f.start_rev
    get_revision_manager().set_local(f.start_rev)
    return True
  else:
    fi.clear_block(bid)
    assert block_done(bid)
    return False

def frame(bid):
  pf = get_program_frame()
  fi = FrameInfo.get_frameinfo(pf)
  return fi.get_block(bid)