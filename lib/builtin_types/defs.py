from ..type_value import BuiltinTypeInternal, is_determined,\
    get_determined_value

IntType = BuiltinTypeInternal('int', (int, long))
IndexType = BuiltinTypeInternal('int', (int, long))
BoolType = BuiltinTypeInternal('bool', (int, ))
BoolType.get_type()
BoolType.base = (bool, )
FloatType = BuiltinTypeInternal('float', (float, ))
StringType = BuiltinTypeInternal('str', (str, ))

ListType = None
DictType = None

