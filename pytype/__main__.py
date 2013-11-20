import os
import sys
import tempfile
from .transform import transform
from .traced_frame import TracedFrame, FunctionDecision
from codegen import to_source
from . import hook_builtins

if not sys.argv[1:] or sys.argv[1] in ("--help", "-h"):
  print "usage: pdb.py scriptfile [arg] ..."
  sys.exit(2)

mainpyfile = sys.argv[1]     # Get script filename
if not os.path.exists(mainpyfile):
  print 'Error:', mainpyfile, 'does not exist'
  sys.exit(1)

del sys.argv[0]         # Hide "pytype.py" from argument list

# Replace pdb's dir with script's dir in front of module search path.
sys.path[0] = os.path.dirname(mainpyfile)

exc = transform(open(mainpyfile).read(), mainpyfile)

exc = to_source(exc, '  ', True)
tmpf, path = tempfile.mkstemp(suffix='.py', text=True)
os.fdopen(tmpf, 'w').write(exc)
mainpyfile = path
print exc

mod = compile(exc, mainpyfile, 'exec')
result = FunctionDecision()
frame = TracedFrame(result, topmost = True)

try:
  while frame.next_path():
    g = hook_builtins.get_globals('__main__')
    with frame:
      exec mod in g
  frame.result.dump_exceptions(hide_internal=True)
finally:
  os.remove(path)
