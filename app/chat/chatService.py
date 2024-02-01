from app.db import conn
from datetime import datetime
from app.const import MAX_CHAT, Status, FIRST
from psycopg2.extras import DictCursor


def chatList():
    #TODO jwt에서 유저 id 가져오기
    id = 1

    cursor = conn.cursor(cursor_factory=DictCursor)
    sql = 'SELECT DISTINCT ON ("user_id") "user_id", "msg", "msg_time", "msg_check" \
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
            'target_id': chat['id'],
            'name': user['name'],
            'status': Status.OFFLINE, #TODO socket으로 status 처리
            'birthday': datetime.strftime(user['birthday'], '%Y-%m-%d'),
            'longitude': user['longitude'], #TODO 거리로 줄건지,,%s
            'latitude': user['latitude'],
            'new': chat['msg_check']
        })

    in_cursor.close()
    cursor.close()
    return {
        'message': 'succeed',
        'data': result,
    }, 200


def getMsg(data):
    #TODO jwt에서 유저 id 가져오기
    id = 1
    target_id = data['target_id']
    
    cursor = conn.cursor(cursor_factory=DictCursor)
    sql = 'UPDATE "Chat" SET "msg_new" = False WHERE "user_id" = %s AND "target_id" = %s;'
    cursor.execute(sql, (target_id, id))
    conn.commit()

    if data['msg_id'] == FIRST: #방 클릭
        sql = 'SELECT * FROM "Chat" \
            WHERE ("target_id" = %s AND "user_id" = %s) OR ("user_id" = %s AND "target_id" = %s) \
            ORDER BY "msg_time" DESC \
            LIMIT %s;'
        cursor.execute(sql, (id, target_id, id, target_id, MAX_CHAT))
    else: #방 내부에서 추가 로딩
        sql = 'SELECT * FROM "Chat" \
            WHERE ("target_id" = %s AND "user_id" = %s) OR ("user_id" = %s AND "target_id" = %s) \
                    AND "id" < %s \
            ORDER BY "msg_time" DESC \
            LIMIT %s;'
        cursor.execute(sql, (id, target_id, id, target_id, data['msg_id'], MAX_CHAT))
    
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


def saveChat(data):
    ###############TODO 소켓에서 유저 id 가져오기
    id = 1

    cursor = conn.cursor(cursor_factory=DictCursor)
    sql = 'INSERT INTO "Chat" (user_id, target_id, msg, msg_time, msg_new) VALUES (%s, %s, %s, %s, %s)'
    cursor.execute(sql, (id,
                         data['target_id'],
                         data['msg'],
                         datetime.today(),
                         True))
    conn.commit()
    cursor.close()

    return {
        'message': 'succeed',
    }, 200
