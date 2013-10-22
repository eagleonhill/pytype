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

  def visit_FunctionDef(self, node):
    self.generic_visit(node)
    name = node.args.kwarg
    if name is not None:
      stmt = Assign(
          targets=[Name(id=name, ctx=Store())],
          value=self.wrap('dict_unkwargs', Name(id=name, ctx=Load()))
      )
      node.body.insert(0, stmt)
    return node
  def visit_Num(self, node):
    return self.wrap('num_const', node)
  def visit_Str(self, node):
    return self.wrap('str_const', node)
  def visit_Call(self, node):
    self.generic_visit(node)
    if node.kwargs is not None:
      node.kwargs = self.wrap('dict_kwargs', node.kwargs)
    return node
  def visit_List(self, node):
    self.generic_visit(node)
    return self.wrap('list_const', node)

  def visit_Dict(self, node):
    self.generic_visit(node)
    keys = copy_location(Tuple(elts=node.keys, ctx=Load()), node)
    values = copy_location(Tuple(elts=node.keys, ctx=Load()), node)
    return self.wrap('dict_const', keys, values)

  def wrap(self, typename, *nodes):
    return copy_location(Call(
      func=Attribute(value=Name(id='__hook_types__', ctx=Load()),
        attr=typename,
        ctx=Load()),
      args=list(nodes),
      keywords=[],
      ), nodes[0])

def transform(source, filename):
  root = parse(source, filename)
  #print dump(root)
  Visitor().visit(root)
  fix_missing_locations(root)
  #print dump(root)
  return root
