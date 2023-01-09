# from pymysql import cursors

def select_rows(conn, query, where_params=[]):
    try:
        with conn.cursor() as cursor:
            cursor.execute(query, where_params)
            response = cursor.fetchall()
            return response
    except Exception as e:
        print(e)
        return False

