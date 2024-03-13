from app.db import conn
from psycopg2.extras import DictCursor
from datetime import datetime
import pytz
from ..const import KST


def get_match_user_list(id) -> set:
    cursor = conn.cursor(cursor_factory=DictCursor)
    
    sql = 'SELECT DISTINCT "target_id" FROM "Chat" WHERE "user_id" = %s;'
    cursor.execute(sql, (id, ))
    db_data = cursor.fetchall()
    
    user_list = set()
    for data in db_data:
        user_list.add(data['target_id'])
    
    cursor.close()
    return user_list


def save_chat(id, target_id, message):
    now_kst = datetime.now(pytz.timezone(KST))
    
    cursor = conn.cursor(cursor_factory=DictCursor)
    sql = 'INSERT INTO "Chat" (user_id, target_id, msg, msg_time, msg_new) VALUES (%s, %s, %s, %s, %s)'
    cursor.execute(sql, (id,
                         target_id,
                         message,
                         now_kst,
                         True))
    conn.commit()
    cursor.close()

    return {
        'message': 'succeed',
    }, 200


def read_chat(id, target_id):
    cursor = conn.cursor(cursor_factory=DictCursor)

    sql = 'UPDATE "Chat" SET "msg_new" = False WHERE "user_id" = %s AND "target_id" = %s;'
    cursor.execute(sql, (target_id, id))
    conn.commit()
    cursor.close()