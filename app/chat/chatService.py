from ..db.db import conn
from ..utils.const import MAX_CHAT, FIRST_CHAT, Fancy, StatusCode, RedisOpt
from psycopg2.extras import DictCursor
from . import chatUtils
from ..history import historyUtils as hisUtils
from ..socket import socketService as socketServ
from ..user import userUtils
from werkzeug.exceptions import Unauthorized, BadRequest, Forbidden
from ...app import chat_collection
from ..utils import redisServ


def chat_list(id):
    user = redisServ.get_user_info(id, RedisOpt.LOCATION)
    if user is None:
        raise Unauthorized("유저 정보를 찾을 수 없습니다.")
    long, lat = user["longitude"], user["latitude"]

    with conn.cursor(cursor_factory=DictCursor) as cursor:

        sql = 'SELECT DISTINCT ON ("user_id") "user_id", "msg", "msg_time", "msg_new" \
                FROM "Chat" \
                WHERE "target_id" = %s \
                ORDER BY "msg_time" DESC;'
        cursor.execute(sql, (id,))
        chatrooms = cursor.fetchall()

        result = []
        for chat in chatrooms:
            target = userUtils.get_user(chat["user_id"])
            picture = userUtils.get_picture(target["picture"][0])
            result.append(
                {
                    "id": target["id"],
                    "name": target["name"],
                    "last_name": target["last_name"],
                    "status": socketServ.check_status(target["id"]),
                    "distance": userUtils.get_distance(
                        lat, long, target["latitude"], target["longitude"]
                    ),
                    "fancy": hisUtils.get_fancy(id, target["id"]),
                    "new": chat["msg_new"],
                    "picture": picture,
                }
            )

    return {
        "chat_list": result,
    }, StatusCode.OK


def get_msg(id, target_id, msg_id):
    if userUtils.get_user(target_id) is None:
        raise BadRequest("유저 정보를 찾을 수 없습니다.")

    if hisUtils.get_fancy(id, target_id) < Fancy.CONN:
        raise Forbidden("매칭된 상대가 아닙니다.")

    with conn.cursor(cursor_factory=DictCursor) as cursor:

        if msg_id == FIRST_CHAT:  # 방 클릭
            # 채팅 읽음 처리
            chatUtils.read_chat(id, target_id)

            sql = 'SELECT * FROM "Chat" \
                WHERE ("target_id" = %s AND "user_id" = %s) OR ("user_id" = %s AND "target_id" = %s) \
                ORDER BY "msg_time" DESC \
                LIMIT %s;'
            cursor.execute(sql, (id, target_id, id, target_id, MAX_CHAT))

        else:  # 방 내부에서 추가 로딩
            sql = 'SELECT * FROM "Chat" \
                WHERE ("target_id" = %s AND "user_id" = %s) OR ("user_id" = %s AND "target_id" = %s) \
                        AND "msg_id" < %s \
                ORDER BY "msg_time" DESC \
                LIMIT %s;'
            cursor.execute(sql, (id, target_id, id, target_id, msg_id, MAX_CHAT))

        chats = cursor.fetchall()
        result = []

        for chat in chats:
            result.append(
                {
                    "msg_id": chat["id"],
                    "sender": chat["user_id"],
                    "msg": chat["msg"],
                    "msg_time": chat["msg_time"],
                    "checked": chat["msg_new"] if chat["user_id"] == id else True,
                }
            )

    return {
        "msg_list": result,
    }, StatusCode.OK
