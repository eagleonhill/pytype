from ..type_value import BuiltinTypeInternal, is_determined,\
    get_determined_value

IntTypeInternal = BuiltinTypeInternal('int', (int, long))
IntType = IntTypeInternal.create_type()
class t(object):pass
BoolType = t()
del t
FloatTypeInternal = BuiltinTypeInternal('float', (float, ))
FloatType = FloatTypeInternal.create_type()
StringTypeInternal = BuiltinTypeInternal('str', (str, ))
StringType = StringTypeInternal.create_type()

ListType = None
DictType = None

