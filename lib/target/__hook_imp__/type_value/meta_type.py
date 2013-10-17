"""
Every single object have different type.
Base type for generic types including list, set, dict, tuple
"""

from base import *

def getMeta(x):
  return x

class MetaType(TypeValue):
  def __new__(cls, name, base, defs):
    #defs['__new__'] = cls.patch_new(defs.get('__new__', None))
    return super(MetaType, cls).__new__(cls, name, base, defs)

  @classmethod
  def patch_new(c, orig):
    def create(cls, *args, **kargs):
      if orig:
        v = orig(cls, *args, **kargs)
      else:
        v = super(cls, cls).__new__(cls, *args, **kargs)
      v.__init__(*args, **kargs)
      return MetaTypeValue(v)
    return create
  #def __instancecheck__(self, instance):
    #raise NotImplementedError()

class MetaTypeValue:
  __slots__ = ['__meta']
  def __init__(self, meta):
    self.__meta = meta
  def __getattr__(self, name):
    print name
    return getattr(self.__meta, name)
  def __setattr__(self, name, value):
    if name != '_MetaTypeValue__meta':
      setattr(self.__meta, name, value)
    else:
      self.__dict__[name] = value

