# ContactsDBandUI
A simple database application to store contacts with a UI to view, manage, and add contacts. The UI is created using Tkinter.

The example contact info and pictures are from www.random-name-generator.com.

## Files
createDB.py: Create a simple SQLite3 database with a "contacts" table -  
                    contacts(id INTEGER PRIMARY KEY NOT NULL, name TEXT NOT NULL, email TEXT, "
                    "phone TEXT, address TEXT, photo BLOB, birth_date TEXT, occupation TEXT, notes TEXT)

excelToDB.py: A simple script to insert the contacts specified in the "insert-contacts.xlsx" template Excel file. The "photo" column must contain the local path and name of the profile photos.

modulesDB.py: Contains all the code for the UI. 

displayDB: A simple script to launch the UI.
