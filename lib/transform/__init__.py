import ast
from constant_visitor import ConstantVisitor

def transform(source, filename):
  root = ast.parse(source, filename)
  #print ast.dump(root)
  ConstantVisitor().visit(root)
  ast.fix_missing_locations(root)
  #print ast.dump(root)
  return root
