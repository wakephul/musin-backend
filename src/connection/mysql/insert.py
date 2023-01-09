# from pymysql import cursors

def insert_row(conn, query, list_to_insert):
    try:
        with conn.cursor() as cursor:
            cursor = conn.cursor()
            cursor.execute(query, list_to_insert)
            conn.commit()
            return cursor.lastrowid
    except Exception as e:
        print(e)
        return False