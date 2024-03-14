from app.db import conn
from datetime import datetime
from app.const import MAX_CHAT, FIRST_CHAT, Fancy
from psycopg2.extras import DictCursor
from ..history.historyUtils import getFancy
from . import chatUtils
from ..socket.socket_service import check_status
from ..user.userUtils import get_distance


def chatList(id):
    cursor = conn.cursor(cursor_factory=DictCursor)
    sql = 'SELECT * FROM "User" WHERE "id" = %s;'
    cursor.execute(sql, (id, ))

    user = cursor.fetchone()
    if not user:
        cursor.close()
        return {
            'message': 'no such user',
        }, 400
    
    long, lat = user['longitude'], user['latitude']

    sql = 'SELECT DISTINCT ON ("user_id") "user_id", "msg", "msg_time", "msg_new" \
            FROM "Chat" \
            WHERE "target_id" = %s \
            ORDER BY "msg_time" DESC;'
    cursor.execute(sql, (id, ))
    chatrooms = cursor.fetchall()

    result = []
    in_cursor = conn.cursor(cursor_factory=DictCursor)
    for chat in chatrooms:
        sql = 'SELECT * FROM "User" WHERE "id" = %s;'
        in_cursor.execute(sql, (chat['user_id'], ))
        target = in_cursor.fetchone()

        result.append({
            'id': target['id'],
            'name': target['name'],
            'last_name': target['last_name'],
            'status': check_status(target['id']),
            'distance': get_distance(lat, long, target['latitude'], target['longitude']),
            'fancy': getFancy(id, target['id']),
            'new': chat['msg_new']
        })

    in_cursor.close()
    cursor.close()
    return {
        'message': 'succeed',
        'data': result,
    }, 200


def getMsg(data, id):

    target_id = data['target_id']
    if getFancy(id, target_id) < Fancy.CONN:
        return {
            'message': 'cannot msg to unmatched user',
        }, 400

    cursor = conn.cursor(cursor_factory=DictCursor)

    if data['msg_id'] == FIRST_CHAT: #방 클릭
        #채팅 읽음 처리
        chatUtils.read_chat(id, target_id)
        
        sql = 'SELECT * FROM "Chat" \
            WHERE ("target_id" = %s AND "user_id" = %s) OR ("user_id" = %s AND "target_id" = %s) \
            ORDER BY "msg_time" DESC \
            LIMIT %s;'
        cursor.execute(sql, (id, target_id, id, target_id, MAX_CHAT))

    else: #방 내부에서 추가 로딩
        sql = 'SELECT * FROM "Chat" \
            WHERE ("target_id" = %s AND "user_id" = %s) OR ("user_id" = %s AND "target_id" = %s) \
                    AND "msg_time" < %s \
            ORDER BY "msg_time" DESC \
            LIMIT %s;'
        cursor.execute(sql, (id, target_id, id, target_id, data['msg_time'], MAX_CHAT))
    
    chats = cursor.fetchall()
    result = []

    for chat in chats:
        result.append({
            'msg_id': chat['id'],
            'sender': chat['user_id'],
            'msg': chat['msg'],
            'msg_time': chat['msg_time'],
            'checked': chat['msg_new'] if chat['user_id'] == id else True
        })

    cursor.close()
    return {
        'message': 'succeed',
        'data': result,
    }, 200
