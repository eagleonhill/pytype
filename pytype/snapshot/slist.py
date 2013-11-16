from UserList import UserList
from .base import Snapshotable
from ..checker import notify_update

class SList(UserList, Snapshotable):
  def __make__(self):
    return list(self.data)
  def __restore__(self, value, oldvalue = None):
    self.data = value

  def __init__(self, initlist=None):
    notify_update(self)
    UserList.__init__(self, initlist)

  def __setitem__(self, i, item):
    notify_update(self)
    UserList.__setitem__(self, i, item)

  def __delitem__(self, i):
    notify_update(self)
    UserList.__delitem__(self, i)

  def __setslice__(self, i, j, other):
    notify_update(self)
    UserList.__setslice__(self, i, j, other)

  def __delslice__(self, i, j):
    notify_update(self)
    UserList.__delslice__(self, i, j)

  def __iadd__(self, other):
    notify_update(self)
    return UserList.__iadd__(self, other)

  def __imul__(self, other):
    notify_update(self)
    return UserList.__imul__(self, other)
  def append(self, item): notify_update(self);self.data.append(item)
  def insert(self, i, item): notify_update(self);self.data.insert(i, item)
  def pop(self, i=-1): notify_update(self);return self.data.pop(i)
  def remove(self, item): notify_update(self);self.data.remove(item)
  def reverse(self): notify_update(self);self.data.reverse()
  def sort(self, *args, **kwds): notify_update(self);self.data.sort(*args, **kwds)
  def extend(self, other):
    notify_update(self)
    UserList.extend(self, other)
  def __makefits__(self, other):
    from ..makefits import FittingFailedException,\
        type_make_fit_internal
    if len(self) != len(other):
      raise FittingFailedException
    for a, b in zip(self.data, other.data):
      type_make_fit_internal(a, b)
