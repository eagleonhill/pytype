from ..traced_frame import DecisionSet, TracedFrame
from ..checker import get_program_frame, get_revision_manager

blockprefix = '__pytype_block'
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

def get_frame(bid, default = None):
  pf = get_program_frame()
  identifier = blockprefix + str(bid)
  if default is None:
    return pf.f_locals[identifier]
  frame = pf.f_locals.get(identifier, None)
  if frame is None:
    frame = default()
    pf.f_locals[identifier] = frame
  return frame

def clear_frame(bid):
  pf = get_program_frame()
  identifier = blockprefix + str(bid)
  del pf.f_locals[identifier]

def do_block(bid):
  if block_done(bid):
    return False
  def init():
    t = TracedFrame(BlockDecision())
    t.start_rev = get_revision_manager().commit_local()
    #print 'commiting', t.start_rev
    return t
  f = get_frame(bid, init)
  if f.next_path():
    #print 'next_path', f.start_rev
    get_revision_manager().set_local(f.start_rev)
    return True
  else:
    clear_frame(bid)
    assert block_done(bid)
    return False

def frame(bid):
  pf = get_program_frame()
  return get_frame(bid)
