from app.db import conn
from . import userUtils as utils
from app.const import MAX_SEARCH, DAYS, DISTANCE, Key
from datetime import datetime, timedelta
import app.history.historyUtils as historyUtils
from psycopg2.extras import DictCursor

# from flask import jsonify


#TODO conn.commit()
#TODO cursor.close() after using cursor result
#TODO update, insert, delete count확인 후 리턴 처리


def login(data):
    login_id = data['login_id']

    cursor = conn.cursor(cursor_factory=DictCursor)
    sql = 'SELECT * FROM "User" WHERE "login_id" = %s;'
    cursor.execute(sql, (login_id, ))
    user = cursor.fetchone()

    if not user:
        cursor.close()
        return {
            'message': 'no such user',
        }, 400
    
    if not utils.isValidPassword(data['pw'], user['password']):
        cursor.close()
        return {
            'message': 'wrong password',
        }, 400

    sql = 'UPDATE "User" SET "longitude" = %s, "latitude" = %s WHERE "login_id" = %s;'
    cursor.execute(sql, (data['longitude'], data['latitude'], login_id)) #TODO check if it works without float()
    conn.commit()
    cursor.close()

    token = utils.createJwt(user['id'])
    return {
        'message': 'succeed',
        'data': {
            'token': f'{token}',
            'id': user['id'],
            'name': user['name'],
            'birthday': datetime.strftime(user['birthday'], '%Y-%m-%d'),
            'email_check': user['email_check'],
            'profile_check': True if user['gender'] else False,
            'emoji_check': True if user['emoji'] else False,
        }
    }, 200


# def kakao():
# return

# def google():
# return


# ##### identify
def checkId(data):
    login_id = data['login_id']
    cursor = conn.cursor(cursor_factory=DictCursor)
    sql = 'SELECT * FROM "User" WHERE "login_id" = %s;'
    cursor.execute(sql, (login_id, ))
    user = cursor.fetchone()
    
    #TODO True, false 확인 필요
    occupied = True if user else False
    cursor.close()
    
    return {
        'message': 'succeed',
        'data': {
            'occupied': occupied
        }
    }, 200
        

# def profile(data):
#     #TODO jwt에서 유저 id 가져오기
#     id = 1

#     cursor = conn.cursor(cursor_factory=DictCursor)
#     sql = 'SELECT * FROM "User" WHERE "id" = %s;'
#     cursor.execute(sql, (data['id'], ))
#     user = cursor.fetchone()

#     fancy = 0
#     in_cursor = conn.cursor(cursor_factory=DictCursor)
#     sql = 'SELECT "fancy" FROM "History" WHERE "user_id" = %s AND "target_id" = %s;'
#     in_cursor.execute(sql, (id, data['id']))
#     send = in_cursor.fetchone()
#     if send:
#         fancy |= send['fancy']

#     sql = 'SELECT "fancy" FROM "History" WHERE "user_id" = %s AND "target_id" = %s;'
#     in_cursor.execute(sql, (data['id'], id))
#     recv = in_cursor.fetchone()
#     if recv:
#         fancy |= recv['fancy']

#     result = {
#         'id': user['id'],
#         'login_id': user['login_id'],
#         'name': user['name'],
#         'birthday': datetime.strftime(user['birthday'], '%Y-%m-%d'),
#         'longitude': user['longitude'],
#         'latitude': user['latitude'],
#         'fame': user['count_fancy'] / user['count_view'] * 10,
#         'tags': utils.decodeBit(user['tags']),
#         'fancy': fancy,
#     },

#     in_cursor.close()
#     cursor.close()
#     return {
#         'message': 'succeed',
#         'data': result #TODO 잘 가는 지 확인 필요
#     }, 200


def profileDetail(data):
    #TODO jwt에서 유저 id 가져오기
    id = 1
    target_id = data['target_id']
    now = datetime.now()

    cursor = conn.cursor(cursor_factory=DictCursor)

    #History.last_view update
    sql = 'SELECT * FROM "History" WHERE "user_id" = %s AND "target_id" = %s;'
    cursor.execute(sql, (id, target_id))
    db_data = cursor.fetchone()

    if db_data: #update
        sql = 'UPDATE "History" SET "last_view" = %s \
                WHERE "user_id" = %s AND "target_id" = %s;'
        cursor.execute(sql, (now, id, target_id))    
    else: #create History && update count_view
        sql = 'INSERT INTO "History" (user_id, target_id, fancy, last_view) \
                                VALUES (%s, %s, %s, %s)'
        cursor.execute(sql, (id, target_id, False, now))
        sql = 'UPDATE "User" SET count_view = count_view + 1 \
                WHERE "id" = %s'
        cursor.execute(sql, (id, ))
    conn.commit()

    sql = 'SELECT * FROM "User" WHERE "id" = %s;'
    cursor.execute(sql, (target_id, ))
    user = cursor.fetchone()

    result = {
        'last_name': user['last_name'],
        'status': user['status'], #TODO status socket 처리
        'last_online': user['last_online'],
        'gender': user['gender'],
        'taste': user['taste']
    }
    cursor.close()
    
    return {
        'message': 'succeed',
        'data': result #TODO 잘 가는 지 확인 필요
    }, 200


def logout():
    #TODO jwt, refresh token 삭제
    #TODO cache, session 삭제
    #TODO socket 정리

    #TODO jwt에서 유저 id 가져오기
    id = 1

    cursor = conn.cursor(cursor_factory=DictCursor)
    sql = 'UPDATE "User" SET "refresh" = %s, last_online = %s WHERE "id" = %s;'
    cursor.execute(sql, (None, datetime.now(), id))
    conn.commit()
    cursor.close()
    return {
        'message': 'succeed',
    }, 200


# ##### email
def checkEmail(data):

    if not utils.isValidEmail(data['email']):
        return {
            'message': 'fail: not valid email address',
        }, 400

    cursor = conn.cursor(cursor_factory=DictCursor)
    sql = 'SELECT * FROM "User" WHERE "email" = %s;'
    cursor.execute(sql, (data['email'], ))
    occupied = True if cursor.fetchone() else False #TODO 잘 되는지 체크 필요
    cursor.close()
    
    return {
        'message': 'succeed',
        'data': {
            #TEST True, false 확인 필요
            'occupied': occupied,
        }
    }, 200


def emailStatus():
    #TODO jwt에서 유저 id 가져오기
    id = 1

    cursor = conn.cursor(cursor_factory=DictCursor)
    sql = 'SELECT * FROM "User" WHERE "id" = %s;'
    cursor.execute(sql, (id, ))
    user = cursor.fetchone()

    result = {
        'email_check': user['email_check'],
        'profile_check': True if user['gender'] else False,
        'emoji_check': True if user['emoji'] else False,
    }
    cursor.close()

    return {
        'message': 'succeed',
        'data': result
    }, 200


def getEmail():
    #TODO jwt에서 유저 id 가져오기
    id = 1

    cursor = conn.cursor(cursor_factory=DictCursor)
    sql = 'SELECT * FROM "User" WHERE "id" = %s;'
    cursor.execute(sql, (id, ))
    email = cursor.fetchone()['email']
    cursor.close()

    return {
        'message': 'succeed',
        'data': {
            'email': email
        }
    }, 200
        

def sendEmail():
    #TODO jwt에서 유저 id 가져오기
    id = 1

    cursor = conn.cursor(cursor_factory=DictCursor)
    sql = 'SELECT * FROM "User" WHERE "id" = %s;'
    cursor.execute(sql, (id, ))
    user = cursor.fetchone()

    email = user['email']
    result = {
        'email_check': user['email_check'],
        'profile_check': True if user['gender'] else False,
        'emoji_check': True if user['emoji'] else False,
    }
    cursor.close()

    #TODO email 보내기
    utils.sendEmail(email, user['email_key'], Key.EMAIL)

    return {
        'message': 'succeed',
        'data': result
    }, 200
        

def changeEmail(data):
    #TODO jwt에서 유저 id 가져오기
    id = 1

    if not utils.isValidEmail(data['email']):
        return {
            'message': 'fail: not valid email address',
        }, 400

    #TODO with ~ as ~ 내용으로 모두 바꾸기
    with conn.cursor(cursor_factory=DictCursor) as cursor:

        #check email_check
        sql = 'SELECT * FROM "User" WHERE "id" = %s;'
        cursor.execute(sql, (id, ))
        user = cursor.fetchone()
        if user['email_check']:
            cursor.close()
            return {
                'message': 'error: cannot change verified email',
            }, 400

        #update
        sql = 'UPDATE "User" SET "email" = %s WHERE "id" = %s;'
        cursor.execute(sql, (data['email'], id))
        conn.commit()

        #send verify email
        utils.sendEmail(data['email'], user['email_key'], Key.EMAIL)

        result = {
            'email_check': False,
            'profile_check': True if user['gender'] else False,
            'emoji_check': True if user['emoji'] else False,
        }
        
        return {
            'message': 'succeed',
            'data': result
        }, 200



    
def registerEmail(key):
    cursor = conn.cursor(cursor_factory=DictCursor)
    sql = 'UPDATE "User" SET "email_check" = %s, "email_key" = %s WHERE "email_key" = %s;'
    cursor.execute(sql, (True, None, key))
    num_rows_updated = cursor.rowcount
    conn.commit()
    cursor.close()

    if num_rows_updated:
        return {
            'message': 'email check succeed',
        }, 200
    
    return {
        'message': 'wrong email check link',
    }, 200


# ##### register && setting
def setting(data):
    #TODO jwt에서 유저 id 가져오기
    id = 1

    if not utils.isValidEmail(data['email']):
        return {
            'message': 'fail: not valid email address',
        }, 400

    tags = utils.encodeBit(data['tags'])
    hate_tags = utils.encodeBit(data['hate_tags'])
    emoji = utils.encodeBit(data['emoji'])
    hate_emoji = utils.encodeBit(data['hate_emoji'])

    cursor = conn.cursor(cursor_factory=DictCursor)
    sql = 'UPDATE "User" SET "email" = %s, "pw" = %s, "last_name" = %s, "name" = %s, \
                            "birthday" = %s, "gender" = %s, "taste" = %s, "bio" = %s,\
                            "tags" = ", "hate_tags" = %s, "emoji" = %s, "hate_emoji" = %s, similar = %s \
            WHERE "id" = %s;'

    #TODO 잘 들어가는 지 확인 필요 (birthday!)
    cursor.execute(sql, (data['email'], data['pw'], data['last_name'], data['name'],
                         data['birthday'], data['gender'], data['taste'], data['bio'],
                         tags, hate_tags, emoji, hate_emoji, data['similar']))
    conn.commit()
    cursor.close()

    return {
        'message': 'succeed',
    }, 200


def register(data):

    if not utils.isValidEmail(data['email']):
        return {
            'message': 'fail: not valid email address',
        }, 400

    try:
        hashed_pw = utils.hashing(data['pw'])
        email_key = utils.createEmailKey(data['login_id'])

        cursor = conn.cursor(cursor_factory=DictCursor)
        sql = 'INSERT INTO "User" (email, email_check, email_key, login_id, password, name, last_name, birthday) \
                            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)'
        cursor.execute(sql, (data['email'], 
                            False,
                            email_key,
                            data['login_id'],
                            hashed_pw,
                            data['name'],
                            data['last_name'], #TODO last name not null아니면 처리 필요
                            data['birthday'])) #TODO date처리 확인 필요

        conn.commit()
        cursor.close()
    except Exception:
        print('failed while create db')
        raise e

    #TODO email 보내기
    utils.sendEmail(data['email'], email_key, Key.EMAIL)

    return {
        'message': 'succeed',
    }, 200


def setProfile(data):
    #TODO jwt에서 유저 id 가져오기
    id = 1

    tags = utils.encodeBit(data['tags'])
    hate_tags = utils.encodeBit(data['hate_tags'])

    try:
        cursor = conn.cursor(cursor_factory=DictCursor)
        sql = 'UPDATE "User" SET "gender" = %s, "taste" = %s, "bio" = %s, "tags" = %s, "hate_tags" = %s WHERE "id" = %s;'
        cursor.execute(sql, (data['gender'], 
                            data['taste'],
                            data['bio'],
                            tags,
                            hate_tags))
        conn.commit()
        cursor.close()
    except Exception as e:
        print('failed while update db')
        raise e

    return {
        'message': 'succeed',
    }, 200


def setPicture(data):
    #TODO picture file 업로드

    return

def setLocation(data):
    #TODO jwt에서 유저 id 가져오기
    id = 1

    cursor = conn.cursor(cursor_factory=DictCursor)
    sql = 'UPDATE "User" SET "longitude" = %s, "latitude" = %s WHERE "id" = %s;'
    cursor.execute(sql, (data['longitude'], data['latitude'], id)) #TODO check if it works without float()
    conn.commit()
    cursor.close()

    return {
        'message': 'succeed',
    }, 200


def resetPw(data, key):
    hashed_pw = utils.hashing(data['pw'])

    cursor = conn.cursor(cursor_factory=DictCursor)
    sql = 'UPDATE "User" SET "password" = %s, "email_key" = %s WHERE "email_key" = %s;'
    cursor.execute(sql, (hashed_pw, None, key))
    conn.commit()
    cursor.close()

    return {
        'message': 'succeed',
    }, 200


def requestReset(data):
    cursor = conn.cursor(cursor_factory=DictCursor)
    sql = 'SELECT * FROM "User" WHERE "login_id" = %s;'
    cursor.execute(sql, (data['login_id'], ))
    user = cursor.fetchone()
    
    if not user:
        return {
            'message': 'failed',
            'data': { 'id_check': False }
        }, 200
    
    if not user['email_check']:
        return {
            'message': 'failed',
            'data': {
                'id_check': True,
                'email_check': False
            }
        }, 200
    
    email = user['email']
    email_key = utils.createEmailKey(user['login_id'])

    sql = 'INSERT INTO "User" (email_key) VALUES (%s) WHERE "login_id" = %s'
    cursor.execute(sql, (email_key, data['login_id']))
    conn.commit()
    cursor.close()

    utils.sendEmail(email, email_key, Key.PASSWORD)

    return {
        'message': 'failed',
        'data': {
            'id_check': True,
            'email_check': True
        }
    }, 200


def unregister():
    # 유저 및 관련 내용 모두 삭제 => cascade로 진행
        # -> 이렇게 하면 채팅창이 이미 열려있는 경우 등에서 target이 없는 id여서 엄청난 에러폭풍이 예상된다...
        # -> #TODO 없는 유저인 경우 별도 처리 필요하겠다
    
    #TODO jwt에서 유저 id 가져오기
    id = 1

    cursor = conn.cursor(cursor_factory=DictCursor)
    sql = 'DELETE FROM "User" WHERE "id" = %s;'
    cursor.execute(sql, (id, ))
    conn.commit()
    cursor.close()

    return {
        'message': 'succeed',
    }, 200
    
    
# ##### taste
def emoji(data):
    #TODO jwt에서 유저 id 가져오기
    id = 1

    emoji = utils.encodeBit(data['emoji'])
    hate_emoji = utils.encodeBit(data['hate_emoji'])

    cursor = conn.cursor(cursor_factory=DictCursor)
    sql = 'UPDATE "User" SET "emoji" = %s, "hate_emoji" = %s, "similar" = %s WHERE "id" = %s;'
    cursor.execute(sql, (emoji, 
                         hate_emoji,
                         data['similar'], #TODO bool 잘 들어가는지 확인
                         id))
    conn.commit()
    cursor.close()

    return {
        'message': 'succeed',
    }, 200


# ##### search
def search(data):
    #TODO jwt에서 유저 id 가져오기
    id = 1

    today = datetime.now()
    date_start = today - timedelta(data['min_age'] * DAYS)
    date_end = today - timedelta(data['max_age'] * DAYS)
    tags = utils.encodeBit(data['tags'])
    distance = int(data['distance']) * DISTANCE

    cursor = conn.cursor(cursor_factory=DictCursor)
    sql = 'SELECT * FROM "User" WHERE "id" = %s;'
    cursor.execute(sql, (id, ))
    user = cursor.fetchone()

    sql = 'SELECT * FROM "User" WHERE "id" != %s AND "User"."id" NOT IN ( \
                                                    SELECT "target_id" \
                                                    FROM "Block" \
                                                    WHERE "user_id" = %s ) AND \
                                    "birthday" BETWEEN %s AND %s \
                                    "count_fancy" / "count_view" * 10 >= %s AND \
                                    "tags" & %s > 0 AND \
                                    earth_distance(ll_to_earth(latitude, longitude), ll_to_earth(%s, %s)) < %s \
            ORDER BY "last_online" DESC \
            LIMIT %s;'
    cursor.execute(sql, (id, id,
                         date_start, date_end,
                         data['fame'],
                         tags,
                         user['latitude'], user['longitude'], distance,
                         MAX_SEARCH))
    db_data = cursor.fetchall()
    result = []
    
    for record in db_data:
        result.append({
            'id': record['id'],
            'login_id': record['login_id'],
            'name': record['name'],
            'birthday': datetime.strftime(record['birthday'], '%Y-%m-%d'),
            'longitude': record['longitude'],
            'latitude': record['latitude'],
            'fame': record['count_fancy'] / record['count_view'] * 10,
            'tags': utils.decodeBit(record['tags']),
            'fancy': historyUtils.getFancy(id, record['id']),
        })

    cursor.close()
    return {
        'message': 'succeed',
        'data': result,
    }, 200


# ##### report && block
def block(data):
    #TODO jwt에서 유저 id 가져오기
    #TODO report에서 불리는 것도 id 잘 가져오는 지 확인 필요
    id = 1

    #TODO 블록유저와 관련된 history 삭제 필요한가%s(block하려면 상세 프로필 확인해야하니까)
    #   -> 그럴 경우 fame rate 재조정이 필요할 것인가%s
    #       -> fame rate는 계속 다시 계산하는거여서 재조정 노필요
    cursor = conn.cursor(cursor_factory=DictCursor)
    sql = 'SELECT * FROM "Block" WHERE "user_id" = %s AND "target_id" = %s'
    cursor.execute(sql, (id, data['target_id']))
    if cursor.fetchone():
        cursor.close()
        return {
            'message': 'fail: cannot block again',
        }, 400

    sql = 'INSERT INTO "Block" (user_id, target_id) VALUES (%s, %s)'
    cursor.execute(sql, (id, data['target_id']))

    sql = 'SELECT * FROM "History" WHERE "user_id" = %s AND "target_id" = %s;'
    cursor.execute(sql, (id, data['target_id']))
    #TODO 하기 ["fancy"] 잘 되는지 확인 필요
    if cursor.fetchone()["fancy"]:
        sql = 'UPDATE "History" SET "fancy" = False WHERE "user_id" = %s AND "target_id" = %s;'
        cursor.execute(sql, (id, data['target_id']))
        sql = 'UPDATE "User" SET "count_fancy" = "count_fancy" - 1 WHERE "id" = %s;'
        cursor.execute(sql, (data['target_id'], ))

    conn.commit()
    cursor.close()
    return {
        'message': 'succeed',
    }, 200


def report(data):
    #TODO jwt에서 유저 id 가져오기
    id = 1

    #report시 자동 block 처리
    block(data)

    cursor = conn.cursor(cursor_factory=DictCursor)
    sql = 'SELECT * FROM "Report" WHERE "user_id" = %s AND "target_id" = %s'
    cursor.execute(sql, (id, data['target_id']))
    if cursor.fetchone():
        cursor.close()
        return {
            'message': 'fail: cannot report again',
        }, 400
    
    sql = 'INSERT INTO "Report" (user_id, target_id, reason, reason_opt) VALUES (%s, %s, %s, %s)'
    cursor.execute(sql, (id, data['target_id'],
                         data['reason'], data['reason_opt']))
    conn.commit()
    cursor.close()
    return {
        'message': 'succeed',
    }, 200

