import sys
import pandas as pd
import sqlite3
from modulesDB import convert_to_binary

insert_str = "INSERT INTO contacts(name, email, phone, address, photo, birth_date, occupation, notes) " \
             "VALUES(?, ?, ?, ?, ?, ?, ?, ?)"

df = pd.read_excel("insert-contacts.xlsx") # Read the excel file and store it in a pandas Dataframe
df["birth_date"] = df["birth_date"].dt.strftime(r'%Y-%m-%d') # Change date format to text to match database format


# Check if dataframe has more columns than expected
#if len(df.columns) > 8:
#    print("------! The dataframe has more columns than expected. Will try to remove NA columns.")
#    # Drop columns where all values are NA and modify the existing dataframe (inplace=True)
#    df.dropna(axis=1, how="all", inplace=True)
#    # Check if the extra columns have been removed
#    if len(df.columns) > 8:
#        print("------! Could not remove extra columns. Terminating program.")
#        sys.exit()
#    else:
#        print("Successfully removed extra columns and will continue insertion.")


dbConn = sqlite3.connect("contacts.db")
cursor = dbConn.cursor()

# TODO: Account for duplicates
for row in df.itertuples():
    cursor.execute(insert_str, (row.name, row.email, row.phone, row.address, convert_to_binary(row.photo),
                                row.birth_date, row.occupation, row.notes))

# Commit the changes to the table
cursor.connection.commit()


cursor.close()
dbConn.close()
