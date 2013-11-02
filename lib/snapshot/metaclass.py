from types import ClassType, InstanceType
from ..checker import notify_update
from base import Snapshotable, restore_as_dict

class SnapshotableMetaClass(type):
  @staticmethod
  def find_method(name, bases, defs):
    f = defs.get(name)
    if f is None:
      for base in bases:
        if hasattr(base, name):
          f = getattr(base, name)
          if f is not None:
            break
    return f

  @staticmethod
  def update_classobj(name, bases, defs):
    f = SnapshotableMetaClass.find_method('__setattr__', bases, defs)
    if f is not None:
      # That's inefficient to track if __dict__ is changed in user-defined
      # __setattr__, so always trigger notify_update
      def __setattr__(self, key, value):
        f(self, key, value)
        notify_update(self)
      defs['__setattr__'] = __setattr__
    else:
      def __setattr__(self, key, value):
        self.__dict__[key] = value
        notify_update(self)
      defs['__setattr__'] = __setattr__

    init = SnapshotableMetaClass.find_method('__init__', bases, defs)
    # Track when instance is created, add it before any __init__ calls
    if init is not None:
      def __init__(self, *args, **kwds):
        notify_update(self)
        return init(self, *args, **kwds)
      defs['__init__'] = __init__
    else:
      def __init__(self, *args, **kwds):
        notify_update(self)
      defs['__init__'] = __init__

  def __new__(cls, name, bases, defs):
    if any(map(lambda x: isinstance(SnapshotableMetaClass, x), bases)):
      # BaseObject is a base type
      t = super(SnapshotableMetaClass, cls).__new__(name, bases, defs)
      assert issubclass(t, BaseObject)
    else:
      cls.update_classobj(name, bases, defs)
      t = ClassType(name, bases, defs)
    return t

class BaseObject(Snapshotable):
  def __new__(cls, *args, **kwds):
    x = super(BaseObject, cls).__new__(cls, *args, **kwds)
    notify_update(x)
    return x
  def __setattr__(self, key, value):
    notify_update(self)
    super(BaseObject, self).__setattr__(key, value)
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
