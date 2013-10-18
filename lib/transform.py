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
    return self.wrap('num_const', node)
  def visit_Str(self, node):
    return self.wrap('str_const', node)
  def visit_List(self, node):
    self.generic_visit(node)
    return self.wrap('list_const', node)

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
  #print dump(root)
  Visitor().visit(root)
  fix_missing_locations(root)
  #print dump(root)
  return root
