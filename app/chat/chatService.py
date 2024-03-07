from app.db import conn
from datetime import datetime
from app.const import MAX_CHAT, Status, FIRST_CHAT
from psycopg2.extras import DictCursor
from ..history.historyUtils import getFancy
from . import chatUtils
from ..socket.events import check_status


def chatList(id):
    cursor = conn.cursor(cursor_factory=DictCursor)
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
        user = in_cursor.fetchone()

        result.append({
            'target_id': user['id'],
            'name': user['name'],
            'status': check_status(user['id']),
            'birthday': datetime.strftime(user['birthday'], '%Y-%m-%d'),
            'longitude': user['longitude'],
            'latitude': user['latitude'],
            'fancy': getFancy(id, user['id']),
            'new': chat['msg_new']
        })

    in_cursor.close()
    cursor.close()
    return {
        'message': 'succeed',
        'data': result,
    }, 200


def getMsg(data, id):

    #TODO id, target_id가 connected인지 확인 필요
    
    target_id = data['target_id']
    
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
