from backend.app.db.db import conn
from psycopg2.extras import DictCursor
from ..utils.const import Fancy, KST
from datetime import datetime
import pytz


def update_fancy_check(id):
    # 전달할 fancy 리스트 fancyCheck = True 처리하기
    with conn.cursor(cursor_factory=DictCursor) as cursor:
        sql = 'UPDATE "History" SET "fancy_check" = True \
                WHERE "target_id" = %s AND "fancy" = True;'
        cursor.execute(sql, (id,))
        conn.commit()


def get_fancy(id, target_id) -> int:
    fancy = 0

    with conn.cursor(cursor_factory=DictCursor) as cursor:
        sql = 'SELECT "fancy" FROM "History" WHERE "user_id" = %s AND "target_id" = %s;'
        cursor.execute(sql, (id, target_id))
        send = cursor.fetchone()

        # TODO send, recv: True, False 대로 처리되는지 확인 필요
        if send:
            fancy |= Fancy.SEND

        sql = 'SELECT "fancy" FROM "History" WHERE "user_id" = %s AND "target_id" = %s;'
        cursor.execute(sql, (target_id, id))
        recv = cursor.fetchone()
        if recv:
            fancy |= Fancy.RECV

    return fancy


def update_last_view(id, target_id):
    with conn.cursor(cursor_factory=DictCursor) as cursor:
        now_kst = datetime.now(pytz.timezone(KST))

        sql = 'SELECT * FROM "History" WHERE "user_id" = %s AND "target_id" = %s;'
        cursor.execute(sql, (id, target_id))
        history = cursor.fetchone()

        if history:  # update
            sql = 'UPDATE "History" SET "last_view" = %s \
                    WHERE "user_id" = %s AND "target_id" = %s;'
            cursor.execute(sql, (now_kst, id, target_id))

        else:  # create History && update count_view
            from ..user import userUtils

            userUtils.update_count_view(target_id)

            sql = 'INSERT INTO "History" (user_id, target_id, fancy, last_view) \
                                    VALUES (%s, %s, %s, %s)'
            cursor.execute(sql, (id, target_id, False, now_kst))

        conn.commit()


def get_match_list(id) -> set:
    with conn.cursor(cursor_factory=DictCursor) as cursor:
        sql = 'SELECT "target_id" \
                FROM "History" \
                WHERE "user_id" = %s \
                    AND "fancy" = True \
                    AND "target_id" \
                        IN (SELECT "user_id" FROM "History" \
                            WHERE "target_id" = %s AND "fancy" = True);'
        cursor.execute(sql, (id, id))
        match_list = cursor.fetchall()

        return set([item["target_id"] for item in match_list])
