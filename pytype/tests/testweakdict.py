import unittest
from ..snapshot.weak_dict import SIDWeakKeyDictionary

class ValueRef(object):
  def __init__(self, value):
    self.value = value
  def __hash__(self):
    return hash(self.value)
  def __eq__(self, other):
    if not isinstance(other, ValueRef):
      return False
    return self.value == other.value

class SIDWeakKeyDictionaryTestCase(unittest.TestCase):
  def test_builtin(self):
    d = SIDWeakKeyDictionary()
    a = ValueRef(1)
    b = ValueRef(1)
    
    self.assertEqual(hash(a), hash(b))
    self.assertEqual(a, b)
    self.assertNotEqual(id(a), id(b))
    d2 = {}
    d2[a] = 3
    d2[b] = 4
    self.assertEqual(d2[a], 4)
    del d2
    d[a] = 3
    d[b] = 4
    self.assertEqual(d[a], 3)
    self.assertEqual(d[b], 4)
    self.assertEqual(len(d), 2)
    del a
    self.assertEqual(len(d), 1)

if __name__ == '__main__':
  unittest.main()

