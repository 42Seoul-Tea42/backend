from app.db import conn
from psycopg2.extras import DictCursor


def getFancy(id, target_id) -> int:
    cursor = conn.cursor(cursor_factory=DictCursor)
    fancy = 0

    sql = 'SELECT "fancy" FROM "History" WHERE "user_id" = %s AND "target_id" = %s;'
    cursor.execute(sql, (id, target_id))
    send = cursor.fetchone()
    if send:
        fancy |= send['fancy']

    sql = 'SELECT "fancy" FROM "History" WHERE "user_id" = %s AND "target_id" = %s;'
    cursor.execute(sql, (target_id, id))
    recv = cursor.fetchone()
    if recv:
        fancy |= recv['fancy']

    cursor.close()
    return fancy