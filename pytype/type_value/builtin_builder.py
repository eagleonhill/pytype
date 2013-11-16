from builtin_type import BuiltinTypeInternal
from func_type import BuiltinFunc
from types import ModuleType

class Module:
  def __init__(self, real, defs):
    self.real = real
    self.defs = defs
    # Should be topmost
    self.name = real.__name__
  def build(self, parent = None):
    ret = ModuleType(self.name, self.real.__doc__)
    for d in self.defs:
      name = d.name
      value = d.build(self)
      setattr(ret, name, value)
    return ret

class Type:
  def __init__(self, name, real_type, defs):
    self.defs = defs
    self.name = name
    self.real_type = real_type
  def build(self, parent):
    ret = BuiltinTypeInternal(name, real_type)
    self.rebuild(parent, ret)
    return ret.get_type()
  
  def rebuild(self, value):
    value.attr = {}
    for d in self.defs:
      name = d.name
      value.attr[name] = d.build(self)

class Func:
  def __init__(self, name, args, return_type, **attrs):
    self.name = name
    self.args = args
    self.return_type = return_type
    self.attrs = attrs

  def build(self, parent):
    ret = BuiltinFunc(self.name);
    self.rebuild(ret)
    return ret

  def rebuild(self, value):
    value.set_attribute(**self.attrs)
    for arg in self.args:
      if isinstance(arg, tuple):
        format_str, args = arg
      else:
        format_str, args = arg, None
      value.add_from_format_str(format_str, args, self.return_type)
    return value

class Value:
  def __init__(self, name, value):
    self.name = name
    self.value = value

  def build(self, parent):
    return self.value

def export(globals_, module):
  for key in module.__dict__:
    value = module.__dict__[key]
    globals_[key] = value
