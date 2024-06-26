from ..db.db import PostgreSQLFactory
from datetime import datetime

from ..utils.const import (
    MAX_HISTORY,
    ProfileList,
    KST,
    Fancy,
    StatusCode,
    FancyOpt,
    Authorization,
    RedisOpt,
    TIME_STR_TYPE,
)
import app.user.userUtils as userUtils
from . import historyUtils as utils
from app.chat import chatUtils
from psycopg2.extras import DictCursor
from ..socket import socketService as socketServ
from werkzeug.exceptions import BadRequest
from ..utils import redisServ


def view_history(id, time_limit, opt):
    # 유저 API 접근 권한 확인
    userUtils.check_authorization(id, Authorization.EMOJI)

    conn = PostgreSQLFactory.get_connection()
    with conn.cursor(cursor_factory=DictCursor) as cursor:

        if opt == ProfileList.FANCY:
            sql = 'SELECT * FROM "History" \
                    WHERE "target_id" = %s AND "fancy" = True AND "fancy_time" < %s \
                    ORDER BY "fancy_time" DESC \
                    LIMIT %s;'

        elif opt == ProfileList.HISTORY:
            sql = 'SELECT * FROM "History" \
                    WHERE "user_id" = %s AND "last_view" < %s \
                    ORDER BY "last_view" DESC \
                    LIMIT %s;'

        elif opt == ProfileList.VISITOR:
            sql = 'SELECT * FROM "History" \
                    WHERE "target_id" = %s AND "last_view" < %s \
                    ORDER BY "last_view" DESC \
                    LIMIT %s;'

        cursor.execute(sql, (id, time_limit, MAX_HISTORY))
        histories = cursor.fetchall()

    result = [
        userUtils.get_target_profile(
            id,
            history["target_id" if opt == ProfileList.HISTORY else "user_id"],
            (
                history["fancy_time"]
                if opt == ProfileList.FANCY
                else history["last_view"]
            ).strftime(TIME_STR_TYPE),
        )
        for history in histories
    ]

    return {
        "profile_list": result,
    }, StatusCode.OK


def check_before_service(id, target_id):
    # 유저 API 접근 권한 확인
    userUtils.check_authorization(id, Authorization.EMOJI)

    if id == target_id:
        raise BadRequest("스스로를 fancy할 수 없습니다.")

    if userUtils.get_user(target_id) is None:
        raise BadRequest("존재하지 않는 유저입니다.")

    # block check
    block_set = redisServ.get_user_info(id, RedisOpt.BLOCK)
    if target_id in block_set:
        raise BadRequest("차단한 유저입니다.")


def fancy(id, target_id):
    check_before_service(id, target_id)

    now_kst = datetime.now(KST)

    conn = PostgreSQLFactory.get_connection()
    with conn.cursor(cursor_factory=DictCursor) as cursor:

        sql = 'SELECT * FROM "History" WHERE "user_id" = %s AND "target_id" = %s;'
        cursor.execute(sql, (id, target_id))
        history = cursor.fetchone()

        if history:  # update
            if history["fancy"]:
                return {
                    "msg": "success",
                }, StatusCode.OK

            sql = 'UPDATE "History" \
                    SET "fancy" = True, "fancy_time" = %s, "last_view" = %s \
                    WHERE "user_id" = %s AND "target_id" = %s;'
            cursor.execute(sql, (now_kst, now_kst, id, target_id))
        else:  # create
            sql = 'INSERT INTO "History" (user_id, target_id, fancy, fancy_time, last_view) \
                                VALUES (%s, %s, %s, %s, %s)'
            cursor.execute(sql, (id, target_id, True, now_kst, now_kst))
        conn.commit()

        userUtils.update_count_fancy(target_id, FancyOpt.ADD)

        if history is None:
            userUtils.update_count_view(target_id)

        if utils.get_fancy_status(id, target_id) == Fancy.CONN:
            socketServ.new_match(id, target_id)

        socketServ.new_fancy(id, target_id)

    return {
        "msg": "success",
    }, StatusCode.OK


def unfancy(id, target_id):
    check_before_service(id, target_id)

    now_kst = datetime.now(KST)

    conn = PostgreSQLFactory.get_connection()
    with conn.cursor(cursor_factory=DictCursor) as cursor:

        sql = 'SELECT * FROM "History" WHERE "user_id" = %s AND "target_id" = %s;'
        cursor.execute(sql, (id, target_id))
        history = cursor.fetchone()

        if history:
            if not history["fancy"]:
                return {
                    "msg": "success",
                }, StatusCode.OK

            sql = 'UPDATE "History" \
                    SET "fancy" = False, "fancy_time" = %s, "last_view" = %s \
                    WHERE "user_id" = %s AND "target_id" = %s;'
            cursor.execute(sql, (now_kst, now_kst, id, target_id))
        else:
            raise BadRequest("잘못된 접근입니다. (fancy기록 없음)")
        conn.commit()

        userUtils.update_count_fancy(target_id, FancyOpt.DEL)

        if utils.get_fancy_status(id, target_id) == Fancy.RECV:
            chatUtils.delete_chat(id, target_id)
            socketServ.unmatch(id, target_id)

        socketServ.new_unfancy(id, target_id)

    return {
        "msg": "success",
    }, StatusCode.OK


def dummy_fancy(id, target_id):
    if id == target_id:
        return {
            "msg": "success",
        }, StatusCode.OK

    now_kst = datetime.now(KST)

    conn = PostgreSQLFactory.get_connection()
    with conn.cursor(cursor_factory=DictCursor) as cursor:

        sql = 'SELECT * FROM "History" WHERE "user_id" = %s AND "target_id" = %s;'
        cursor.execute(sql, (id, target_id))
        history = cursor.fetchone()

        if history:  # update
            if history["fancy"]:
                return {
                    "msg": "success",
                }, StatusCode.OK

            sql = 'UPDATE "History" \
                    SET "fancy" = True, "fancy_time" = %s, "last_view" = %s \
                    WHERE "user_id" = %s AND "target_id" = %s;'
            cursor.execute(sql, (now_kst, now_kst, id, target_id))
        else:  # create
            sql = 'INSERT INTO "History" (user_id, target_id, fancy, fancy_time, last_view) \
                                VALUES (%s, %s, %s, %s, %s)'
            cursor.execute(sql, (id, target_id, True, now_kst, now_kst))
        conn.commit()

        userUtils.update_count_fancy(target_id, FancyOpt.ADD)

        if history is None:
            userUtils.update_count_view(target_id)

        if utils.get_fancy_status(id, target_id) == Fancy.CONN:
            socketServ.new_match(id, target_id)

        socketServ.new_fancy(id, target_id)

    return {
        "msg": "success",
    }, StatusCode.OK


def dummy_unfancy(id, target_id):
    if id == target_id:
        return {
            "msg": "success",
        }, StatusCode.OK

    now_kst = datetime.now(KST)

    conn = PostgreSQLFactory.get_connection()
    with conn.cursor(cursor_factory=DictCursor) as cursor:

        sql = 'SELECT * FROM "History" WHERE "user_id" = %s AND "target_id" = %s;'
        cursor.execute(sql, (id, target_id))
        history = cursor.fetchone()

        if history:
            if not history["fancy"]:
                return {
                    "msg": "success",
                }, StatusCode.OK

            sql = 'UPDATE "History" \
                    SET "fancy" = False, "fancy_time" = %s, "last_view" = %s \
                    WHERE "user_id" = %s AND "target_id" = %s;'
            cursor.execute(sql, (now_kst, now_kst, id, target_id))
        else:
            raise BadRequest("잘못된 접근입니다. (fancy기록 없음)")
        conn.commit()

        userUtils.update_count_fancy(target_id, FancyOpt.DEL)

        if utils.get_fancy_status(id, target_id) == Fancy.RECV:
            chatUtils.delete_chat(id, target_id)
            socketServ.unmatch(id, target_id)

        socketServ.new_unfancy(id, target_id)

    return {
        "msg": "success",
    }, StatusCode.OK
