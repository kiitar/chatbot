import optparse
import os.path
import os
import psycopg2

# db env

if 'DATABASE_URL' in os.environ:
  dburl = os.environ['DATABASE_URL']
else:
  dburl = 'postgres://postgres:postgres@103.245.164.59:5405/postgres'

try:
  conn = psycopg2.connect(dburl)
except Exception as e:
  print(e)
  print("unable to connect to the database")

cur = conn.cursor()

def db_select(q, params):
  try:
    cur.execute(q, params)
  except Exception as e:
    print(e)
    print("Cannot execute " + q + ' ' +','.join(params))
    return(['error', e])
  rows = cur.fetchall()
  return rows

def db_exec(q, params):
  try:
    cur.execute(q, params)
  except Exception as e:
    print(e)
    print("Cannot execute " + q + ' ' +','.join(params))
    return(['error', e])
  conn.commit()
  return True