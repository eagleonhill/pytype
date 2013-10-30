
class RevisionManager:
  def __init__(self):
    self.root = Revision(None)
    self.cur_rev = self.root
    self.traced_frame = None
  def push_revision(self):
    """ Control flow fork or join point"""
    self.cur_rev = Revision(self.cur_rev)
  def set_rev(self, rev):
    self.cur_rev = rev
  current = None

def get_revisions():
  if RevisionManager.current is None:
    RevisionManager.current = RevisionManager()
  return RevisionManager.current

class Revision:
  """ A change set """
  def __init__(self, parent):
    self.parent = parent
    self.frame_info = None
    if parent is not None:
      parent.childs.append(self)
    self.childs = []
