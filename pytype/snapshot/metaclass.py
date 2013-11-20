from types import ClassType, InstanceType
from ..checker import notify_update, attr_error, raise_checker_error
from .base import Snapshotable, restore_as_dict, create_object

def validate(defs):
  if '__make__' in defs:
    assert '__restore__' in defs
    assert '__makefits__' in defs

class SnapshotableMetaClass(type):
  __defining_baseobject = True
  def __new__(cls, name, bases, defs):
    defs.setdefault('_SnapshotableMetaClass__builtin', False)
    if not SnapshotableMetaClass.__defining_baseobject:
      if BaseObject not in bases:
        bases = bases + (BaseObject, )
    else:
      SnapshotableMetaClass.__defining_baseobject = False
    validate(defs)
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
    x = create_object(BaseObject, cls)
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

  def __makefits__(self, other, context):
    td, sd = self.__make__(), context.get_data(other)
    if td is None or sd is None:
      context.fail()
    if td.keys() != sd.keys():
      context.fail()
    for x in td:
      context.fit(td[x], sd[x])

BaseObject._pytype_make_internal_type()

Snapshotable.register(BaseObject)
 
__all__ = ['BaseObject', 'SnapshotableMetaClass']
