import unittest
from ..lib.snapshot.collectionvalue import *
from ..lib.builtin_types import *
from ..lib.type_value import *
from ..lib.traced_frame import TracedFrame, FunctionDecision

class CollectinValueTestCase(unittest.TestCase):
  def test_add(self):
    i3 = IntType.create_from_value(3)
    i2 = IntType.create_from_value(2)
    value = CollectionValue()
    value.addvalue(i2)
    value.addvalue(i3)
    self.assertFalse(is_determined(i2))
    self.assertEqual(len(value.values), 1)
    value.addvalue(StringType.create_from_value('1231'))
    self.assertEqual(len(value.values), 2)
  def test_deref(self):
    i3 = IntType.create_from_value(3)
    i2 = IntType.create_from_value(2)
    value = CollectionValue()
    value.addvalue(i2)
    value.addvalue(StringType.create_from_value('1231'))
    value.addvalue(i3)
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

