from base import *
from ast import *

class NextLineNode(AST):
  _fields=['value']
  
class BlockVisitor(NodeTransformer):
  def __init__(self):
    self.blockid = 0
  def block_creator(self, node):
    self.blockid += 1
    bid = self.blockid
    return lambda : copy_location(Num(n=bid), node)

  def visit_Return(self, node):
    return copy_location(Expr(value=decorate('return_value', node.value)), node)
  def loop_break(self, node = None):
    p = Expr(value=call_export('loop_break'))
    if node is not None:
      p = copy_location(p, node)
    return p
  def visit_While(self, node):
    """
    while cond:
      stmt1
    else:
      stmt2

    transform to:
    if not do_next_decision(): # Combine this to l.next_start
      l = LoopFrame()
      l.add_start_rev(localcommit()) # Do it in LoopFrame.__init__
      while l.next_start_rev():
        while l.has_more_path():
          with l:
            l.set_start_rev()  # Do it in l.__enter__
            if not cond:
              stmt2
              break
            stmt1
            # Do following in l.__exit__
            l.add_start_rev(localcommit()) 
            if l.loops > C1 and cond is not MustBreak:
              l.merge_revs() # Merge constants with new values to be
                             # undetermined
            if l.loops > C2:
              warning! Shouldn't happen unless type is changed in loop
      l.finalize_decisions() # Create a new decision,
                             #do it in next_start()
      if l has no final rev:
        Warn!! Possibly a dead loop
    
    All break will transfrom to "raise IterationStop"
    If l catch an IterationStop, it adds to final state
    When l enters, revert to start rev.
    When l exits, adds to a new start state if it's different from 
    others before.

    Exact transfrom::
    while do_while(loopid):
      with loop_frame(loopid):  # For catch exceptions
        if cond:
          stmt1
        else:
          stmt2
          break
    """
    self.generic_visit(node)
    bid = self.block_creator(node)
    return copy_location(While(
      test=decorate('do_while', bid()),
      body=[With(
        context_expr=decorate('frame', bid()),
        body=[If(
          test=node.test,
          body=node.body,
          orelse=node.orelse + [self.loop_break(node)],
        )]
      )],
      orelse=[]
    ), node)
  def visit_For(self, node):
    """ 
    for target in iter:
      stmt1
    else:
      stmt2

    transfromed to:
    while do_for(loopid, lambda: iter):
      with loop_frame(loopid):  # For catch exceptions
        try:
          target = for_next(loopid)
        except StopIteration:
          stmt2
          loop_break()
        stmt1
    """ 
    self.generic_visit(node)
    bid = self.block_creator(node)
    return [copy_location(While(
      test=decorate(
        'do_for',
        bid(),
        Lambda(args=arguments(args=[], defaults=[]), body=node.iter)
      ),
      body=[With(
        context_expr=decorate('frame', bid()),
        body=[
          NextLineNode(value=self.reloadlocal()),
          TryExcept(
            body=[Assign(
                targets=[node.target],
                value=decorate('for_next', bid())
            )],
            handlers=[
              ExceptHandler(
                type=Name(id='StopIteration', ctx=Load()),
                body=node.orelse + [self.loop_break(node)]
              )
            ],
            orelse=[]
          ),
        ] + node.body
      )],
      orelse=[]
    ), node),
    NextLineNode(value=self.reloadlocal())]

  def visit_Break(self, node):
    return self.loop_break(node)

  def visit_If(self, node):
    self.generic_visit(node)
    """
    transform block to:
    while do_block(blockid):
      with block(blockid):
        exec '__hook_exports__.loadlocals()' # Force refresh locals and fast
        stmts
    exec '__hook_exports__.loadlocals()'
    """
    blockid = self.block_creator(node)
    return [copy_location(While(
        test=decorate('do_block', blockid()),
        body=[With(
          context_expr=decorate('frame', blockid()),
          body=[
            NextLineNode(value=self.reloadlocal()),
            node,
          ]
        )],
        orelse=[]
      ), node),
      NextLineNode(value=self.reloadlocal()),
    ]
  def reloadlocal(self):
    return Exec(body=Str('__hook_exports__.loadlocals()'))

class NextLineNoVisitor(NodeTransformer):
  def generic_visit(self, node):
    return super(NextLineNoVisitor, self).generic_visit(node)
    for f, v in iter_fields(node):
      if isinstance(v, list):
        while len(v) and isinstance(v[-1], NextLineNode):
          v.pop()
        for i in range(len(v) - 1):
          if isinstance(v[i], ReloadLocal):
            v[i] = copy_location(\
              v[i].value,
              v[i + 1]
            )
    return node
