from ..snapshot import Snapshotable, restore_snapshot, make_snapshot
class Revision:
  """ A change set """
  def __init__(self, back, revision_manager = None):
    self.back = back
    if revision_manager is None:
      revision_manager = back.rm
    else:
      assert not back or revision_manager is back.rm
    self.rm = revision_manager
    self.frame_info = None
    self.objs = {}
    self.id = self.rm.get_rev_id()
  def take_snapshot(self, last_rev, obj):
    self.objs[id(obj)] = last_rev, obj, make_snapshot(obj)
  def replay_revision(self):
    #print 'Replaying', self
    assert self.rm.is_clean, "Uncommitted change"
    assert self.rm.cur_rev == self.back
    for rev, obj, value in self.objs.itervalues():
      self.replay(obj)
    self.rm.cur_rev = self
  def replay(self, obj = None):
    if obj is None:
      self.replay_revision()
      return
    rev, obj2, value = self.objs[id(obj)]
    assert obj2 is obj
    oldvalue = None
    if rev:
      oldrev, obj2, oldvalue = rev.objs[id(obj)]
      assert obj2 is obj
    with self.rm.replay_lock:
      restore_snapshot(obj, value, oldvalue)
  def rollback(self):
    for rev, obj, value in self.objs.itervalues():
      if rev is not None:
        rev.replay(obj)
      else:
        # The object is new created. It shouldn't be referenced after rollback
        pass

  def __str__(self):
    return '<revision %d>' % self.id
