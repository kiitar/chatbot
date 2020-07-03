from yoyo import step

def do_step(conn):
  cursor = conn.cursor()
  # train_set
  sql = "CREATE SEQUENCE public.train_set_id_seq " + \
    "AS integer " + \
    "START WITH 1 " + \
    "INCREMENT BY 1 " + \
    "NO MINVALUE " + \
    "NO MAXVALUE " + \
    "CACHE 1;"
  cursor.execute(sql)
  sql = "CREATE TABLE public.train_set (" + \
    "id integer DEFAULT nextval('public.train_set_id_seq'::regclass) NOT NULL PRIMARY KEY," + \
    "message character(255) NOT NULL," + \
    "intent character(255)," + \
    "keywords character(255) NOT NULL" + \
    ");"
  cursor.execute(sql)
  sql = "CREATE INDEX message_idx ON public.train_set USING btree (message);"
  cursor.execute(sql)
  # users
  sql = "CREATE SEQUENCE public.user_id_seq " + \
    "START WITH 1 " + \
    "INCREMENT BY 1 " + \
    "NO MINVALUE " + \
    "NO MAXVALUE " + \
    "CACHE 1;"
  cursor.execute(sql)
  sql = "CREATE TABLE public.users (" + \
    "id integer DEFAULT nextval('public.user_id_seq'::regclass) NOT NULL PRIMARY KEY," + \
    "username character(255) NOT NULL," + \
    "password character(255)" + \
    ");"
  cursor.execute(sql)
  # word_intent
  sql = "CREATE SEQUENCE public.word_intent_id_seq " + \
    "START WITH 1 " + \
    "INCREMENT BY 1 " + \
    "NO MINVALUE " + \
    "NO MAXVALUE " + \
    "CACHE 1;"
  cursor.execute(sql)
  sql = "CREATE TABLE public.word_intent (" + \
    "id integer DEFAULT nextval('public.word_intent_id_seq'::regclass) NOT NULL PRIMARY KEY," + \
    "word character(255) NOT NULL," + \
    "intent character(255)" + \
    ");"
  cursor.execute(sql)
  sql = "CREATE INDEX word_intent_word_idx ON public.word_intent USING btree (word);"
  cursor.execute(sql)

def rollback_step(conn):
  cursor = conn.cursor()
  sql = "drop table train_set"
  cursor.execute(sql)
  sql = "drop table word_intent"
  cursor.execute(sql)
  sql = "drop table users"
  cursor.execute(sql)
  sql = "drop sequence train_set_id_seq"
  cursor.execute(sql)
  sql = "drop sequence user_id_seq"
  cursor.execute(sql)
  sql = "drop sequence word_intent_id_seq"
  cursor.execute(sql)

step(do_step, rollback_step)
