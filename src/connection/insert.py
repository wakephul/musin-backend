import sqlite3
from sqlite3 import Error

def insert_row(conn, insert_row_sql, list_to_insert):
    try:
        cur = conn.cursor()
        cur.execute(insert_row_sql, list_to_insert)
        conn.commit()
        return cur.lastrowid
    except Error as e:
        print(e)