from types import ClassType, InstanceType
from ..checker import notify_update, attr_error, raise_checker_error
from base import Snapshotable, restore_as_dict

class SnapshotableMetaClass(type):
  __defining_baseobject = True
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
        notify_update(self)
        f(self, key, value)
      defs['__setattr__'] = __setattr__
    else:
      def __setattr__(self, key, value):
        notify_update(self)
        self.__dict__[key] = value
      defs['__setattr__'] = __setattr__
    # Track when attribute is removed
    d = SnapshotableMetaClass.find_method('__delattr__', bases, defs)
    if d is not None:
      def __delattr__(self, key):
        notify_update(self)
        d(self, key)
      defs['__delattr__'] = __delattr__
    else:
      def __delattr__(self, key):
        notify_update(self)
        try:
          del self.__dict__[key]
        except KeyError:
          attr_error(self, key)
      defs['__delattr__'] = __delattr__

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
    defs.setdefault('_SnapshotableMetaClass__builtin', False)
    if not SnapshotableMetaClass.__defining_baseobject:
      if BaseObject not in bases:
        bases = bases + (BaseObject, )
    else:
      SnapshotableMetaClass.__defining_baseobject = False
    t = super(SnapshotableMetaClass, cls).__new__(cls, name, bases, defs)
    return t

  def __setattr__(self, name, value):
    if self.__builtin:
      raise_checker_error(TypeError, \
          "can't set attributes of built-in/extension type %s" %\
          self.__name__)
    super(SnapshotableMetaClass, self).__setattr__(name, value)

  def _pytype_make_internal_type(self):
    self.__builtin = True

class BaseObject(object):
  __metaclass__ = SnapshotableMetaClass
  def __new__(cls, *args, **kwds):
    x = super(BaseObject, cls).__new__(cls, *args, **kwds)
    notify_update(x)
    return x
  def __setattr__(self, key, value):
    notify_update(self)
    super(BaseObject, self).__setattr__(key, value)
  def __delattr__(self, key):
    notify_update(self)
    super(BaseObject, self).__delattr__(key)
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

BaseObject._pytype_make_internal_type()

Snapshotable.register(BaseObject)
