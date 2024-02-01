from app.db import conn
from datetime import datetime
from app.const import MAX_HISTORY, History
import app.user.userUtils as userUtils
from . import historyUtils as utils
from psycopg2.extras import DictCursor


def updateFancyCheck(time_limit):
    #전달할 fancy 리스트 fancyCheck = True 처리하기
    cursor = conn.cursor(cursor_factory=DictCursor)
    sql = 'UPDATE "History" SET "fancy_check" = True \
            WHERE "target_id" = %s AND "fancy" = True AND "fancy_time" < %s \
            ORDER BY "fancy_time" DESC \
            LIMIT %s;'
    cursor.execute(sql, (id, time_limit, MAX_HISTORY))
    conn.commit()
    cursor.close()


def viewHistory(data, opt):
    #TODO jwt에서 유저 id 가져오기
    id = 1

    cursor = conn.cursor(cursor_factory=DictCursor)
    time_limit = data['time']

    if opt == History.FANCY:
        updateFancyCheck(time_limit)
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
    db_data = cursor.fetchall()

    result = []
    in_cursor = conn.cursor(cursor_factory=DictCursor)
    for record in db_data:

        sql = 'SELECT * FROM "User" WHERE "id" = %s;'
        in_cursor.execute(sql, (record['user_id'], ))
        user = in_cursor.fetchone()

        result.append({
            'id': record['user_id'],
            'login_id': user['login_id'],
            'name': user['name'],
            'birthday': datetime.strftime(user['birthday'], '%Y-%m-%d'),
            'longitude': user['longitude'],
            'latitude': user['latitude'],
            'fame': userUtils.getFameRate(record['user_id']),
            'tags': userUtils.decodeBit(user['tags']),
            'fancy': utils.getFancy(id, record['user_id']),
        })

    in_cursor.close()
    cursor.close()
    return {
        'message': 'succeed',
        'data': result,
    }, 200


def fancy(data):
    #TODO jwt에서 유저 id 가져오기
    id = 1
    target_id = data['target_id']

    now = datetime.now()
    
    cursor = conn.cursor(cursor_factory=DictCursor)
    sql = 'SELECT * FROM "HISTORY" WHERE "user_id" = %s AND "target_id" = %s;'
    cursor.execute(sql, (id, target_id))
    db_data = cursor.fetchone()
    cur_fancy = db_data['fancy']

    if db_data: #update
        sql = 'UPDATE "History" SET "last_view" = %s, "fancy_time" = %s, "fancy" = %s, "fancy_check" = False \
                WHERE "user_id" = %s AND "target_id" = %s;'
        cursor.execute(sql, (now, now, not cur_fancy,
                             id, target_id))
    else: #create
        sql = 'INSERT INTO "History" (user_id, target_id, fancy, fancy_time, fancy_check, last_view) \
                                VALUES (%s, %s, %s, %s, %s, %s)'
        cursor.execute(sql, (id, target_id, True, now, False, now))

    if cur_fancy: #unfancy
        sql = 'UPDATE "User" SET "count_fancy" = "count_fancy" - 1 WHERE "id" = %s;'
        cursor.execute(sql, (target_id, ))
    else: #fancy
        sql = 'UPDATE "User" SET "count_fancy" = "count_fancy" + 1 WHERE "id" = %s;'
        cursor.execute(sql, (target_id, ))

    conn.commit()
    cursor.close()
    
    return {
        'message': 'succeed',
    }, 200

