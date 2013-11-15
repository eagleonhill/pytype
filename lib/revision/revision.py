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
    self.objs = {}
    self.local = None
    self.code = None
    self.id = self.rm.get_rev_id()
  def take_snapshot(self, obj):
    value = make_snapshot(obj)
    self.objs[id(obj)] = obj, value
    #print self, 'has', obj, value
  def replay_revision(self):
    #print 'Replaying', self
    assert self.rm.is_clean, "Uncommitted change"
    assert self.rm.cur_rev == self.back
    for obj, value in self.objs.itervalues():
      self.replay(obj, value=value)
    self.rm.cur_rev = self
  def replay(self, obj = None, curvalue = None, value=None):
    if obj is None:
      self.replay_revision()
      return
    if value is None:
      obj2, value = self.objs[id(obj)]
      assert obj2 is obj
    with self.rm.replay_lock:
      #print obj, 'revert from', curvalue, 'to', value
      restore_snapshot(obj, value, curvalue)
  def rollback(self):
    #print 'Rollback', self
    assert self.back, 'Cannot rollback root'
    for obj, value in self.objs.itervalues():
      if not self.back.__rollback_obj(obj, value):
        #print obj, 'not reverted from', self, value, self.back
        pass
  def __rollback_obj(self, obj, curvalue):
    rev = self
    while rev and not id(obj) in rev.objs:
      rev = rev.back
    if rev:
      rev.replay(obj, curvalue=curvalue)
      return True
    else:
      return False
  def __str__(self):
    return '<revision %d>' % self.id
