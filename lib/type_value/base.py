
# Can do everything, contains all attributes, never fails
class UltimateType:
  def __call__(self, *args, **kargs):
    return self
  def __getattr__(self, name):
    return self

BadType = UltimateType()

def hooked_isinstance(instance, type_):
  from builtin_type import BuiltinObjInstance
  if not isinstance(instance, BuiltinObjInstance) or \
      type(type_) != tuple and issubclass(type_, BuiltinObjInstance):
    return isinstance(instance, type_)
  else:
    t = instance._type
    if type(type_) is not tuple:
      type_ = (type_, )
    return all(map(\
        lambda x:any(map(lambda y: issubclass(x, y), type_)), t.base))
