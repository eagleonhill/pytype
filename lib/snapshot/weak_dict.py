from weakref import WeakKeyDictionary, WeakValueDictionary, ref
from sdict import SDict
from ..checker import notify_update
from base import Immutable

class IDedRef(ref):
  def __init__(self, obj, callback):
    super(IDedRef, self).__init__(obj, callback)
    self.id = id(obj)

class SIDWeakKeyDictionary(WeakKeyDictionary):
  def __init__(self, dict=None):
    self.data = SDict()
    def remove(k, selfref=ref(self)):
      self = selfref()
      if self is not None:
        del self.data[k.id]
    self._remove = remove
    if dict is not None: self.update(dict)

  def __delitem__(self, key):
    del self.data[id(key)]

  def __getitem__(self, key):
    return self.data[id(key)][1]

  def __repr__(self):
    return "<WeakKeyDictionary at %s>" % id(self)

  def __setitem__(self, key, value):
    self.data[id(key)] = IDedRef(key, self._remove), value

  def copy(self):
    new = WeakKeyDictionary()
    for key, value in self.data.values():
      o = key()
      if o is not None:
        new[o] = value
    return new

  __copy__ = copy

  def __deepcopy__(self, memo):
    from copy import deepcopy
    new = self.__class__()
    for key, value in self.data.items():
      o = key()
      if o is not None:
        new[o] = deepcopy(value, memo)
    return new

  def get(self, key, default=None):
    return self.data.get(id(key),(None, default))[1]

  def has_key(self, key):
    return id(key) in self.data

  def __contains__(self, key):
    return id(key) in self.data

  def items(self):
    L = []
    for key, value in self.data.values():
      o = key()
      if o is not None:
        L.append((o, value))
    return L

  def iteritems(self):
    for wr, value in self.data.itervalues():
      key = wr()
      if key is not None:
        yield key, value

  def iterkeys(self):
    for wr, value in self.data.itervalues():
      obj = wr()
      if obj is not None:
        yield obj

  def __iter__(self):
    return self.iterkeys()

  def itervalues(self):
    for wr, value in self.data.itervalues():
      obj = wr()
      if obj is not None:
        yield value

  def keys(self):
    L = []
    for wr, value in self.data.values():
      o = wr()
      if o is not None:
        L.append(o)
    return L

  def popitem(self):
    while 1:
      key, value = self.data.popitem()
      key, value = value
      o = key()
      if o is not None:
        return o, value

  def pop(self, key, *args):
    if id(key) in self.data:
      return self.data.pop(id(key))[1]
    return self.data.pop(id(key), *args)

  def setdefault(self, key, default=None):
    if not key in self:
      self[key] = default
    return self[key]

  def update(self, dict=None, **kwargs):
    d = self.data
    if dict is not None:
      if not hasattr(dict, "items"):
        dict = type({})(dict)
      for key, value in dict.items():
        d[id(key)] = IDedRef(key, self._remove), value
    if len(kwargs):
      self.update(kwargs)

class SWeakKeyDictionary(WeakKeyDictionary):
  def __init__(self, dict=None):
    WeakKeyDictionary.__init__(self, dict)
    self.data = SDict(self.data)

class SWeakValueDictionary(WeakValueDictionary):
  def __init__(self, dict=None):
    WeakValueDictionary.__init__(self, dict)
    self.data = SDict(self.data)

# Only have attribute data, should remain constant
Immutable.register(SIDWeakKeyDictionary)
Immutable.register(SWeakKeyDictionary)
Immutable.register(SWeakValueDictionary)
