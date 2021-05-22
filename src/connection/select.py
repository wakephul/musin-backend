import sqlite3
from sqlite3 import Error

def select_rows(conn, select_sql):
    try:
        cur = conn.cursor()
        cur.execute(select_sql)
        rows = cur.fetchall()
        return rows
    except Error as e:
        print(e)

