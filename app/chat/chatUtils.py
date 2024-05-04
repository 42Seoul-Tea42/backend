from backend.app.db.db import conn
from psycopg2.extras import DictCursor
from datetime import datetime
import pytz
from ..utils.const import KST


def get_match_user_list(id) -> set:
    with conn.cursor(cursor_factory=DictCursor) as cursor:
        sql = 'SELECT DISTINCT "target_id" FROM "Chat" WHERE "user_id" = %s;'
        cursor.execute(sql, (id,))
        db_data = cursor.fetchall()

    user_list = set()
    for data in db_data:
        user_list.add(data["target_id"])

    return user_list


def save_chat(id, target_id, message):
    now_kst = datetime.now(pytz.timezone(KST))

    with conn.cursor(cursor_factory=DictCursor) as cursor:
        sql = 'INSERT INTO "Chat" (user_id, target_id, msg, msg_time, msg_new) \
                            VALUES (%s, %s, %s, %s, %s)'
        cursor.execute(sql, (id, target_id, message, now_kst, True))
        conn.commit()


def read_chat(id, target_id):
    with conn.cursor(cursor_factory=DictCursor) as cursor:
        sql = 'UPDATE "Chat" SET "msg_new" = False \
                WHERE "user_id" = %s AND "target_id" = %s;'
        cursor.execute(sql, (target_id, id))
        conn.commit()
