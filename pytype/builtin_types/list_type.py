from abc import abstractmethod, ABCMeta
import sys
from .defs import *
from . import defs
from ..checker import reraise_error, notify_update, run_in_sandbox, assume
from ..type_value import get_determined_value, is_determined
from ..snapshot import SList, CollectionValue, Immutable, Snapshotable,\
    create_object

notgiven = object()
class ListState:
  __metaclass__ = ABCMeta
  @abstractmethod
  def __getitem__(self, index): pass

  @abstractmethod
  def __setitem__(self, index, value): pass

  @abstractmethod
  def __delitem__(self, index): pass

  @abstractmethod
  def append(self, item): pass

  @abstractmethod
  def sort(self, *arg, **kwds): pass

  @abstractmethod
  def index(self, item): pass

  @abstractmethod
  def count(self, item): pass

  @abstractmethod
  def reverse(self): pass

  @abstractmethod
  def insert(self): pass

  @abstractmethod
  def extend(self, other): pass

  @abstractmethod
  def __imul__(self, other): pass

  @abstractmethod
  def pop(self, index): pass
  
  @abstractmethod
  def __len__(self): pass

  @abstractmethod
  def __iter__(self): pass

  @abstractmethod
  def __nonzero__(self): pass

  @abstractmethod
  def copy(self, list): pass

class ListUnderterminedState(ListState):
  def __init__(self, list, values = []):
    self.value = CollectionValue()
    self.list = list
    self.maybeempty = False
    notify_update(self)
    for v in values:
      self.value.addvalue(v)
  def __getitem__(self, index):
    self.checkindex(index)
    if isinstance(index, slice):
      return self.list
    return self.value.deref()
  def __make__(self):
    return self.maybeempty
  def __restore__(self, value, curvalue = None):
    self.maybeempty = value
  def __setitem__(self, index, value):
    self.checkindex(index)
    if isinstance(index, slice):
      if index == ListUnderterminedState.slice_all:
        self.list._to_determined([])
      self.list.extend(value)
    else:
      self.value.addvalue(value)
  @staticmethod
  def checkindex(index):
    # TODO
    pass
  def onremove(self):
    self.maybeempty = True
    notify_update(self)
  def __delitem__(self, index):
    self.checkindex(index)
    self.onremove()
  def count(self, item):
    v = IntType.create_undetermined()
    assume(v >= IntType.create_from_value(0))
    return v
  def pop(self, item):
    self.onremove()
    return self.value.deref()
  def __len__(self):
    v = IntType.create_undetermined()
    if self.maybeempty:
      assume(v >= IntType.create_from_value(0))
    else:
      assume(v > IntType.create_from_value(0))
    return v
  def __iter__(self):
    return self.value.iterator(self.maybeempty)
  def append(self, value):
    self.value.addvalue(value)
    if self.maybeempty:
      self.maybeempty = False
      notify_update(self)
  def extend(self, other):
    if not other._determined():
      for v in other._state.value.values:
        self.value.addvalue(v)
      if not other._state.maybeempty and self._state.maybeempty:
        self.maybeempty = False
        notify_update(self)
    else:
      for v in other._state:
        self.append(v)
  def insert(self, index, value):
    self.checkindex(index)
    self.append(value)
  def __nonzero__(self):
    if not self.maybeempty:
      return True
    if checker.fork():
      self.maybeempty = False
      notify_update(self)
      return True
    else:
      self.list._to_determined([])
      return False
  def copy(self, list):
    new = ListUnderterminedState(list)
    new.value = self.value.clone()
    new.maybeempty = self.maybeempty
    notify_update(new)
    return new
  def __repr__(self):
    return '{%slist: %s}' %\
        ('nonempty' if not self.maybeempty else '', repr(self.value))
  def __imul__(self, other):
    if not isinstance(other, IntType):
      raise_checker_error(TypeError, 
          "can't multiply sequence by non-int of type %s" % type(other))
    return self
  def reverse(self): pass
  def sort(self, cmp=None, key=None, reserve=None): pass
  def index(self, item, i, j):
    return IntType.create_undetermined()
  def __makefits__(self, other, context):
    if isinstance(other, ListUnderterminedState):
      context.fit(self.value, other.value)
      if context.get_data(other) and not self.maybeempty:
        self.maybeempty = True
        notify_update(self)
    elif isinstance(other, ListDerterminedState):
      for v in context.get_data(other.data):
        self.value.addvalue(v, context)
    else:
      context.fail()

class ListDerterminedState(ListState):
  def __init__(self, list, values):
    self.data = SList(values)
    self.list = list
  def __getitem__(self, index):
    # TODO: convert using __index__
    if is_determined(index):
      return self.data[get_determined_value(index)]
    if isinstance(index, slice):
      # Undetermined index
      other = List(self.list)
      other._to_undetermined()
      return other[index]
    elif isinstance(index, IntType):
      # undetermined index
      from ..traced_frame import TracedFrame, FunctionDecision
      cur_frame = TracedFrame.current()
      if not cur_frame.has_more_decisions():
        cur_frame.add_decision(FunctionDecision.from_values(self))
      return cur_frame.get_next_call_decision()
    else:
      raise_checker_error(TypeError, 
          'list indices must be integers, not %s' % type(index))
  def __setitem__(self, index, value):
    if is_determined(index):
      self.data[get_determined_value(index)] = value
    self.list._to_undetermined()
    self.list[index] = value

  def copy(self, list):
    return ListDerterminedState(list, self.data)
  def __delitem__(self, index):
    if is_determined(index):
      del self.data[get_determined_value(index)]
    self.list._to_undetermined()
    del self.list[index]
  def __iter__(self):
    return self.data.__iter__()
  def __imul__(self, other):
    if not is_determined(other):
      self.list._to_undetermined()
      self.list *= other
      return self.list
    self.data *= get_determined_value(other)
  def append(self, item):
    self.data.append(item)
  def insert(self, index, item):
    if not is_determined(index):
      self.list._to_undetermined()
      self.list.insert(index, item)
      return
    self.data.insert(get_determined_value(index), item)
  def index(self, item):
    # TODO
    raise NotImplementedError
  def pop(self, i):
    if not is_determined(i):
      self.list._to_undetermined()
      return self.list.pop(i)
    return self.data.pop(get_determined_value(i))
  def reverse(self):
    return self.data.reverse()
  def sort(self, *args, **kwds):
    if not all (is_determined(x) for x in self.data):
      self.list._to_undetermined()
    else:
      self.data.sort(*args, **kwds)
  def extend(self, other):
    if other._determined():
      self.data += other._state.data
    else:
      self.list._to_undetermined()
      self.list += other
  def __repr__(self):
    return repr(self.data)
  def __len__(self):
    return IntType.create_from_value(len(self.data))
  def count(self, item):
    # TODO: no-sideeffect compare
    return self.data.count(item)
  def __nonzero__(self):
    return bool(self.data)
  def __makefits__(self, other, context):
    fitted = False
    if isinstance(other, ListDerterminedState):
      fitted = context.try_fit(self.data, other.data)
    if not fitted:
      if context.flags & context.FITS_LIST:
        self.list._to_undetermined()
        context.fit(self.list._state, other)
      else:
        context.fail()

Immutable.register(ListDerterminedState)

def _from_iterable_func():
  s = self
  while __hook_exports__.do_for(1, lambda: iterable):
    with __hook_exports__.frame(1):
      try:
        v = __hook_exports__.for_next(1)
      except StopIteration:
        __hook_exports__.loop_break()
      s.append(v)
      del v

class List(object):
  __slots__ = ['_state', '__weakref__']
  def __new__(cls, iterable = None):
    return create_object(List, cls)
  def __init__(self, iterable = None):
    if isinstance(iterable, List):
      self._state = iterable._state.copy(self)
      notify_update(self)
    if isinstance(iterable, (list, tuple, str)):
      self._state = ListDerterminedState(self, iterable)
      notify_update(self)
    else:
      self._state = ListDerterminedState(self, None)
      notify_update(self)
      if iterable is not None:
        self._init_from_iterable(iterable)

  def _init_from_iterable(self, iterable):
    run_in_sandbox(_from_iterable_func, locals())
  def __getitem__(self, index):
    return self._state[index]

  def __setitem__(self, key, value):
    self._state[key] = value
  def __delitem__(self, index):
    del self._state[index]
  def __iter__(self):
    return self._state.__iter__()
  def __add__(self, other):
    new = List(self)
    new += other
    return new
  def __iadd__(self, other):
    self._state.extend(other)
    return self
  def extend(self, other):
    self._state.extend(other)
  def __mul__(self, other):
    new = List(self)
    new *= other
    return new
  def _to_undetermined(self):
    if not self._determined():
      return
    self._state = ListUnderterminedState(self, self._state)
    notify_update(self)
  def _to_determined(self, values):
    if self._determined():
      return
    self._state = SList(values)
    notify_update(self)
  def _determined(self):
    return isinstance(self._state, ListDerterminedState)

  def append(self, element):
    self._state.append(element)
  def __len__(self):
    return self._state.__len__()
  def __repr__(self):
    return repr(self._state)
  def __nonzero__(self):
    return bool(self._state)
  def __make__(self):
    return self._state
  def __restore__(self, value, oldvalue=None):
    self._state = value
  def insert(self, index, item):
    self._state.insert(index, item)
  def pop(self, index = notgiven):
    if index is notgiven:
      index = IntType.create_from_value(-1)
    return self._state.pop(index)
  def index(self, item, i = notgiven, j = notgiven):
    if i is notgiven:
      i = IntType.create_from_value(0)
    if j is notgiven:
      j = IntType.create_from_value(sys.maxint)
    return self._state.index(item, i, j)
  def __makefits__(self, other, context):
    if type(other) is not type(self):
      context.fail()
    state = context.get_data(other)
    context.fit(self._state, state)
  def remove(self, item):
    i = self.index(item)
    del self[i]
  def revsere(self):
    self._state.reverse()
  def sort(self, *args, **kwds):
    self._state.sort(*args, **kwds)

  __hash__ = None

List.__name__ = 'list'
Snapshotable.register(List)

defs.ListType = List
