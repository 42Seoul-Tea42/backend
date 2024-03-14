# from app import app
# from flask import send_from_directory
from app.db import conn
from psycopg2.extras import DictCursor
from . import userUtils as utils
from app.const import MAX_SEARCH, DAYS, DISTANCE, Key, Status, EARTH_RADIUS, KST, PICTURE_DIR
from datetime import datetime, timedelta
import pytz
import app.history.historyUtils as historyUtils
import os
from ..socket import socket_service as socketServ
# from werkzeug.utils import secure_filename

#TODO conn.commit()
#TODO cursor.close() after using cursor result
#TODO update, insert, delete count확인 후 리턴 처리
#TODO with ~ as ~ 내용으로 모두 바꾸기
# db result 접근 전 에러 처리 (user 없을 경우 등)

def login(data):
    cursor = conn.cursor(cursor_factory=DictCursor)
    sql = 'SELECT * FROM "User" WHERE "login_id" = %s;'
    cursor.execute(sql, (data['login_id'], ))
    user = cursor.fetchone()

    if not user:
        cursor.close()
        return {
            'message': 'no such user',
        }, 400
    
    if not utils.isValidPassword(data['pw'], data['login_id'], user['password']):
        cursor.close()
        return {
            'message': 'wrong password',
        }, 400

    sql = 'UPDATE "User" SET "longitude" = %s, "latitude" = %s WHERE "login_id" = %s;'
    cursor.execute(sql, (data['longitude'], data['latitude'], data['login_id']))
    conn.commit()
    cursor.close()

    token = utils.generate_jwt(user['id'])
    refresh = utils.generate_refresh(user['id'])
    return {
        'message': 'succeed',
        'data': {
            'token': token,
            'refresh': refresh,
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
def resetToken(data):
    refresh = data['refresh']
    cursor = conn.cursor(cursor_factory=DictCursor)
    sql = 'SELECT "refresh" FROM "User" WHERE "refresh" = %s;'
    cursor.execute(sql, (refresh, ))
    user = cursor.fetchone()
    if not user:
        cursor.close()
        return {
            'message': 'Unauthorized refresh token',
        }, 401

    cursor.close()
    if utils.check_refresh(refresh):
        token = utils.generate_jwt(id)
        return {
            'message': 'succeed',
            'data': {
                'token': token
            }
        }, 200
    
    return {
        'message': 'Unauthorized refresh token',
    }, 401


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


def profileDetail(data, id):
    target_id = data['target_id']
    if id == target_id:
        return {
            'message': 'cannot check self',
        }, 400
    
    now_kst = datetime.now(pytz.timezone(KST))
    cursor = conn.cursor(cursor_factory=DictCursor)

    #check if target is available
    sql = 'SELECT * FROM "User" WHERE "id" = %s;'
    cursor.execute(sql, (target_id, ))
    db_data = cursor.fetchone()
    if not db_data:
        cursor.close()
        return {
            'message': 'no such user',
        }, 400

    #History.last_view update
    sql = 'SELECT * FROM "History" WHERE "user_id" = %s AND "target_id" = %s;'
    cursor.execute(sql, (id, target_id))
    db_data = cursor.fetchone()

    if db_data: #update
        sql = 'UPDATE "History" SET "last_view" = %s \
                WHERE "user_id" = %s AND "target_id" = %s;'
        cursor.execute(sql, (now_kst, id, target_id))    
    else: #create History && update count_view
        sql = 'INSERT INTO "History" (user_id, target_id, fancy, last_view) \
                                VALUES (%s, %s, %s, %s)'
        cursor.execute(sql, (id, target_id, False, now_kst))
        sql = 'UPDATE "User" SET count_view = COALESCE("count_view", 0) + 1 \
                WHERE "id" = %s'
        cursor.execute(sql, (id, ))
    conn.commit()

    sql = 'SELECT * FROM "User" WHERE "id" = %s;'
    cursor.execute(sql, (target_id, ))
    target = cursor.fetchone()

    result = {
        'login_id': target['login_id'],
        'status': socketServ.check_status(target_id),
        'last_online': target['last_online'],
        'gender': target['gender'],
        'taste': target['taste'],
        'bio': target['bio']
    }
    cursor.close()

    ## (socket) history update alarm
    socketServ.new_history(id)
    
    return {
        'message': 'succeed',
        'data': result
    }, 200


def logout(id):
    #socket 정리 및 last_onlie 업데이트는 handle_disconnect()에서 자동으로 처리될 것

    #refresh token 삭제
    utils.delete_refresh(id)
    
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


def emailStatus(id):
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


def getEmail(id):
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
        

def sendEmail(id):
    cursor = conn.cursor(cursor_factory=DictCursor)
    sql = 'SELECT * FROM "User" WHERE "id" = %s;'
    cursor.execute(sql, (id, ))
    user = cursor.fetchone()

    email = user['email']
    if user['email_check']:
        cursor.close()
        return {
            'message': 'email already verified',
        }, 400
    
    result = {
        'email_check': user['email_check'],
        'profile_check': True if user['gender'] else False,
        'emoji_check': True if user['emoji'] else False,
    }
    cursor.close()

    utils.sendEmail(email, user['email_key'], Key.EMAIL)
    return {
        'message': 'succeed',
        'data': result
    }, 200
        

def changeEmail(data, id):
    if not utils.isValidEmail(data['email']):
        return {
            'message': 'fail: not valid email address',
        }, 400

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
        email_key = utils.createEmailKey(user['login_id'], Key.EMAIL)
        sql = 'UPDATE "User" SET "email" = %s, "email_key" = %s WHERE "id" = %s;'
        cursor.execute(sql, (data['email'], email_key, id))
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
    if key[-1] != str(Key.EMAIL):
        return {
            'message': 'wrong email check key',
        }, 200
    
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
def setting(data, id):
    if not utils.isValidEmail(data['email']):
        return {
            'message': 'fail: not valid email address',
        }, 400

    hashed_pw = utils.hashing(data['pw'], data['login_id'])
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
    cursor.execute(sql, (data['email'], hashed_pw, data['last_name'], data['name'],
                         data['birthday'], data['gender'], data['taste'], data['bio'],
                         tags, hate_tags, emoji, hate_emoji, data['similar'],
                         id))
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
        hashed_pw = utils.hashing(data['pw'], data['login_id'])
        email_key = utils.createEmailKey(data['login_id'], Key.EMAIL)

        cursor = conn.cursor(cursor_factory=DictCursor)
        sql = 'INSERT INTO "User" (email, email_check, email_key, login_id, password, \
                                    name, last_name, birthday, longitude, latitude) \
                            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)'
        #TODO last name not null아니면 처리 필요
        cursor.execute(sql, (data['email'], False, email_key,data['login_id'], hashed_pw,
                             data['name'], data['last_name'], data['birthday'], data['longitude'], data['latitude']))
        conn.commit()
        cursor.close()

    except Exception as e:
        print('failed while create db')
        raise e

    utils.sendEmail(data['email'], email_key, Key.EMAIL)

    return {
        'message': 'succeed',
    }, 200


def setProfile(data, id):
    tags = utils.encodeBit(data['tags'])
    hate_tags = utils.encodeBit(data['hate_tags'])
    print('tag encodeing', tags, hate_tags)

    try:
        cursor = conn.cursor(cursor_factory=DictCursor)
        sql = 'UPDATE "User" SET "gender" = %s, "taste" = %s, "bio" = %s, "tags" = %s, "hate_tags" = %s \
                WHERE "id" = %s;'
        cursor.execute(sql, (data['gender'], data['taste'], data['bio'], tags, hate_tags, id))
        conn.commit()
        cursor.close()
    except Exception as e:
        print('failed while update db')
        raise e

    return {
        'message': 'succeed',
    }, 200


def allowed_file(filename, id):
    if '.' in filename:
        name, extension = filename.rsplit('.', 1)
        if 0 <= int(name) < 5 and extension.lower() in {'png', 'jpg', 'jpeg'}:
            return str(id) + "_" + name + '.' + extension
    return None


def setPicture(data, id):
    if 'images' not in data:
        return { 'message': 'no image part' }, 400
    
    cursor = conn.cursor(cursor_factory=DictCursor)
    sql = 'SELECT "pictures" FROM "User" WHERE "id" = %s;'
    cursor.execute(sql, (id, ))
    user = cursor.fetchone()
    if not user:
        cursor.close()
        return {
            'message': 'no such user',
        }, 400
    
    prev_pictures = set(user['pictures']) #기존 이미지 리스트
    
    # 새 이미지 저장
    images = data['images']
    new_pictures = list()
    error = False
    for image in images:
        filename = None
        if (image.filename == '') or ((filename := allowed_file(image.filename, id)) is None):
            error = True
            continue
        image.save(f'/usr/app/srcs/app/profile/{filename}')
        new_pictures.append(filename)

    if new_pictures:
        sql = f'UPDATE "User" SET "pictures" = ARRAY{tuple(new_pictures)} WHERE "id" = %s;'
        cursor.execute(sql, (id,))

        #필요없는 파일 지우기
        pictures = prev_pictures - set(new_pictures) if prev_pictures else set()
        for file_to_delete in pictures:
            file_path = os.path.join(PICTURE_DIR, file_to_delete)
            try:
                os.remove(file_path)
            except Exception as e:
                print(f"An error occurred(setPicture): {e}")

    if error:
        return {
            'message': 'there was an unexpected error saving image(s)',
        }, 400
    
    return {
        'message': 'succeed',
    }, 200


def getPicture(data):
    target = data['target_id']

    cursor = conn.cursor(cursor_factory=DictCursor)
    sql = 'SELECT "pictures" FROM "User" WHERE "id" = %s;'
    cursor.execute(sql, (target, ))
    user = cursor.fetchone()
    if not user:
        cursor.close()
        return {
            'message': 'no such user',
        }, 400
    
    pictures = user['pictures']
    if not pictures:
        cursor.close()
        return {
            'message': 'no pictures',
        }, 400

    images = []
    for picture in pictures:
        image_path = os.path.join(PICTURE_DIR, picture)
        try:
            if os.path.exists(image_path):
                with open(image_path, 'rb') as img_file:
                    images.append(img_file.read())
        except Exception as e:
            print(f"An error occurred(getPicture): {e}")
    
    #TODO images 잘 가는 지 확인 필요 (특히 형식)
    return {
        'message': 'succeed',
        'data': images
    }, 200


def setLocation(data, id):
    cursor = conn.cursor(cursor_factory=DictCursor)
    sql = 'UPDATE "User" SET "longitude" = %s, "latitude" = %s WHERE "id" = %s;'
    cursor.execute(sql, (data['longitude'], data['latitude'], id))
    conn.commit()
    cursor.close()

    #(socket) 거리 업데이트
    socketServ.update_distance(id, data['longitude'], data['latitude'])
    
    return {
        'message': 'succeed',
    }, 200


def resetPw(data, key):
    if key[-1] != str(Key.PASSWORD):
        return {
            'message': 'wrong password reset key',
        }, 200

    cursor = conn.cursor(cursor_factory=DictCursor)
    sql = 'SELECT * FROM "User" WHERE "email_key" = %s;'
    cursor.execute(sql, (key, ))
    user = cursor.fetchone()
    
    if not user:
        cursor.close()
        return {
            'message': 'no such reset key',
        }, 400

    hashed_pw = utils.hashing(data['pw'], user['login_id'])
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
            'message': 'id_check failed'
        }, 400
    
    if not user['email_check']:
        return {
            'message': 'email_check failed',
        }, 400
    
    email = user['email']
    email_key = utils.createEmailKey(user['login_id'], Key.PASSWORD)

    sql = 'UPDATE "User" SET "email_key" = %s WHERE "login_id" = %s'
    cursor.execute(sql, (email_key, data['login_id']))
    conn.commit()
    cursor.close()

    utils.sendEmail(email, email_key, Key.PASSWORD)

    return {
        'message': 'success',
        'data': {
            'id_check': True,
            'email_check': True
        }
    }, 200


def unregister(id):
    # 유저 및 관련 내용 모두 삭제 => cascade로 진행
        # -> 이렇게 하면 채팅창이 이미 열려있는 경우 등에서 target이 없는 id여서 엄청난 에러폭풍이 예상된다...
        # -> #TODO 없는 유저인 경우 별도 처리 필요하겠다
    
    cursor = conn.cursor(cursor_factory=DictCursor)
    sql = 'DELETE FROM "User" WHERE "id" = %s;'
    cursor.execute(sql, (id, ))
    conn.commit()
    cursor.close()

    return {
        'message': 'succeed',
    }, 200
    
    
# ##### taste
def emoji(data, id):
    emoji = utils.encodeBit(data['emoji'])
    hate_emoji = utils.encodeBit(data['hate_emoji'])

    cursor = conn.cursor(cursor_factory=DictCursor)
    sql = 'UPDATE "User" SET "emoji" = %s, "hate_emoji" = %s, "similar" = %s WHERE "id" = %s;'
    cursor.execute(sql, (emoji, hate_emoji, data['similar'], id))
    conn.commit()
    cursor.close()

    return {
        'message': 'succeed',
    }, 200


# ##### search
def search(data, id):
    
    #TODO 모두 세팅된 유저만 나오게 처리 (회원가입, 사진, 태그, 이모지)

    now_kst = datetime.now(pytz.timezone(KST))
    date_start = now_kst - timedelta(data['min_age'] * DAYS)
    date_end = now_kst - timedelta(data['max_age'] * DAYS)
    tags = utils.encodeBit(data['tags'])
    distance = int(data['distance']) * DISTANCE

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

    sql = 'SELECT * \
            FROM "User" \
            WHERE "id" != %s \
                    AND "User"."id" NOT IN ( \
                            SELECT "target_id" \
                            FROM "Block" \
                            WHERE "user_id" = %s ) \
                    AND "birthday" BETWEEN %s AND %s \
                    AND "count_fancy" / COALESCE("count_view", 1) * 10 >= %s \
                    AND "tags" & %s > 0 \
                    AND ( %s * acos( \
                                cos(radians("latitude")) * cos(radians(%s)) * \
                                cos(radians("longitude" - %s)) + \
                                sin(radians("latitude")) * sin(radians(%s)) \
                            ) \
                        ) < %s \
            ORDER BY "last_online" DESC \
            LIMIT %s;'

    cursor.execute(sql, (id, id,
                         date_end, date_start,
                         data['fame'], tags if tags else -1,
                         EARTH_RADIUS, user['latitude'], user['longitude'], user['latitude'], distance,
                         MAX_SEARCH))
    db_data = cursor.fetchall()
    
    result = []
    for record in db_data:
        result.append({
            'id': record['id'],
            'name': record['name'],
            'last_name': record['last_name'],
            'birthday': datetime.strftime(record['birthday'], '%Y-%m-%d'),
            'distance': utils.get_distance(lat, long, record['latitude'], record['longitude']),
            'fame': record['count_fancy'] / record['count_view'] * 10 if record['count_view'] else 0,
            'tags': utils.decodeBit(record['tags']),
            'fancy': historyUtils.getFancy(id, record['id']),
        })

    cursor.close()
    return {
        'message': 'succeed',
        'data': result,
    }, 200


# ##### report && block
def report(data, id):
    
    #report시 자동 block 처리
    block(data, id)

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

def block(data, id):
    
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

    sql = 'SELECT * FROM "History" WHERE "user_id" = %s AND "target_id" = %s AND "fancy" = True;'
    cursor.execute(sql, (id, data['target_id']))
    #TODO 하기 ["fancy"] 잘 되는지 확인 필요
    history = cursor.fetchone()
    if history:
        sql = 'UPDATE "History" SET "fancy" = False WHERE "user_id" = %s AND "target_id" = %s;'
        cursor.execute(sql, (id, data['target_id']))
        sql = 'UPDATE "User" SET "count_fancy" = "count_fancy" - 1 WHERE "id" = %s;'
        cursor.execute(sql, (data['target_id'], ))

    conn.commit()
    cursor.close()
    return {
        'message': 'succeed',
    }, 200
