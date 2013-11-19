from UserDict import UserDict
from .base import Snapshotable
from ..checker import notify_update

class SDict(UserDict, Snapshotable):
  def __make__(self):
    return dict(self.data)
  def __restore__(self, value, oldvalue = None):
    self.data = dict(value)

  def __init__(self, initlist=None):
    notify_update(self)
    UserDict.__init__(self, initlist)

  def __setitem__(self, i, item):
    notify_update(self)
    UserDict.__setitem__(self, i, item)

  def __delitem__(self, key):
    notify_update(self)
    UserDict.__delitem__(self, key)

  def update(self, dict=None, **kwargs):
    notify_update(self)
    UserDict.update(self, dict, **kwargs)

  def setdefault(self, key, failobj=None):
    notify_update(self)
    return UserDict.setdefault(self, key, failobj)

  def pop(self, key, **kwargs):
    notify_update(self)
    return UserDict.pop(self, key, **kwargs)

  def popitem(self):
    notify_update(self)
    return UserDict.popitem(self)

  def __makefits__(self, other, context):
    if type(other) is not type(self):
      context.fail()
    other = context.get_data(other)
    if set(self.keys()) != set(other.keys()):
      context.fail()
    for k in self.keys():
      context.fit(self[k], other[k])
