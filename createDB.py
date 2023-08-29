import sqlite3

db = sqlite3.connect("contacts.db")
db.execute("CREATE TABLE IF NOT EXISTS contacts(id INTEGER PRIMARY KEY NOT NULL, name TEXT NOT NULL, email TEXT, "
          "phone TEXT, address TEXT, photo BLOB, birth_date TEXT, occupation TEXT, notes TEXT)")


# for row in db.execute("SELECT name, email, phone, address, birth_date, occupation, notes FROM contacts"):
#     print(row)


db.close()
