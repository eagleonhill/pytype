import ast

def decorate(name, *nodes):
  return ast.copy_location(call_export(name, *nodes), nodes[0])

def call_export(name, *args):
  return ast.Call(
    func=get_export(name),
    args=list(args),
    keywords=[],
    )

def get_export(name):
  return ast.Attribute(value=ast.Name(id='__hook_exports__', ctx=ast.Load()),
      attr=name,
      ctx=ast.Load())
