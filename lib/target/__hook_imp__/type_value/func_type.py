import checker
from base import BadType, hooked_isinstance
from builtin_type import get_determined_value, is_determined

class InvokePattern(object):
  def __init__(self, args):
    self.f = f
    self.args = args
    self.return_type = BadType
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
  def get_result(self, args):
    pass

class FuncValue:
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
    # TODO: verify signature
    return self.func(*args, **kargs)

class BuiltinInvokePattern(InvokePattern):
  def __init__(self, args, optional_args, return_type):
    if args is None:
      args = []
    if optional_args is None:
      optional_args = []
    from builtin_type import BuiltinTypeInternal
    def convert(x):
      if isinstance(x, BuiltinTypeInternal):
        return x.base
      else:
        return x
    args = map(convert, args)
    optional_args = map(convert, optional_args)
    self.args = args
    self.optional_args = optional_args
    self.all_args = args + optional_args
    self.return_type = return_type

  def match(self, args):
    if len(args) < len(self.args) or len(args) > len(self.all_args):
      return False
    return all(map(hooked_isinstance, args, self.all_args))
  
  @classmethod
  def create_from_format(cls, formatstr, args, return_type):
    args, optional_args = FormatStrParser.parse(formatstr, args)
    if type(return_type) == str:
      return_type = FormatStrParser.get_return_type(return_type)
    return cls(args, optional_args, return_type)
  
  def __repr__(self):
    return '({0}, [{1}]):{2}'.format(
        ', '.join(map(str, self.args)),
        ', '.join(map(str, self.optional_args)),
        str(self.return_type)
        )

class FormatStrParser:
  mapping = None
  wrapper = None
  @classmethod
  def setup(cls):
    if cls.mapping == None:
      # TODO: Auto register
      from ..builtin_types import defs
      b = defs
      cls.wrapper = {
          'b': b.BoolType,
          's': b.StringType,
          'i': b.IntType,
          'l': b.IndexType,
          'f': b.FloatType,
          't': None,
          }
      cls.mapping = {
          'b': (bool,),
          's': (str,),
          'i': (int, long),
          'l': (b.IndexType,),
          'f': (float,),
          't': None
          }

  @classmethod
  def getitem(cls, item, args):
    if (item.lower() == 't'):
      t = args.pop()
      if type(t) != tuple:
        t = (t, )
    else:
      assert item.lower() in cls.mapping, 'Unknown type ' + item
      t = cls.mapping[item.lower()]
    if item.isupper():
      return (type(None), ) + t
    else:
      return t

  @classmethod
  def get_return_type(cls, item):
    return cls.wrapper[item]

  @classmethod
  def parse_item(cls, item):
    cls.setup()
    return cls.getitem(item)

  @classmethod 
  def parse(cls, formatstr, args):
    cls.setup()
    if args is None:
      args = []
    args = args.reverse()
    mapping = cls.mapping
    types = []
    optionaltypes = []
    cur = types
    argindex = 0
    for ch in formatstr:
      if ch == '|':
        cur = optionaltypes
      else:
        cur.append(cls.getitem(ch, args))
    return types, optionaltypes

# Do a simple type-check, and call the builtin function if applicable
class BuiltinFunc(FuncValue):
  def __init__(self, name):
    self.call_default = True
    self.name = name
    self.patterns = []

  def set_attribute(self, call_default = True, sideeffect = False):
    self.call_default = call_default
    self.sideeffect = sideeffect
  
  def add_from_format_str(self, formatstr, args, return_type):
    self.patterns.append(
        BuiltinInvokePattern.create_from_format(formatstr, args, return_type))

  def add_pattern(self, args, optional_args, return_type):
    self.patterns.append(BuiltinInvokePattern(args, optional_args, return_type))

  def __str__(self):
    return self.name

  def can_invoke_stub(self, context, args):
    return self.call_default and all(map(is_determined, (context, ) + args))

  def get_matched_pattern(self, args):
    f = filter(lambda x: x.match(args), self.patterns)
    if len(f) == 0:
      return None
    else:
      return f[0]
  def __call__(self, context, *args):
    pattern = self.get_matched_pattern(args)
    if pattern is None:
      checker.argument_error(args, self.patterns)

    if self.can_invoke_stub(context, args):
      vargs = map(lambda x: get_determined_value(x), args)
      value = (getattr(get_determined_value(context), self.name)(*vargs))
      return pattern.return_type.create_from_value(value)
    else:
      return pattern.return_type.create_undetermined()

class InstanceFunc:
  def __init__(self, func, context):
    self.func = func
    self.context = context
  def __call__(self, *args, **kargs):
    return self.func(self.context, *args, **kargs)

