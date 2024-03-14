from app.db import conn
from datetime import datetime
import pytz
from app.const import MAX_HISTORY, History, KST, Fancy
import app.user.userUtils as userUtils
from . import historyUtils as utils
from psycopg2.extras import DictCursor
from ..socket import socket_service as socketServ


def updateFancyCheck(time_limit, id):
    #전달할 fancy 리스트 fancyCheck = True 처리하기
    cursor = conn.cursor(cursor_factory=DictCursor)
    sql = 'UPDATE "History" SET "fancy_check" = True \
            WHERE "target_id" = %s AND "fancy" = True AND "fancy_time" < %s \
            ORDER BY "fancy_time" DESC \
            LIMIT %s;'
    cursor.execute(sql, (id, time_limit, MAX_HISTORY))
    conn.commit()
    cursor.close()


def viewHistory(data, id, opt):
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

    time_limit = data['time']
    if opt == History.FANCY:
        updateFancyCheck(time_limit, id)
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
        target = in_cursor.fetchone()

        if target:
            result.append({
                'id': target['id'],
                'name': target['name'],
                'last_name': target['last_name'],
                'birthday': datetime.strftime(target['birthday'], '%Y-%m-%d'),
                'distance': userUtils.get_distance(lat, long, target['latitude'], target['longitude']),
                'fame': target['count_fancy'] / target['count_view'] * 10 if target['count_view'] else 0,
                'tags': userUtils.decodeBit(target['tags']),
                'fancy': utils.getFancy(id, target['id']),
            })

    in_cursor.close()
    cursor.close()
    return {
        'message': 'succeed',
        'data': result,
    }, 200


def fancy(data, id):
    target_id = data['target_id']
    if id == int(target_id):
        return {
            'message': 'cannot self-fancy/unfancy',
        }, 400

    now_kst = datetime.now(pytz.timezone(KST))
    
    cursor = conn.cursor(cursor_factory=DictCursor)
    sql = 'SELECT * FROM "History" WHERE "user_id" = %s AND "target_id" = %s;'
    cursor.execute(sql, (id, target_id))
    db_data = cursor.fetchone()
    
    #TODO 업데이트 잘 되는지 (True <-> False) 확인 필요
    if db_data: #update
        sql = 'UPDATE "History" \
                SET "fancy" = %s, "fancy_time" = %s, "fancy_check" = False, "last_view" = %s \
                WHERE "user_id" = %s AND "target_id" = %s;'
        cursor.execute(sql, (not db_data['fancy'], now_kst, now_kst,
                             id, target_id))
    else: #create
        sql = 'INSERT INTO "History" (user_id, target_id, fancy, fancy_time, fancy_check, last_view) \
                                VALUES (%s, %s, %s, %s, %s, %s)'
        cursor.execute(sql, (id, target_id, True, now_kst, False, now_kst))
        sql = 'SELECT * FROM "History" WHERE "user_id" = %s AND "target_id" = %s;'
        cursor.execute(sql, (id, target_id))
        db_data = cursor.fetchone()

    #TODO unfancy 잘 돌아가는지 확인 필요
    if db_data and db_data['fancy']: #fancy
        sql = 'UPDATE "User" SET "count_fancy" = "count_fancy" + 1 WHERE "id" = %s;'
        cursor.execute(sql, (target_id, ))

        if utils.getFancy(id, target_id) == Fancy.CONN:
            socketServ.new_match(id, target_id)
        else:
            socketServ.new_fancy(id, target_id)

    else: #unfancy
        sql = 'UPDATE "User" SET "count_fancy" = "count_fancy" - 1 WHERE "id" = %s;'
        cursor.execute(sql, (target_id, ))

        if utils.getFancy(id, target_id) == Fancy.RECV:
            socketServ.unmatch(id, target_id)

    conn.commit()
    cursor.close()
    
    return {
        'message': 'succeed',
    }, 200

