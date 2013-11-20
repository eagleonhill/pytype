import sys
from abc import ABCMeta, abstractmethod
from .defs import *
from . import defs
from .hashable import Hash
from ..checker import raise_checker_error, reraise_error, fork, assume,\
    notify_update
from ..type_value import get_determined_value, is_determined
from ..snapshot import SDict, Snapshotable, Immutable, CollectionValue,\
    create_object
from ..makefits import try_fit_obj

notgiven = object()

class DictState(object):
  __metaclass__ = ABCMeta
  @abstractmethod
  def __setitem__(self, key, value):
    pass

  @abstractmethod
  def __getitem__(self, key):
    pass

  @abstractmethod
  def __delitem__(self, key):
    pass

  @abstractmethod
  def has_key(self, key):
    pass

  @abstractmethod
  def __len__(self):
    pass

  @abstractmethod
  def get(self, key, default):
    pass

  @abstractmethod
  def iteritems(self):
    pass

  @abstractmethod
  def itervalues(self):
    pass

  @abstractmethod
  def iterkeys(self):
    pass

  @abstractmethod
  def popitem(self):
    pass

  @abstractmethod
  def pop(key, default = notgiven):
    pass

  @abstractmethod
  def setdefault(key, default = None):
    pass

  @abstractmethod
  def update(self, other):
    pass
  
  @abstractmethod
  def __nonzero__(self):
    pass

  @abstractmethod
  def copy(self):
    pass

  @abstractmethod
  def __makefits__(self, other, context):
    pass

class DictUndeterminedState(DictState):
  def __init__(self, dict, iterable = None):
    self.data = CollectionValue()
    self.dict = dict
    self.maybeempty = False
    notify_update(self)
    if iterable:
      assert isinstance(iterable, DictDeterminedState)
      for key, v in iterable.iteritems():
        self[key] = v

  def onadd(self):
    if self.maybeempty:
      self.maybeempty = False
      notify_update(self)
  def ondel(self):
    if not self.maybeempty:
      self.maybeempty = True
      notify_update(self)

  def __setitem__(self, key, value):
    h = Hash(key)
    self.data.addvalue((key, value))
    self.onadd()

  def __getitem__(self, key):
    h = Hash(key)
    # Assume key always exist
    pair = self.data.deref()
    # TODO: Check if key is possible equal to pair[0]
    return pair[1]

  def __delitem__(self, key):
    h = Hash(key)
    # Assume key always exist
    self.ondel()

  def has_key(self, key):
    h = Hash(key)
    return fork()

  def __len__(self):
    v = IntType.create_undetermined()
    if self.maybeempty:
      assume(v >= IntType.create_from_value(0))
    else:
      assume(v > IntType.create_from_value(0))
    return v

  def get(self, key, default = None):
    if fork():
      return self[key]
    else:
      return default

  def iteritems(self):
    return self.data.iterator(self.maybeempty)

  def itervalues(self):
    # TODO
    raise NotImplementedError()

  def iterkeys(self):
    # TODO
    raise NotImplementedError()

  def popitem(self):
    self.ondel()
    return self.data.deref()

  def pop(self, key, default = notgiven):
    if default is not notgiven and fork():
      return default
    else:
      keyt, value = self.data.deref()
      assume(try_fit_obj(keyt, key, 0))
      return value

  def setdefault(self, key, default = None):
    h = Hash(key)
    self.onadd()
    self.data.addvalue((key, default))

  def update(self, other):
    if other._determined():
      for key, value in other.iteritems():
        self[key] = value
    else:
      if not other._state.maybeempty and self.maybeempty:
        self.maybeempty = False
        notify_update(self)
      for v in other._state.data.values:
        self.data.addvalue(v)

  def __nonzero__(self):
    if not self.maybeempty:
      return True
    else:
      if self.fork():
        self.dict._to_determined({})
        return False
      else:
        self.maybeempty = False
        notify_update(self)
        return True

  def copy(self, dict):
    new = DictUndeterminedState(dict)
    new.data = self.data.clone()
    new.maybeempty = self.maybeempty
    return new

  def __make__(self):
    return self.maybeempty
  def __restore__(self, value, curvalue = None):
    self.maybeempty = value
  def __makefits__(self, other, context):
    context.fit(self.data, other.data)
    d = context.get_data(other)
    if self.maybeempty != d:
      self.maybeempty = d
      notify_update(self)

  def __str__(self):
    return '{%sdict: %s}' % ('' if self.maybeempty else 'nonempty ', 
        str(self.data))

  def __repr__(self):
    return '{%sdict: %s}' % ('' if self.maybeempty else 'nonempty ', 
        repr(self.data))

class DictDeterminedState(DictState):
  def __init__(self, dict, iterable = None):
    self.data = SDict(iterable)
    self.dict = dict

  def __setitem__(self, key, value):
    h = Hash(key)
    if h.hash is None:
      self.dict._to_undetermined()
      self.dict[key] = value
    else:
      self.data[h] = value

  def __getitem__(self, key):
    h = Hash(key)
    if h.hash is None:
      # TODO: Remove duplicated/impossible items
      cur_frame = get_current_frame()
      if not cur_frame.has_more_decisions():
        d = FunctionDecision(sideeffect=False)
        for t in self.data.itervalues():
          d.add_return_value(t)
        cur_frame.add_decision(d)
      return cur_frame.get_next_decision(FunctionDecision)
    else:
      try:
        return self.data[h]
      except KeyError:
        err = sys.exc_info()
        missing = getattr(type(self.dict), '__missing__', None)
        if callable(missing):
          return missing(self.dict, key)
        raise_checker_error(*err)

  def __delitem__(self, key):
    h = Hash(key)
    if h.hash is None:
      self.dict._to_undetermined()
      del self.dict[key]
    else:
      try:
        del self.data[h]
      except KeyError:
        reraise_error()

  def has_key(self, key):
    h = Hash(key)
    if h.hash is None:
      return fork()
    else:
      return h in self.data

  def __len__(self):
    return IntType.create_from_value(len(self.data))

  def get(self, key, default = None):
    try:
      return self[key]
    except KeyError:
      return default

  def iteritems(self):
    for key, value in self.data.iteritems():
      yield key.value, value

  def itervalues(self):
    return self.data.itervalues()

  def iterkeys(self):
    for key in self.data.iterkeys():
      yield key.value

  def popitem(self):
    try:
      key, value = self.data.popitem()
      return key.value, value
    except KeyError:
      reraise_error()

  def pop(key, default = notgiven):
    h = Hash(key)
    if h.hash is None:
      self.dict._to_undetermined()
      return self.dict.pop(key, default)
    else:
      try:
        return self.data.pop(h)
      except KeyError:
        reraise_error()

  def setdefault(key, default = None):
    h = Hash(key)
    if h.hash is None:
      self.dict._to_undetermined()
      return self.dict.setdefault(key, default)
    else:
      return self.data.setdefault(h, default)

  def update(self, other):
    if other._determined():
      for key, value in other.iteritems():
        self[key] = value
    else:
      self.dict._to_undetermined()
      self.dict.update(other)

  def __nonzero__(self):
    return bool(self.data)

  def copy(self, dict):
    new = DictDeterminedState(dict)
    new.data = SDict(self.data)
    return new

  def __makefits__(self, other, context):
    context.fit(self.data, other.data)

  def __repr__(self):
    return repr(self.data)

  def __str__(self):
    return str(self.data)

def _dict_init_from_iterable():
  s = self
  while __hook_exports__.do_for(1, lambda: iterable):
    with __hook_exports__.frame(1):
      try:
        key, value = __hook_exports__.for_next(1)
      except StopIteration:
        __hook_exports__.loop_break()
      s[key] = value
      del key, value
class Dict(object):
  __slots__ = ['_state', '__weakref__']
  def __new__(cls, iterable = None):
    return create_object(Dict, cls)

  def __init__(self, iterable = None):
    notify_update(self)
    if isinstance(iterable, Dict):
      self._state = iterable._state.copy(self)
    else:
      self._state = DictDeterminedState(self)
      if isinstance(iterable, dict):
        for x in iterable:
          self[x] = iterable[x]
      elif iterable is not None:
        self._init_from_iterable(iterable)
  def _init_from_iterable(self, iterable):
    run_in_sandbox(_dict_init_from_iterable, locals())
  def __setitem__(self, key, value):
    self._state[key] = value

  def __getitem__(self, key):
    return self._state[key]
  
  def __delitem__(self, key):
    del self._state[key]

  def __iter__(self):
    return self._state.iterkeys()

  def __contains__(self, key):
    return self._state.has_key(key)

  def has_key(self, key):
    return self._state.has_key(key)

  def iteritems(self):
    return self._state.iteritems()

  def iterkeys(self):
    return self._state.iterkeys()

  def itervalues(self):
    return self._state.itervalues()

  def pop(self, key, default=notgiven):
    return self._state.pop(key, default)

  def popitem(self):
    return self._state.popitem()

  def setdefault(self, key, default=None):
    return self._state.setdefault(key, default)

  def get(self, key, default=None):
    return self._state.get(key, default)

  def update(self, other, **kwds):
    if not isinstance(other, Dict):
      other = Dict(other)
    self._state.update(other)
    if len(kwds):
      self.update(self._from_kwargs(kwds))

  def keys(self):
    return ListType(self._state.iterkeys())

  def values(self):
    return ListType(self._state.itervalues())

  def items(self):
    return ListType(self._state.iteritems())

  def __len__(self):
    return self._state.__len__()

  def __repr__(self):
    return repr(self._state)

  @classmethod
  def _from_kwargs(cls, args):
    d = cls()
    for key, value in args.iteritems():
      d[StringType.create_from_value(key)] = value
    return d

  def _to_kwargs(self):
    if not self._determined():
      raise_checker_error(ValueError, 'Expecting determined keys in kwargs')
    d = {}
    for key, value in self._items.itervalues():
      if not isinstance(key, StringType):
        type_error(key, StringType)
      d[get_determined_value(key)] = value
    return d

  def __nonzero__(self):
    return self._state.__nonzero__()

  def __makefits__(self, other, context):
    context.fit(self._state, other._state)

  def _determined(self):
    return isinstance(self._state, DictDeterminedState)

  def _to_determined(self, value):
    if not self._determined():
      self._state = DictDeterminedState(self, value)
      notify_update(self)

  def _to_undetermined(self):
    if self._determined():
      self._state = DictUndeterminedState(self, self._state)
      notify_update(self)

  def __make__(self):
    return self._state
  def __restore__(self, value, curvalue = None):
    self._state = value
  def __str__(self):
    return str(self._state)
  def __repr__(self):
    return repr(self._state)

Snapshotable.register(DictUndeterminedState)
Immutable.register(DictDeterminedState)
Snapshotable.register(Dict)

Dict.__name__ = 'dict'
defs.DictType = Dict
