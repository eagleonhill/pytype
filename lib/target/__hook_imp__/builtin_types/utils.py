from ..type_value import BuiltinType, match
from ..func_value import StubFunc

def addUnaryOperator(c, op, returnType = None):
  if returnType is None: 
    returnType = c
  c.add_builtin_call_pattern(op, [], returnType)

def addBinaryOperator(c, op, returnType = None, otherType = None): 
  if returnType is None: 
    returnType = c
  if otherType is None: 
    otherType = c
  c.add_builtin_call_pattern(op, [otherType], returnType)

def addFunction(c, op, args, returnType, optionalArgs = None):
  c.add_builtin_call_pattern(op, [otherType], returnType, optionalArgs)

def addStubFunction(c, op, func):
  c.attr[op] = StubFunc(func)
