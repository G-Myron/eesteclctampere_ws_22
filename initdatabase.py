import sqlite3

# method initdb creates eestec-database and creates one table with two columns
# https://www.sqlitetutorial.net/sqlite-python/sqlite-python-select/
def initdb(db='eestec.db'):

    # creating table
    # using connect, sqlite will try to open the file
    conn = sqlite3.connect(db)
    conn.execute("PRAGMA encoding='UTF-8'")
    # cursor allows you to execute sql code
    c = conn.cursor()

    # executing command CREATE TABLE to create table with two columns
    c.execute('CREATE TABLE IF NOT EXISTS data_table('
        'date text,'
        'data integer)')

    # commit saves changes to the database
    conn.commit()
    # finally closing connection
    conn.close()