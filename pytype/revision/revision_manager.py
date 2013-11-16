from threading import local
import sys
from weakref import WeakValueDictionary
from revision import Revision
from ..snapshot import Immutable, Snapshotable
from ..checker import get_program_frame

class RevisionManager(object):
  class ReplayLock(object):
    __slots__ = 'count'
    def __init__(self, rm):
      self.count = 0
    def __enter__(self):
      self.count += 1
    def __exit__(self, exc_type, exc_value, traceback):
      self.count -= 1
    def __nonzero__(self):
      return self.count > 0

  def __init__(self):
    self.rev_id = -1
    self.root = Revision(None, self)
    self.cur_rev = self.root
    self.changed_objs = WeakValueDictionary()
    self.replay_lock = RevisionManager.ReplayLock(self)
    self.commiting = False

  def get_rev_id(self):
    self.rev_id += 1
    return self.rev_id

  def commit(self):
    from revision import Revision
    self.commiting = True
    new_rev = Revision(self.cur_rev, self)
    while self.changed_objs:
      try:
        key, obj = self.changed_objs.popitem()
      except KeyError: # Key may be deleted while popping
        break
      new_rev.take_snapshot(obj)
      #print obj.__class__, 'commited'
    #print 'Commit from', self.cur_rev, 'to', new_rev
    self.cur_rev = new_rev
    self.commiting = False
    return new_rev
  def commit_local(self):
    rev = self.commit()
    f = get_program_frame()
    rev.local = dict(f.f_locals)
    rev.code = f.f_code
    return rev

  def pop(self):
    self.cur_rev.rollback()
    self.cur_rev = self.cur_rev.back

  @staticmethod
  def lcp(rev1, rev2):
    s1 = set((rev1, ))
    s2 = set((rev2, ))
    while not s1 & s2 and (rev1 or rev2):
      if rev1:
        rev1 = rev1.back
        s1.add(rev1)
      if rev2:
        rev2 = rev2.back
        s2.add(rev2)
    cp = s1 & s2
    assert len(cp) <= 1, 'Found more than one lcp'
    assert cp, 'Cannot find LCP'
    return cp.pop()

  def set_rev(self, rev, setlocal = False):
    if self.cur_rev != rev:
      #print 'Setting rev to', rev
      lcp = self.lcp(rev, self.cur_rev)
      while self.cur_rev != lcp:
        self.pop()
      self.push_to_rev(rev)
    if setlocal:
      f = get_program_frame()
      assert rev.local is not None
      assert f.f_code is rev.code
      LocalLoader(f, rev).setup()

  def set_local(self, rev):
    self.set_rev(rev, True)

  def push_to_rev(self, rev):
    if rev is None:
      raise ValueError, "rev could't be None"
    if self.cur_rev == rev:
      return
    self.push_to_rev(rev.back)
    rev.replay()
    self.cur_rev = rev

  def notify_update(self, obj):
    assert not isinstance(obj, Immutable)
    assert not self.commiting
    if not self.replay_lock:
      self.changed_objs[id(obj)] = obj

  def discard(self):
    """Discard all uncommited changes"""
    if not self.is_clean:
      #print 'Discarding all changes'
      rev = self.commit()
      self.pop()

  @property
  def is_clean(self):
    return not self.changed_objs

_rev = local()
def get_revisions():
  if not hasattr(_rev, 'rm'):
    _rev.rm = RevisionManager()
  return _rev.rm

class LocalLoader(object):
  @staticmethod
  def defaultTrace(f, event, arg):
    return None
  def __init__(self, frame, rev):
    self.rev = rev
    self.local = rev.local
    self.frame = frame
  def setup(self):
    self.old_ftrace = self.frame.f_trace
    self.set = False
    self.frame.f_trace = self
  def __call__(self, f, event, arg):
    if event == 'call':
      assert False
      return self.old_trace(f, event, arg) if self.old_trace else None
    assert f == self.frame
    if self.set:
      return
    backup = {}
    d = f.f_locals
    for name in d:
      if name.startswith('__pytype'):
        backup[name] = d[name]
    before = [x for x in d.keys() if not x.startswith('_')]
    d.clear()
    d.update(backup)
    d.update(self.local)
    end = [x for x in d.keys() if not x.startswith('_')]
    #print self.rev, before, end
    self.set = True
    if self.old_ftrace:
      ret = self.old_ftrace(f, event, arg)
    else:
      ret = self.old_ftrace
    return ret
sys.settrace(LocalLoader.defaultTrace)
