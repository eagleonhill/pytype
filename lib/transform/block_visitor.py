from base import *
from ast import *

class ReloadLocal(AST):
  _fields=[]
  _attributes=[]
  
class BlockVisitor(NodeTransformer):
  def __init__(self):
    self.blockid = 0
  def visit_If(self, node):
    self.generic_visit(node)
    return self.gen_block(node)
  def reloadlocal(self):
    return Exec(body=Str('__hook_exports__.loadlocals()'))
  def generic_visit(self, node):
    super(BlockVisitor, self).generic_visit(node)
    for f, v in iter_fields(node):
      if isinstance(v, list):
        while len(v) and isinstance(v[-1], ReloadLocal):
          v.pop()
        for i in range(len(v) - 1):
          if isinstance(v[i], ReloadLocal):
            v[i] = copy_location(\
              Exec(body=Str('__hook_exports__.loadlocals()')),
              v[i + 1]
            )
    return node

  def gen_block(self, node):
    """
    transform block to:
    while do_block(blockid):
      with block(blockid):
        exec '__hook_exports__.loadlocals()' # Force refresh locals and fast
        stmts
    exec '__hook_exports__.loadlocals()'
    """
    self.blockid += 1
    blockid = lambda : copy_location(Num(n=self.blockid), node)
    return [copy_location(While(
        test=decorate('do_block', blockid()),
        body=[With(
          context_expr=decorate('frame', blockid()),
          body=[
            copy_location(self.reloadlocal(), node),
            node,
          ]
        )],
        orelse=[]
      ), node),
      ReloadLocal()
    ]

  def visit_Return(self, node):
    return decorate('return_value', node.value)
