from weakref import WeakKeyDictionary, WeakValueDictionary
from sdict import SDict
from ..checker import notify_update
from base import Immutable

class SWeakKeyDictionary(WeakKeyDictionary):
  def __init__(self, dict=None):
    WeakKeyDictionary.__init__(self, dict)
    self.data = SDict(self.data)

# Only have attribute data, should remain constant
Immutable.register(SWeakKeyDictionary)

class SWeakValueDictionary(WeakValueDictionary):
  def __init__(self, dict=None):
    WeakValueDictionary.__init__(self, dict)
    self.data = SDict(self.data)

Immutable.register(SWeakValueDictionary)
