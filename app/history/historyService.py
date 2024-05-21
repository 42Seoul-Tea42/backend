from ..db.db import PostgreSQLFactory
from datetime import datetime

from ..utils.const import (
    MAX_HISTORY,
    History,
    KST,
    Fancy,
    StatusCode,
    FancyOpt,
    Authorization,
    RedisOpt,
)
import app.user.userUtils as userUtils
from . import historyUtils as utils
from psycopg2.extras import DictCursor
from ..socket import socketService as socketServ
from werkzeug.exceptions import BadRequest
from ..utils import redisServ


def view_history(id, time_limit, opt):
    # 유저 API 접근 권한 확인
    userUtils.check_authorization(id, Authorization.EMOJI)

    conn = PostgreSQLFactory.get_connection()
    with conn.cursor(cursor_factory=DictCursor) as cursor:

        if opt == History.FANCY:
            utils.update_fancy_check(id)

            sql = 'SELECT * FROM "History" \
                    WHERE "target_id" = %s AND "fancy" = True AND "fancy_time" < %s \
                    ORDER BY "fancy_time" DESC \
                    LIMIT %s;'

        elif opt == History.HISTORY:
            sql = 'SELECT * FROM "History" \
                    WHERE "user_id" = %s AND "last_view" < %s \
                    ORDER BY "last_view" DESC \
                    LIMIT %s;'

        cursor.execute(sql, (id, time_limit, MAX_HISTORY))
        histories = cursor.fetchall()

    result = [
        userUtils.get_profile(
            id, history["target_id" if opt == History.HISTORY else "user_id"]
        )
        for history in histories
    ]

    return {
        "profiles": result,
    }, StatusCode.OK


def fancy(data, id):
    # 유저 API 접근 권한 확인
    userUtils.check_authorization(id, Authorization.EMOJI)

    target_id = data["target_id"]
    try:
        target_id = int(target_id)
    except ValueError:
        raise BadRequest("id는 숫자로 제공되어야 합니다.")

    if id == target_id:
        raise BadRequest("스스로를 fancy할 수 없습니다.")

    if userUtils.get_user(target_id) is None:
        raise BadRequest("존재하지 않는 유저입니다.")

    # block check
    block_set = redisServ.get_user_info(id, RedisOpt.BLOCK)
    if target_id in block_set:
        raise BadRequest("차단한 유저입니다.")

    # ban check
    ban_set = redisServ.get_user_info(id, RedisOpt.BAN)
    if target_id in ban_set:
        return StatusCode.OK

    now_kst = datetime.now(KST)

    conn = PostgreSQLFactory.get_connection()
    with conn.cursor(cursor_factory=DictCursor) as cursor:

        sql = 'SELECT * FROM "History" WHERE "user_id" = %s AND "target_id" = %s;'
        cursor.execute(sql, (id, target_id))
        history = cursor.fetchone()

        if history:  # update
            sql = 'UPDATE "History" \
                    SET "fancy" = not "fancy", "fancy_time" = %s, "fancy_check" = False, "last_view" = %s \
                    WHERE "user_id" = %s AND "target_id" = %s;'
            cursor.execute(sql, (now_kst, now_kst, id, target_id))
        else:  # create
            sql = 'INSERT INTO "History" (user_id, target_id, fancy, fancy_time, fancy_check, last_view) \
                                VALUES (%s, %s, %s, %s, %s, %s)'
            cursor.execute(sql, (id, target_id, True, now_kst, False, now_kst))

        # TODO unfancy 잘 돌아가는지 확인 필요
        if history is None or history["fancy"] is None:  # fancy
            userUtils.update_count_fancy(target_id, FancyOpt.ADD)

            if history is None:
                userUtils.update_count_view(target_id)

            if utils.get_fancy(id, target_id) == Fancy.CONN:
                socketServ.new_match(id, target_id)
            else:
                socketServ.new_fancy(id, target_id)

        else:  # unfancy
            userUtils.update_count_fancy(target_id, FancyOpt.DEL)

            if utils.get_fancy(id, target_id) == Fancy.RECV:
                socketServ.unmatch(id, target_id)

        conn.commit()

    return StatusCode.OK
