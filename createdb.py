import sqlite3

db = sqlite3.connect('database.db')
db.execute("CREATE TABLE IF NOT EXISTS users(\
	id INTEGER NOT NULL PRIMARY KEY,\
	name TEXT, gender TEXT, photo TEXT, \
    location TEXT, bio TEXT)")

db.execute("INSERT INTO users (name, gender) VALUES ('Kostas', 'Greece')")

db.execute("UPDATE users set gender='BBBOYYY' WHERE name='Myron'")

schema = db.execute("SELECT * FROM users")

[print(i) for i in schema]

db.commit()
db.close()
