from base import *
from ast import *

class ConstantVisitor(NodeTransformer):
  def visit_FunctionDef(self, node):
    self.generic_visit(node)
    name = node.args.kwarg
    if name is not None:
      stmt = Assign(
          targets=[Name(id=name, ctx=Store())],
          value=decorate('dict_unkwargs', Name(id=name, ctx=Load()))
      )
      node.body.insert(0, stmt)
    node.decorator_list.insert(0, get_export('TracedFunction'))
    return node
  def visit_Num(self, node):
    return decorate('num_const', node)
  def visit_Str(self, node):
    return decorate('str_const', node)
  def visit_Call(self, node):
    self.generic_visit(node)
    if node.kwargs is not None:
      node.kwargs = decorate('dict_kwargs', node.kwargs)
    return node
  def visit_List(self, node):
    self.generic_visit(node)
    return decorate('list_const', node)

  def visit_Dict(self, node):
    self.generic_visit(node)
    keys = copy_location(Tuple(elts=node.keys, ctx=Load()), node)
    values = copy_location(Tuple(elts=node.keys, ctx=Load()), node)
    return decorate('dict_const', keys, values)
