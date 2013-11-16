from types import ModuleType
import builtin_modules.__builtins__ as builtin
import hook_exports
from snapshot import SnapshotableMetaClass

builtin_module = ModuleType('__builtin__')
builtin.export_module(builtin_module.__dict__)
g = dict()
g['__builtins__'] = builtin_module
g['__hook_exports__'] = hook_exports
g['__name__'] = None
g['__package__'] = None
g['__doc__'] = None
g['__metaclass__'] = SnapshotableMetaClass

def get_globals(name, file='None', doc=None, package=None):
  d = dict(g)
  d['__name__'] = name
  d['__file__'] = file
  d['__package__'] = package
  d['__doc__'] = doc
  return d
