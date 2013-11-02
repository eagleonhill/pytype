from types import ClassType
from ..checker import notify_update
from base import Snapshotable, restore_as_dict

class SnapshotableMetaClass(type):
  def __new__(cls, name, bases, defs):
    if any(map(lambda x: isinstance(SnapshotableMetaClass, x), bases)):
      # BaseObject is a base type
      t = super(SnapshotableMetaClass, cls).__new__(name, bases, defs)
      assert issubclass(t, BaseObject)
    else:
      f = defs.get('__setattr__')
      if f is None:
        for base in bases:
          if hasattr(base, '__setattr__'):
            f = base.__setattr__
      if f is not None:
        # That's inefficient to track if __dict__ is changed in user-defined
        # __setattr__, so always trigger notify_update
        f = t.__setattr__
        def __setattr__(self, key, value):
          f(self, key, value)
          notify_update(self)
        defs['__setattr__'] = __setattr__
      else:
        def __setattr__(self, key, value):
          self.__dict__[key] = value
          notify_update(self)
        defs['__setattr__'] = __setattr__
      t = ClassType(name, bases, defs)
    return t
  def __call__(self, *args, **kargs):
    """Constructor, track new created object"""
    ret = super(SnapshotableMetaClass, self).__call__(*args, **kargs)
    notify_update(ret)
    return ret

class BaseObject(Snapshotable):
  def __setattr__(self, key, value):
    notify_update(self)
    super(BaseObject, self).__setattr__(key, value)
  def __new__(cls, *args, **kwds):
    x = super(BaseObject, cls).__new__(*args, **kwds)
    notify_update(x)
    return x
  def __make__(self):
    if hasattr(self, '__slots__'):
      slots = self.__slots__
      if isinstance(slots, basestring):
        slots = (slots, )
      cur = {}
      for key in slots:
        if hasattr(self, key):
          cur[key] = getattr(self, key)
    else:
      cur = self.__dict__
    return dict(cur)

  def __restore__(self, value, cur):
    restore_as_dict(self, value, cur)
