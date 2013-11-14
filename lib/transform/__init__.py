import ast
from constant_visitor import ConstantVisitor
from block_visitor import BlockVisitor, NextLineNoVisitor
import sys

def transform(source, filename):
  root = ast.parse(source, filename)
  #print ast.dump(root)
  root = ConstantVisitor().visit(root)
  root = BlockVisitor().visit(root)
  root = NextLineNoVisitor().visit(root)
  root = ast.fix_missing_locations(root)
  #print ast.dump(root, include_attributes=True)
  return root
