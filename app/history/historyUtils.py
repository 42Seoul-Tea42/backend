from app.db import conn
from psycopg2.extras import DictCursor
from ..const import Fancy


def getFancy(id, target_id) -> int:
    cursor = conn.cursor(cursor_factory=DictCursor)
    fancy = 0

    sql = 'SELECT "fancy" FROM "History" WHERE "user_id" = %s AND "target_id" = %s;'
    cursor.execute(sql, (id, target_id))
    send = cursor.fetchone()
    #TODO send, recv: True, False 대로 처리되는지 확인 필요
    if send:
        fancy |= Fancy.SEND

    sql = 'SELECT "fancy" FROM "History" WHERE "user_id" = %s AND "target_id" = %s;'
    cursor.execute(sql, (target_id, id))
    recv = cursor.fetchone()
    if recv:
        fancy |= Fancy.RECV

    cursor.close()
    return fancy