import sqlite3

db=sqlite3.connect("database.db")
cursor = db.cursor()
cursor.execute("""CREATE TABLE IF NOT EXISTS users(
   user TEXT UNIQUE PRIMARY KEY,
   p_number TEXT,
   c_number TEXT);
""")
db.commit()

cursor.execute("""INSERT INTO users(user) VALUES ('oleg');""")
db.commit()



