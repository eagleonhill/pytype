from threading import local
from weakref import WeakValueDictionary
from revision import Revision
from ..snapshot import Immutable, Snapshotable

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
    self.traced_frame = None
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
    while True:
      try:
        key, obj = self.changed_objs.popitem()
      except KeyError:
        break
      new_rev.take_snapshot(obj)
      #print obj.__class__, 'commited'
    self.cur_rev = new_rev
    self.commiting = False
    #print 'Commit to', new_rev
    return new_rev

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

  def set_rev(self, rev):
    if self.cur_rev == rev:
      return
    #print 'Setting rev to', rev
    lcp = self.lcp(rev, self.cur_rev)
    while self.cur_rev != lcp:
      self.pop()
    self.push_to_rev(rev)

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

