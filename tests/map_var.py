def f(**x):
  print x
a = {'x':3}
b = {'y': '3'}
b.update(a)
print b
f(**a)
