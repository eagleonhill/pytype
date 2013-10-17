def getType(x):
  return x.__type

def getRealValue(x):
  return x.__value

def hasRealValue(x):
  return x.__has_value

def typeEqual(a, b):
  # TODO
  return id(a) == id(b)

class TypeValue(type):
  def match(self, other):
    return NotImplemented

# Can do everything, contains all attributes, never fails
class UltimateType(TypeValue):
  def __new__(self):
    return BadType

class UltimateValue:
  def __call__(self, *args, **kargs):
    return self
  def __getattr__(self, name):
    return self

BadType = UltimateValue()

class ValueInstance:
  pass

# A helper class for define builtin argument
class CanBeNone:
  def __init__(self, t):
    self.inner = t
  def match(self, value):
    if value.__class == NoneType:
      return True
    return self.t.match(value)
