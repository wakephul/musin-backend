import sqlite3
from sqlite3 import Error

def create_connection(db_filename):
    conn = None
    try:
        conn = sqlite3.connect(db_filename)
        return conn
    except Error as e:
        print(e)

def close_connection(connection):
    connection.close()