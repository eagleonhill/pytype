import checker
from base import TypeValue, BadType, getRealValue, hasRealValue,\
    CanBeNone

class FuncValue:
  pass

class InvokePattern:
  def __init__(self, args):
    self.f = f
    self.args = args
    self.returnType = BadType
    self.error = error
  def match(self, args):
    # TODO: check kargs
    # TODO: check determined values
    args = inspect.getcallargs(f, *args, **kargs)
    # TODO: Use dict match
    if args.keys() != self.args.keys():
      return False
    for k in args:
      if not args[k].match(self.args[k]):
        return False
    return True
  def compute(self):
    # TODO
    pass
  def getResult(self, args):
    pass

# Function created by 'def'
class UserFunc(FuncValue):
  def __init__(self, f, static):
    self.f = f
    self.patterns = []
    self.static = static
  def __call__(self, *args, **kargs):
    try:
      args = inspect.getcallargs(f, *args, **kargs)
    except TypeError as e:
      checker.type_error(e)
      return BadType
    
    for pattern in self.patterns:
      if pattern.match(args):
        return pattern.getResult(args)
    pattern = InvokePattern(self.f, args)
    pattern.compute()
    self.patterns.append(pattern)
    return pattern.getResult(args)

# Use a replacement frunction, and bypass type check
# Assume number of argument is always correct. For operators/implicit calls only
class StubFunc(FuncValue):
  def __init__(self, func):
    self.func = func
  def __call__(self, *args, **kargs):
    return self.func(*args, **kargs)
    try:
      return self.func(*args, **kargs)
    except TypeError as ex:
      print 'Bad internal call!'
      checker.type_error(self, ex)
      return BadType

class FormatStrParser:
  mapping = None
  @classmethod
  def setup(cls):
    if cls.mapping == None:
      # TODO: Auto register
      from ..builtin_types.defs import *
      cls.mapping = {
          'b': BoolType,
          's': StringType,
          'i': IntType,
          'l': IndexType,
          'f': FloatType,
          't': None,
          }

  @classmethod
  def getitem(cls, item):
    assert item.lower() in cls.mapping
    t = cls.mapping[item.lower()]
    if item.upper() == item:
      return CanBeNone(t)
    else:
      return t

  @classmethod
  def parse_item(cls, item):
    cls.setup()
    return cls.getitem(item)

  @classmethod 
  def parse(cls, formatstr, args):
    cls.setup()
    if args is None:
      args = []
    mapping = cls.mapping
    types = []
    optionaltypes = []
    cur = types
    argindex = 0
    for ch in formatstr:
      if ch == '|':
        cur = optionaltypes
      elif ch == 't' or ch == 'T':
        # Get a type from args
        cur.append(args[argindex])
        argindex += 1
      else:
        cur.append(cls.getitem(ch))
    return types, optionaltypes

# Do a simple type-check, and call the builtin function
class BuiltinFunc(FuncValue):
  def __init__(self, name):
    self.call_default = True
    self.name = name
    self.patterns = []

  def set_attribute(self, call_default = True, sideeffect = False):
    self.call_default = call_default
    self.sideeffect = sideeffect

  def add_pattern(self, types, optionalTypes, returnType):
    if optionalTypes is None:
      optionalTypes = []
    self.patterns.append((types, optionalTypes, returnType))

  def add_from_format_str(self, formatstr, args, returnType):
    types, optionalTypes = FormatStrParser.parse(formatstr, args)
    if isinstance(returnType, str):
      returnType = FormatStrParser.parse_item(returnType)
    self.add_pattern(types, optionalTypes, returnType)

  def __str__(self):
    return self.name

  def __call__(self, context, *args):
    for types, optionalTypes, returnType in self.patterns:
      if len(types) < len(args):
        continue
      check_func = lambda a, b: a is None or isinstance(a, b)
      checked = all(map(check_func, args, types + optionalTypes))
      if checked:
        break;
    else:
      checker.type_error(args, types + optionalTypes)
      return BadType
    
    if self.call_default and hasRealValue(context) and \
        all(map(lambda x: hasRealValue(x), args)):
      vargs = map(lambda x: getRealValue(x), args)
      return returnType(getattr(getRealValue(context), self.name)(*vargs))
    return returnType()

class InstanceFunc:
  def __init__(self, func, context):
    self.func = func
    self.context = context
  def __call__(self, *args, **kargs):
    return self.func(self.context, *args, **kargs)

