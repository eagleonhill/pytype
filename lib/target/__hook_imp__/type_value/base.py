
# Can do everything, contains all attributes, never fails
class UltimateType:
  def __call__(self, *args, **kargs):
    return self
  def __getattr__(self, name):
    return self

BadType = UltimateType()

def hooked_isinstance(instance, type_):
  from builtin_type import BuiltinObjInstance, BuiltinObjDeterminedInstance
  if not isinstance(instance, BuiltinObjInstance) or \
      (type(type_) == type(BuiltinObjInstance) and \
      issubclass(type_, BuiltinObjInstance)):
    return isinstance(instance, type_)
  elif isinstance(instance, BuiltinObjDeterminedInstance):
    return isinstance(instance._value, type_)
  else:
    t = instance._type
    if type(type_) is not tuple:
      type_ = (type_, )
    return all(map(\
        lambda y:any(map(lambda x: issubclass(y, x), t.base)), type_))
