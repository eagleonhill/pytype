import os
TestConstant = False
TestDynamic = False
TestCast = True

# Constant
if TestConstant:
  print False, 1.0 > 1
  print False, 1 < 1
  print True, 1 == 1
  print False, 1 > 2
  print True, 1 < ''
  print False, 1 > ''
  print False, 1 == ''
  print True, 1 < []

if TestDynamic:
  # Dynamic
  y = int(raw_input())
  if y > 4:
    assert y >= 4
    assert y != 4
  elif y > 5:
    assert False
  elif y < 4:
    assert not y > 4
    assert not y >= 4
  else:
    assert y == 4

  x = raw_input()
  if x == '3':
    assert x == '3'
  else:
    assert x != '3'

  z = float(raw_input())
  if z < 3 and z > 3:
    assert False, 'z < 3 and z > 3'

if TestCast:
  x = int(raw_input())
  if x > 3.5:
    assert x > 3
