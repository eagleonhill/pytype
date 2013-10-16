from ast import *

class Visitor(NodeTransformer):
  def visit_Module(self, node):
    node.body[0:0] = [
      Import(names=[alias(name='__hook_types__', asname=None)]),
      ImportFrom(
        module='__hook_builtins__', names=[alias(name='*', asname=None)]),
    ]
    self.generic_visit(node)
    return node

  def visit_Num(self, node):
    return self.wrap('NumValue', node)
  def visit_Str(self, node):
    return self.wrap('StringType', node)

  def wrap(self, typename, node):
    return copy_location(Call(
      func=Attribute(value=Name(id='__hook_types__', ctx=Load()),
        attr=typename,
        ctx=Load()),
      args=[node],
      keywords=[],
      ), node)

def transform(source, filename):
  root = parse(source, filename)
  Visitor().visit(root)
  fix_missing_locations(root)
  return root
