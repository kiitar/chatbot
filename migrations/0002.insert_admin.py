from yoyo import step

def do_step(conn):
  cursor = conn.cursor()
  cursor.execute("insert into users (username, password) values (%s, %s)",
      ('admin', '$6$rounds=656000$smn60vA1UPp59D/S$vatw4.HqfGnQ9NyaapIxscLEW5esZeJY3yGTKKCJdl0g0buO8ap.KrYEcDFXMCbTN/OBatia4wVzNcwfCyuBS1'))

def rollback_step(conn):
  cursor = conn.cursor()
  cursor.execute("delete from users where username = %s ", ('admin',))

step(do_step, rollback_step)