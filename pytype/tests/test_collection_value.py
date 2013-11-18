import unittest
from ..snapshot.collectionvalue import *
from ..builtin_types import *
from ..type_value import *
from ..traced_frame import TracedFrame, FunctionDecision

class CollectinValueTestCase(unittest.TestCase):
  def test_add(self):
    i0 = IntType.create_from_value(0)
    j0 = IntType.create_from_value(0)
    value = CollectionValue()
    value.addvalue(i0)
    value.addvalue(j0)
    self.assertEqual(len(value.values), 1)
    for i in range(1, 5):
      x = IntType.create_from_value(i)
      value.addvalue(x)
      self.assertEqual(len(value.values), i + 1)
    # Aggresive merge triggered
    i2 = IntType.create_from_value(6)
    value.addvalue(i2)
    self.assertEqual(len(value.values), 1)
    value.addvalue(StringType.create_from_value('1231'))
    self.assertEqual(len(value.values), 2)
  def test_deref(self):
    value = CollectionValue()
    for i in range(5):
      x = IntType.create_from_value(i)
      value.addvalue(x)
      self.assertEqual(len(value.values), i + 1)
    path = 0
    f = TracedFrame(FunctionDecision())
    while f.next_path():
      with f:
        x = value.deref()
        path += 1
    self.assertEqual(path, 5)
    value.addvalue(StringType.create_from_value('1231'))
    f = TracedFrame(FunctionDecision())
    path = 0
    hasint = False
    hasstr = False
    while f.next_path():
      with f:
        x = value.deref()
        path += 1
        if isinstance(x, IntType):
          hasint = True
        if isinstance(x, StringType):
          hasstr = True
    self.assertEqual(path, 2)
    self.assertTrue(hasint)
    self.assertTrue(hasstr)

if __name__ == '__main__':
  unittest.main()

