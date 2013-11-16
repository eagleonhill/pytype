import threading

status = threading.local()
status.loop = 0
status.matching_pairs = {}

class FittingFailedException(Exception):
  pass

def type_make_fit(target, source):
  """ Make target can represent source, return False if failed and target is
  remain unchanged"""
  from .checker import get_revision_manager
  cur = get_revision_manager().commit()
  status.loop += 1
  try:
    type_make_fit_internal(target, source)
  except FittingFailedException:
    get_revision_manager().discard()
    get_revision_manager().set_rev(cur)
    return False
  finally:
    status.loop -= 1
    if status.loop == 0:
      status.matching_pairs.clear()
  return True

def type_make_fit_internal(target, source):
  if target is source:
    return target
  matching = status.matching_pairs.setdefault(id(target), set())
  if id(source) in matching:
    return
  matching.add(id(source))
  if type(target) is not type(source):
    # Impossible
    raise FittingFailedException
  elif type(target) is bool and target != source:
    raise FittingFailedException
  elif type(target) is tuple:
    if len(target) != len(source):
      raise FittingFailedException
    for t, s in zip(target, source):
      type_make_fit_internal(t, s)
  elif type(target) is slice:
    type_make_fit_internal(target.start, source.start)
    type_make_fit_internal(target.step, source.step)
    type_make_fit_internal(target.stop, source.stop)
  elif hasattr(target, '__makefits__'):
    target.__makefits__(source)
  else:
    generic_make_fit(target, source)

def generic_make_fit(target, source):
  td, sd = [getattr(x, '__dict__', None) for x in (target, source)]
  if td is None or sd is None:
    raise FittingFailedException
  if td.keys() != sd.keys():
    raise FittingFailedException
  for x in td:
    type_make_fit_internal(td[x], sd[x])

