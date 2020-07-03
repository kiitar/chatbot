import os
if 'DATABASE_URL' in os.environ:
  dburl = os.environ['DATABASE_URL']
else:
  dburl = 'postgres://postgres:postgres@103.245.164.59:5405/postgres'

f = open('yoyo.ini.template', "r")
lines = f.read()
lines = lines.split("\n")
with open('yoyo.ini', "w") as o_f:
  for line in lines:
    ll = line.split("=")
    k = ll[0].strip()
    if k == 'database':
      l = 'database = ' + dburl + "\n"
      o_f.write(l)
    else:
      o_f.write(line + "\n")