import checker
from ..snapshot import SWeakKeyDictionary, SDict,\
    SnapshotableMetaClass
from builtin_type import get_determined_value, is_determined, BuiltinObjInstance
from func_type import StubFunc
from ..builtin_types.defs import IntType, FloatType

class CompareHistory:
  __metaclass__ = SnapshotableMetaClass
  inverse_op = {
      '__eq__': '__eq__',
      '__ne__': '__ne__',
      '__lt__': '__gt__',
      '__le__': '__ge__',
      '__ge__': '__le__',
      '__gt__': '__lt__',
      }
  operatormap = {
      '__le__': frozenset([-1, 0]),
      '__ge__': frozenset([1, 0]),
      '__ne__': frozenset([-1, 1]),
      '__eq__': frozenset([0]),
      '__lt__': frozenset([-1]),
      '__gt__': frozenset([1]),
      }
  @classmethod
  def get_comparer(cls, value):
    try:
      return value.__comparer
    except AttributeError:
      value.__comparer = cls(value)
      return value.__comparer

  def __init__(self, value):
    self.value = value
    # Compare to constant
    self.low = None
    self.low_inclusive = True
    self.high = None
    self.high_inclusive = True
    self.nonequal = SDict()

    # Compare to undertermined value
    self.comp = SWeakKeyDictionary()

  def update(self, value, s):
    if s == set([0]):
      del self.value.__comparer
      self.value._make_determined(value)
      return
    elif s == set([-1]):
      # self < value
      if self.high is None or value <= self.high:
        self.high = value
        self.high_inclusive = False
    elif s == set([0, -1]):
      # self <= value
      if self.high is None or value < self.high:
        self.high = value
        self.high_inclusive = True
    elif s == set([1]):
      # self > value
      if self.low is None or value >= self.low:
        self.low = value
        self.low_inclusive = False
    elif s == set([0, 1]):
      # self >= value
      if self.low is None or value > self.low:
        self.low = value
        self.low_inclusive = True
    elif s == set([-1, 1]):
      # self != value
      self.nonequal[value] = True
    if self.low == self.high and self.low is not None:
      if self.low_inclusive and self.high_inclusive:
        del self.value.__comparer
        self.value._make_determined(self.low)
      else:
        # Shouldn't happen
        assert False, 'Inconsistent compare result'
        checker.impossible_path()

  def compare_variable(self, other, operator):
    op = self.operatormap[operator]
    # Hash is unique for object
    self.comp.setdefault(other, set([0, 1, -1]))
    s = self.comp[other]
    trues = op & s
    falses = (set([0, 1, -1]) - op) & s
    if trues and falses:
      if checker.fork():
        s &= trues
        self.get_comparer(other).set_from_inverse(s)
        return True
      else:
        s &= falses
        self.get_comparer(other).set_from_inverse(s)
        return False
    else:
      # No information gain
      return True if trues else False

  def compare_constant(self, other, operator):
    s = set([0, 1, -1])
    if self.low is not None:
      if self.low > other or self.low == other and not self.low_inclusive:
        # self > other
        s = set([1])
      elif self.low == other and self.low_inclusive:
        # self >= other
        s = set([0, 1])

    if self.high is not None:
      if self.high < other or self.high == other and not self.high_inclusive:
        # self < other
        s &= set([-1])
      elif self.high == other and self.high_inclusive:
        # self <= other
        s &= set([-1, 0])
    if other in self.nonequal:
      s &= set([-1, 1])
    trues = self.operatormap[operator]
    falses = set([0, 1, -1]) - trues
    trues &= s
    falses &= s
    if trues and falses:
      if checker.fork():
        self.update(other, trues)
        return True
      else:
        self.update(other, falses)
        return False
    else:
      # No information gain
      return True if trues else False

  def compare(self, other, operator):
    assert not is_determined(self.value) or not is_determined(other), \
        'Comparing determined object'
    if is_determined(self.value):
      return self.get_comparer(other).compare(
          self.value, inverse_op[operator])
    if is_determined(other):
      return self.compare_constant(get_determined_value(other), operator)
    else:
      return self.compare_variable(other, operator)

NumerialTypes = (IntType, FloatType)
def type_comparable(x, y):
  if type(x) == type(y):
    return True
  if isinstance(x, NumerialTypes) and \
      isinstance(y, NumerialTypes):
    return True
  return False

def system_compare(x, y):
  # When x and y are not comparable
  # Numbers are smallest
  if isinstance(x, NumerialTypes):
    return -1
  if isinstance(y, NumerialTypes):
    return 1
  if x.__class__ == BuiltinObjInstance:
    type_x = x._type.name
  else:
    type_x = type(x).__name__
  if y.__class__ == BuiltinObjInstance:
    type_y = y._type.name
  else:
    type_y = type(y).__name__
  if type_x != type_y:
    return cmp(type_x, type_y)
  return cmp(id(x), id(y))

def _default_cmp(op, x, y):
  if x is y:
    # Same reference, always equal
    return op in ['__eq__', '__le__', '__ge__']

  if is_determined(x) and is_determined(y):
    # Both have determined value
    import operator
    return getattr(operator, op)(
        get_determined_value(x), get_determined_value(y))

  if not type_comparable(x, y):
    import operator
    checker.uncomparable_warning(x, y)
    return getattr(operator, op)(system_compare(x, y), 0)
  return CompareHistory.get_comparer(x).compare(y, op)

def get_cmp(op):
  return lambda x, y: _default_cmp(op, x, y)

default_cmp = {}
for op in ['eq', 'ne', 'lt', 'gt', 'le', 'ge']:
  opf = '__' + op + '__'
  default_cmp[opf] = StubFunc(get_cmp(opf))
