
# Can do everything, contains all attributes, never fails
class UltimateType(object):
  def __call__(self, *args, **kargs):
    return self
  def __getattribute__(self, name):
    if name == '__class__':
      return UltimateType
    return self
  def __setattr__(self, name, value):
    pass

BadType = UltimateType()
