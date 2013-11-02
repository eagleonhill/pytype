from ast import *

class Visitor(NodeTransformer):
  def visit_FunctionDef(self, node):
    self.generic_visit(node)
    name = node.args.kwarg
    if name is not None:
      stmt = Assign(
          targets=[Name(id=name, ctx=Store())],
          value=self.decorate('dict_unkwargs', Name(id=name, ctx=Load()))
      )
      node.body.insert(0, stmt)
    node.decorator_list.insert(0, self.get_export('TracedFunction'))
    return node
  def visit_Num(self, node):
    return self.decorate('num_const', node)
  def visit_Str(self, node):
    return self.decorate('str_const', node)
  def visit_Call(self, node):
    self.generic_visit(node)
    if node.kwargs is not None:
      node.kwargs = self.decorate('dict_kwargs', node.kwargs)
    return node
  def visit_List(self, node):
    self.generic_visit(node)
    return self.decorate('list_const', node)

  def visit_Dict(self, node):
    self.generic_visit(node)
    keys = copy_location(Tuple(elts=node.keys, ctx=Load()), node)
    values = copy_location(Tuple(elts=node.keys, ctx=Load()), node)
    return self.decorate('dict_const', keys, values)

  def decorate(self, typename, *nodes):
    return copy_location(Call(
      func=self.get_export(typename),
      args=list(nodes),
      keywords=[],
      ), nodes[0])
  def get_export(self, name):
    return Attribute(value=Name(id='__hook_exports__', ctx=Load()),
        attr=name,
        ctx=Load())

def transform(source, filename):
  root = parse(source, filename)
  #print dump(root)
  Visitor().visit(root)
  fix_missing_locations(root)
  #print dump(root)
  return root
