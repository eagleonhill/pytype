import os
import sys
from lib.transform import transform

if not sys.argv[1:] or sys.argv[1] in ("--help", "-h"):
  print "usage: pdb.py scriptfile [arg] ..."
  sys.exit(2)

mainpyfile = sys.argv[1]     # Get script filename
if not os.path.exists(mainpyfile):
  print 'Error:', mainpyfile, 'does not exist'
  sys.exit(1)

del sys.argv[0]         # Hide "pdb.py" from argument list

# Replace pdb's dir with script's dir in front of module search path.
sys.path[0] = os.path.dirname(mainpyfile)
sys.path.append(os.path.join(os.path.dirname(__file__), 'lib', 'target'))

from __hook_imp__.traced_frame import TracedFrame
exc = transform(open(mainpyfile).read(), mainpyfile)
mod = compile(exc, mainpyfile, 'exec')
frame = TracedFrame(None)
while frame.next_path():
  with frame:
    exec mod
frame.result.dump_exceptions()
