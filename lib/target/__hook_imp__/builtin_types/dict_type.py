from defs import *
import defs
from ..checker import type_equal, type_error
from ..type_value import get_determined_value, hooked_isinstance, is_determined

class UndeterminedDict:
  #__metaclass__ = GenericList
  def __init__(self, iterable = None):
    self._items = {}
    self._types = []
    self._maybeempty = False
    if isinstance(iterable, UndeterminedDict):
      self._items = dict(iterable._items)
      self._types = list(iterable._types)
    elif isinstance(iterable, dict):
      for x in iterable:
        self[x] = iterable[x]
    elif iterable is not None:
      for a, b in iterable:
        self[a] = b

  def __setitem__(self, key, value):
    if not self._typeinfo_only() and is_determined(key):
      self._items[get_determined_value(key)] = (key, value)
    if not is_determined(key):
      # Keep type info only
      self._items = {}
    self._add_type(key, value)

  def __getitem__(self, key):
    if is_determined(key) and not self._typeinfo_only():
      return self._items[get_determined_value(key)][1]
    else:
      value_types = self._get_value_type(key)
      if len(value_types) == 1:
        return value_types[0]
      raise NotImplementedError()

  def __iter__(self):
    if self._typeinfo_only():
      raise NotImplementedError();
    else:
      return self._items.__iter__()

  def _add_type(self, key, value):
    if not self._has_type(key, value):
      self._types.append((key, value))
  def __typeeq__(self, other):
    return len(other._types) == len(self._types) and\
        all(map(lambda x: other._has_type_pair(x), self._types))

  def _typeinfo_only(self):
    return len(self._types) != 0 and len(self._items) == 0

  def _has_type_pair(self, pair):
    return self._has_type(pair[0], pair[1])

  def _has_type(self, key, value):
    return any(map(lambda x: \
        type_equal(x[0], key) and type_equal(x[1], value), self._types))
  def _has_key_type(self, key):
    return any(map(lambda x: type_equal(x[0], key), self._types))
  def _get_value_type(self, key):
    return map(lambda x: x[1], \
        filter(lambda x: type_equal(key, x[0]), self._types))
  
  def update(self, other):
    if not isinstance(other, UndeterminedDict):
      checker.type_error(other, UndeterminedDict)
    if other._typeinfo_only() or self._typeinfo_only:
      self._items = {}
    else:
      self._items.update(other._items)
    self._types += filter(lambda x: not self._has_type_pair(x), other._types)

  def keys(self):
    if not self._typeinfo_only():
      return map(lambda x: x[1], self._items.values())
    else:
      raise NotImplementedError()

  def __len__(self):
    if self._typeinfo_only():
      return IntType.create_undetermined()
    else:
      return IntType.create_from_value(len(self._items))

  def _pytypecheck_is_determined(self):
    return not self._typeinfo_only() and\
        all(map(is_determined, self._items.values()))

  def __repr__(self):
    return 'Dict(items=' + str(self._items) + ', types=' + str(self._types) +')'

  @classmethod
  def _from_kwargs(cls, args):
    d = cls()
    for key, value in args.iteritems():
      d[StringType.create_from_value(key)] = value
    return d

  def _to_kwargs(self):
    if self._typeinfo_only():
      raise Exception('Expecting determined keys in kwargs')
    d = {}
    for key, value in self._items.itervalues():
      if not hooked_isinstance(key, str):
        type_error(key, StringType)
      d[get_determined_value(key)] = value
    return d

  def __nonzero__(self):
    if not self._typeinfo_only():
      return len(self._items) > 0
    elif len(self._types) > 0 and not self._maybeempty:
      return True
    elif len(self._types) == 0:
      return False
    else:
      if checker.fork():
        # Make it empty
        self._maybeempty = False
        self._types = []
        self._items = []
        self._length = IntType.create_from_value(0)
        return False
      else:
        # Make it non empty
        self._maybeempty = False
        return True

UndeterminedDict.__name__ = 'dict'
defs.DictType = UndeterminedDict
