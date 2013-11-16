from . import revision

def make_snapshot(self):
  if hasattr(self, '__slots__'):
    slots = self.__slots__
    if isinstance(slots, basestring):
      slots = (slots, )
    cur = {}
    for key in slots:
      if hasattr(self, key):
        cur[key] = getattr(self, key)
  else:
    cur = self.__dict__
  return cur

def restore_snapshot(self, value):
  for key in set(cur.keys()) - set(value.keys()):
    delattr(obj, key)
  for key, v in value.iteritems():
    setattr(obj, key, v)

def __setattr__(self, key, value):
  self._mark_changed()
  if issubclass(self.__class__, object):
    super(DictObject, self).__setattr__(key, value)
  else:
    self.__dict__[key] = value
