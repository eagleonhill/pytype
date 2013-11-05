import ast

def decorate(typename, *nodes):
  return ast.copy_location(ast.Call(
    func=get_export(typename),
    args=list(nodes),
    keywords=[],
    ), nodes[0])

def get_export(name):
  return ast.Attribute(value=ast.Name(id='__hook_exports__', ctx=ast.Load()),
      attr=name,
      ctx=ast.Load())
