from .checker import get_revision_manager

class FittingFailedException(Exception):
  pass

class FittingContext(object):
  FITS_BUILTIN_VALUE = 0x01
  FITS_LIST = 0x02
  FITS_DICT = 0x04

  def __init__(self, flags):
    self.flags = flags
    self.matching_pairs = {}
    self.matching_pair_all = {flags: self.matching_pairs}
    self.target_rev = None
  def set_flags(self, new_flag):
    old_flag = self.flags
    self.matching_pair_all.setdefault(new_flag, {})
    self.matching_pairs = self.matching_pair_all[new_flag]
    self.flags = new_flag
    return old_flag
  def allow_fit_builtin_value(self):
    return self.flags & FITS_BUILTIN_VALUE
  def fail(self):
    raise FittingFailedException
  @property
  def rev_matching(self):
    return self.target_rev is not None
  def fit(self, target, source):
    if target is source and not self.rev_matching:
      return
    matching = self.matching_pairs.setdefault(id(target), set())
    if id(source) in matching:
      return
    matching.add(id(source))
    if type(target) is bool:
      if type(source) is not type(target) or target != source:
        self.fail()
    elif type(target) is tuple:
      if type(source) is not type(target):
        self.fail()
      if len(target) != len(source):
        self.fail()
      for t, s in zip(target, source):
        self.fit(t, s)
    elif type(target) is slice:
      if type(source) is not type(target):
        self.fail()
      self.fit(target.start, source.start)
      self.fit(target.step, source.step)
      self.fit(target.stop, source.stop)
    elif hasattr(target, '__makefits__'):
      target.__makefits__(source, self)
    else:
      raise NotImplementedError, 'Fitting function required'

  def try_fit(self, target, source):
    try:
      start_rev = get_revision_manager().commit()
      self.fit(target, source)
      return True
    except FittingFailedException:
      get_revision_manager().discard()
      get_revision_manager().set_rev(start_rev)
      return False
  def get_data(self, obj):
    if self.rev_matching:
      return self.target_rev.getstatefor(obj)
    else:
      return obj.__make__()

  def try_fit_rev(self, source):
    # TODO
    raise NotImplementedError

  def try_fit_local_rev(self, local, otherrev):
    if local.keys() != otherrev.local.keys():
      return False
    try:
      self.target_rev = otherrev
      start_rev = get_revision_manager().commit()
      for k in local.iterkeys():
        self.fit(local[k], otherrev.local[k])
      return True
    except FittingFailedException:
      get_revision_manager().discard()
      get_revision_manager().set_rev(start_rev)
      return False

def fit_obj(target, source, flags):
  context = FittingContext(flags)
  return context.try_fit(target, source)
