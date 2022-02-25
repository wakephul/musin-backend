def create_support_table():
    return " \
        CREATE TABLE IF NOT EXISTS support ( \
            id integer PRIMARY KEY AUTOINCREMENT \
        ); \
    "
def select_last_value(table, column, value):
    return " \
        SELECT * FROM " + table + "." + column + " \
        ORDER BY " + column + " DESC LIMIT 1 ; \
    "

def insert_new_value(table, column, value):
    return " \
        INSERT INTO " + table + "(" + column + ") \
        VALUES(" + value + ") \
        ; \
    "