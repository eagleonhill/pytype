import unittest
from ..builtin_types import *
from ..makefits import type_make_fit
from ..type_value import is_determined, get_determined_value

class MakeFitsTestCase(unittest.TestCase):
  def test_builtin(self):
    a = IntType.create_from_value(3)
    b = IntType.create_from_value(4)
    self.assertTrue(type_make_fit(a, b))
    self.assertFalse(is_determined(a))

    c = IntType.create_from_value(4)
    self.assertTrue(type_make_fit(c, b))
    self.assertTrue(is_determined(c))
    self.assertEqual(get_determined_value(c), 4)

    s = StringType.create_from_value('3')
    self.assertFalse(type_make_fit(s, b))

  def test_list(self):
    x = ListType([StringType.create_from_value('b')])

    # Merge same element type
    a = ListType([StringType.create_from_value('a')])
    self.assertTrue(type_make_fit(a, x))
    self.assertEquals(get_determined_value(a._length), 1)
    self.assertFalse(is_determined(a[0]))

    # Merge different element type
    b = ListType([IntType.create_undetermined()])
    self.assertTrue(type_make_fit(b, x))
    self.assertFalse(is_determined(b._length))
    self.assertTrue(b._has_type(IntType.create_undetermined()))
    self.assertTrue(b._has_type(StringType.create_undetermined()))

    # Merge different length
    c = ListType([
      StringType.create_undetermined(),
      IntType.create_from_value(1),
    ])
    self.assertTrue(type_make_fit(c, x))
    self.assertFalse(is_determined(c._length))

    d = ListType([IntType.create_from_value(3)])
    self.assertTrue(type_make_fit(d, x))
    self.assertFalse(is_determined(d._length))
    self.assertTrue(d._has_type(IntType.create_undetermined()))
    self.assertTrue(d._has_type(StringType.create_undetermined()))

  def test_dict(self):
    keya = StringType.create_from_value('a')
    keyb = StringType.create_from_value('b')
    keyu = StringType.create_undetermined()
    keyi = IntType.create_from_value(1)

    x = DictType()
    x[keya] = IntType.create_from_value(3)

    # Same key, different value
    a = DictType()
    a[keya] = IntType.create_from_value(4)
    self.assertTrue(type_make_fit(a, x))
    self.assertIsInstance(a[keya], IntType)
    self.assertFalse(is_determined(a[keya]))
    self.assertEquals(len(a._get_value_type(keya)), 1)

    # Same key, different value type
    b = DictType()
    b[keya] = StringType.create_from_value('3')
    self.assertTrue(type_make_fit(b, x))
    self.assertEquals(len(b._get_value_type(keya)), 2)

    # Same key/value type
    c = DictType()
    c[keyb] = IntType.create_from_value(4)
    self.assertTrue(type_make_fit(c, x))
    self.assertTrue(c._typeinfo_only())
    self.assertEquals(len(c._get_value_type(keya)), 1)
    self.assertEquals(len(c._types), 1)

    # Different key/value type
    d = DictType()
    d[keyi] = StringType.create_undetermined()
    self.assertTrue(type_make_fit(d, x))
    self.assertTrue(d._typeinfo_only())
    self.assertEquals(len(d._types), 2)
    self.assertEquals(len(d._get_value_type(keya)), 1)
    self.assertEquals(len(d._get_value_type(keyi)), 1)

  def test_obj(self):
    from ..snapshot import BaseObject, SnapshotableMetaClass
    class A(BaseObject):
      __metaclass__ = SnapshotableMetaClass
    class B:
      __metaclass__ = SnapshotableMetaClass
    for a, b in [(A(), A()), (B(), B())]:
      self.assertTrue(type_make_fit(a, b))
      a.x = IntType.create_from_value(3)
      self.assertFalse(type_make_fit(a, b))

      b.x = IntType.create_from_value(3)
      self.assertTrue(type_make_fit(a, b))
      self.assertTrue(is_determined(a.x))
      self.assertEquals(get_determined_value(a.x), 3)

      b.a = b
      a.a = a
      self.assertTrue(type_make_fit(a, b))

      b.x = IntType.create_from_value(4)
      a.z = IntType.create_from_value(3)
      b.z = StringType.create_undetermined()
      self.assertFalse(type_make_fit(a, b))
      # Mustn't change current value
      self.assertTrue(is_determined(a.x))
      self.assertEquals(get_determined_value(a.x), 3)

if __name__ == '__main__':
  unittest.main()

