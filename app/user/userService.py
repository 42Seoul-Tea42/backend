from flask import make_response, jsonify
from app.db import conn
from psycopg2.extras import DictCursor
import psycopg2
from . import userUtils as utils
from app.const import (
    MAX_SEARCH,
    DISTANCE,
    Key,
    KST,
    PICTURE_DIR,
    Oauth,
    Gender,
    Tags,
    StatusCode,
    MAX_AGE,
    MIN_AGE,
    MAX_DISTANCE,
    MIN_FAME,
    MAX_FAME,
    MAX_PICTURE_AMOUNT,
)
from datetime import datetime
import pytz
import app.history.historyUtils as historyUtils
import os
from ..socket import socket_service as socketServ
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    set_access_cookies,
    set_refresh_cookies,
    unset_jwt_cookies,
)
from app import redis_client
import base64

# TODO conn.commit()
# TODO update, insert, delete count확인 후 리턴 처리

# TODO with ~ as ~ 내용으로 모두 바꾸기
# with conn.cursor(cursor_factory=DictCursor) as cursor:
# db result 접근 전 에러 처리 (user 없을 경우 등)


def login(data):
    login_id = data["login_id"].lower()
    user = utils.get_user_by_login_id(login_id)
    if not user:
        return {
            "message": "존재하지 않는 유저입니다.",
        }, StatusCode.BAD_REQUEST

    # [TEST] login-pw
    if not utils.is_valid_password(data["pw"], login_id, user["password"]):
        return {
            "message": "wrong password",
        }, StatusCode.FORBIDDEN

    access_token = create_access_token(identity=user["id"])
    refresh_token = create_refresh_token(identity=user["id"])

    response = make_response(
        jsonify(
            {
                "id": user["id"],
                "name": user["name"],
                "last_name": user["last_name"],
                "age": user["age"],
                "email_check": user["email_check"],
                "profile_check": True if user["gender"] else False,
                "emoji_check": True if user["emoji"] is not None else False,
                "oauth": user["oauth"],
            }
        ),
        StatusCode.OK,
    )
    response.headers["Content-Type"] = "application/json"
    set_access_cookies(response=response, encoded_access_token=access_token)
    set_refresh_cookies(response=response, encoded_refresh_token=refresh_token)

    # jwt_redis.set(refresh_token, user_id, ex=timedelta(days=14))
    return response


def login_check(id):
    user = utils.get_user(id)
    if not user:
        return {
            "message": "존재하지 않는 유저입니다.",
        }, StatusCode.UNAUTHORIZED

    response = make_response(
        jsonify(
            {
                "email_check": user["email_check"],
                "profile_check": True if user["gender"] else False,
                "emoji_check": True if user["emoji"] is not None else False,
            }
        ),
        StatusCode.OK,
    )
    response.headers["Content-Type"] = "application/json"
    return response


def login_kakao(login_id):
    user = utils.get_user_by_login_id(login_id)
    if not user:
        return {
            "message": "존재하지 않는 유저입니다.",
        }, StatusCode.BAD_REQUEST

    access_token = create_access_token(identity=user["id"])
    refresh_token = create_refresh_token(identity=user["id"])

    response = make_response(
        jsonify(
            {
                "Location": os.environ.get("DOMAIN"),
                "id": user["id"],
                "name": user["name"],
                "last_name": user["last_name"],
                "age": user["age"],
                "email_check": user["email_check"],
                "profile_check": True if user["gender"] else False,
                "emoji_check": True if user["emoji"] is not None else False,
                "oauth": user["oauth"],
            }
        ),
        StatusCode.REDIRECTION,
    )
    response.headers["Content-Type"] = "application/json"  # JSON 형식 응답
    set_access_cookies(response=response, encoded_access_token=access_token)
    set_refresh_cookies(response=response, encoded_refresh_token=refresh_token)

    return response


# def google():
# return


# ##### identify
# def resetToken(data):
#     id = data['id']
#     refresh = data['refresh']
#     cursor = conn.cursor(cursor_factory=DictCursor)
#     sql = 'SELECT "refresh" FROM "User" WHERE "refresh" = %s AND "id" = %s;'
#     cursor.execute(sql, (refresh, id))
#     user = cursor.fetchone()
#     if not user:
#         cursor.close()
#         return {
#             'message': 'Unauthorized refresh token',
#         }, 401

#     cursor.close()
#     if utils.check_refresh(refresh):
#         token = utils.generate_jwt(id)
#         return {
#             'message': 'succeed',
#             'data': {
#                 'token': token
#             }
#         }, 200

#     return {
#         'message': 'Unauthorized refresh token',
#     }, 401


def check_id(login_id):
    login_id = login_id.lower()
    if not utils.is_valid_login_id(login_id):
        return {"occupied": True}, StatusCode.BAD_REQUEST

    with conn.cursor(cursor_factory=DictCursor) as cursor:

        sql = 'SELECT * FROM "User" WHERE "login_id" = %s;'
        cursor.execute(sql, (login_id,))
        user = cursor.fetchone()

        return {"occupied": True if user else False}, StatusCode.OK


# # ##### email
def check_email(email):

    if not utils.is_valid_email(email):
        return {
            "message": "올바르지 않은 이메일 형식입니다.",
        }, StatusCode.BAD_REQUEST

    with conn.cursor(cursor_factory=DictCursor) as cursor:

        sql = 'SELECT * FROM "User" WHERE "email" = %s;'
        cursor.execute(sql, (email,))
        user = cursor.fetchone()

        return {"occupied": True if user else False}, StatusCode.OK


def email_status(id):
    user = utils.get_user(id)
    if not user:
        return {
            "message": "존재하지 않는 유저입니다.",
        }, StatusCode.UNAUTHORIZED

    return {
        "email_check": user["email_check"],
        "profile_check": True if user["gender"] else False,
        "emoji_check": True if user["emoji"] is not None else False,
    }, StatusCode.OK


def get_email(id):
    user = utils.get_user(id)
    if not user:
        return {
            "message": "존재하지 않는 유저입니다.",
        }, StatusCode.UNAUTHORIZED

    return {"email": user["email"]}, StatusCode.OK


def change_email(data, id):
    if not utils.is_valid_email(data["email"]):
        return {
            "message": "유효하지 않은 이메일 형식입니다.",
        }, StatusCode.BAD_REQUEST

    user = utils.get_user(id)
    if not user:
        return {
            "message": "존재하지 않는 유저입니다.",
        }, StatusCode.UNAUTHORIZED

    if user["email_check"]:
        return {
            "message": "이미 인증된 메일입니다.",
        }, StatusCode.BAD_REQUEST

    with conn.cursor(cursor_factory=DictCursor) as cursor:
        # update
        email_key = utils.create_email_key(user["login_id"], Key.EMAIL)
        sql = 'UPDATE "User" SET "email" = %s, "email_key" = %s WHERE "id" = %s;'
        cursor.execute(sql, (data["email"], email_key, id))
        conn.commit()

    # send verify email
    utils.send_email(data["email"], user["email_key"], Key.EMAIL)

    return {
        "email_check": False,
        "profile_check": True if user["gender"] else False,
        "emoji_check": True if user["emoji"] is not None else False,
    }, StatusCode.OK


def resend_email(id):
    user = utils.get_user(id)
    if not user:
        return {
            "message": "존재하지 않는 유저입니다.",
        }, StatusCode.UNAUTHORIZED

    email = user["email"]
    if user["email_check"]:
        return {
            "message": "이미 인증된 메일입니다.",
        }, StatusCode.BAD_REQUEST

    utils.send_email(email, user["email_key"], Key.EMAIL)
    return {
        "email_check": user["email_check"],
        "profile_check": True if user["gender"] else False,
        "emoji_check": True if user["emoji"] is not None else False,
    }, StatusCode.OK


def verify_email(key):
    if key[-1] != str(Key.EMAIL):
        return {
            "message": "유효하지 않은 인증키입니다.",
        }, StatusCode.FORBIDDEN

    with conn.cursor(cursor_factory=DictCursor) as cursor:
        sql = 'UPDATE "User" SET "email_check" = %s, "email_key" = %s WHERE "email_key" = %s;'
        cursor.execute(sql, (True, None, key))
        num_rows_updated = cursor.rowcount
        conn.commit()

    if num_rows_updated:
        return StatusCode.OK

    return {
        "message": "유효하지 않은 인증키입니다.",
    }, StatusCode.FORBIDDEN


# # ##### register && setting
def setting(data, id, images):
    user = utils.get_user(id)
    if not user:
        return {
            "message": "존재하지 않는 유저입니다.",
        }, StatusCode.UNAUTHORIZED

    # 업데이트할 항목 정리
    update_fields = {}
    if data.get("email", None) and user["email"] != data["email"]:
        if not utils.is_valid_email(data["email"]):
            return {
                "message": "유효하지 않은 이메일 형식입니다.",
            }, StatusCode.BAD_REQUEST
        update_fields["email"] = data["email"]
    if user["oauth"] == Oauth.NONE and data.get("pw", None):
        if not utils.is_valid_new_password(data["pw"]):
            return {
                "message": "안전하지 않은 비밀번호입니다.",
            }, StatusCode.BAD_REQUEST
        update_fields["pw"] = utils.hashing(data["pw"], data["login_id"])
    if data.get("last_name", None):
        update_fields["last_name"] = data["last_name"]
    if data.get("name", None):
        update_fields["name"] = data["name"]
    if data.get("age", None):
        update_fields["age"] = data["age"]
    if data.get("gender", None):
        update_fields["gender"] = data["gender"]
    if data.get("taste", None):
        update_fields["taste"] = data["taste"]
    if data.get("bio", None):
        update_fields["bio"] = data["bio"]
    if data.get("tags", None):
        update_fields["tags"] = utils.encodeBit(data["tags"])
    if data.get("hate_tags", None):
        update_fields["hate_tags"] = utils.encodeBit(data["hate_tags"])
    if data.get("prefer_emoji", None):
        update_fields["prefer_emoji"] = utils.encodeBit(data["prefer_emoji"])
    if data.get("hate_emoji", None):
        update_fields["hate_emoji"] = utils.encodeBit(data["hate_emoji"])
    if data.get("similar", None):
        update_fields["similar"] = data["similar"]
    if images:
        # 이전 프로필 사진 지우기
        pictures = user["pictures"]
        for file_to_delete in pictures:
            file_path = os.path.join(PICTURE_DIR, file_to_delete)
            try:
                os.remove(file_path)
            except Exception as e:
                print(f"An error occurred(setPicture): {e}")
                pass
        update_fields["pictures"] = images

    if not update_fields:
        return {"message": "업데이트 내용이 없습니다."}, StatusCode.BAD_REQUEST

    try:
        with conn.cursor(cursor_factory=DictCursor) as cursor:
            set_statements = ", ".join(
                [f'"{key}" = %s' for key in update_fields.keys()]
            )
            sql = f'UPDATE "User" SET {set_statements} WHERE "id" = %s;'
            cursor.execute(sql, tuple(update_fields.values()) + (id,))

            if "email" in update_fields:
                sql = f'UPDATE "User" SET "email_check" = %s WHERE "id" = %s;'
                cursor.execute(sql, tuple(update_fields.values()) + (False, id))

            conn.commit()

    except psycopg2.Error as e:
        conn.rollback()
        if isinstance(e, psycopg2.errors.UniqueViolation):
            return {"message": "이미 등록된 이메일입니다."}, StatusCode.BAD_REQUEST
        else:
            raise e

    if "email" in update_fields:
        logout(id)

    return StatusCode.OK


# TODO [TEST] dummy data
def register_dummy(data):
    try:
        hashed_pw = utils.hashing(data["pw"], data["login_id"])
        now_kst = datetime.now(pytz.timezone(KST))
        pictures = ["1_0.png"]

        with conn.cursor(cursor_factory=DictCursor) as cursor:
            sql = 'INSERT INTO "User" (login_id, password, oauth, \
                                        email, email_check, name, last_name, pictures, \
                                        age, last_online, longitude, latitude, \
                                        gender, taste, bio, tags, hate_tags, emoji, hate_emoji, "similar") \
                                VALUES (%s, %s, %s, \
                                        %s, %s, %s, %s, %s, \
                                        %s, %s, %s, %s, \
                                        %s, %s, %s, %s, %s, %s, %s, %s)'
            cursor.execute(
                sql,
                (
                    data["login_id"],
                    hashed_pw,
                    Oauth.NONE,
                    data["email"],
                    True,
                    data["name"],
                    data["last_name"],
                    pictures,
                    data["age"],
                    now_kst,
                    data["longitude"],
                    data["latitude"],
                    Gender.FEMALE,
                    Gender.ALL,
                    "자기소개입니다",
                    98,
                    2024,
                    33296,
                    16384,
                    True,
                ),
            )
            conn.commit()

    except Exception as e:
        conn.rollback()
        print("/user/register: failed while create db")
        raise e


def save_pictures(id, files):
    if files is None: return []
    
    images = []
    try:
        for idx, image_data in enumerate(files):
            image_info, encoded_data = image_data.split(",", 1)

            extension = utils.get_extention(image_info)
            decoded_data = base64.b64decode(encoded_data)

            filename = f"{id}_{idx}_{datetime.now().strftime("%Y%m%d%H%M%S")}.{extension}"
            
            # 파일 저장
            file_path = os.path.join(PICTURE_DIR, filename)
            with open(file_path, 'wb') as f:
                f.write(decoded_data)

            # 저장된 파일명 리스트에 추가
            images.append(filename)

        # for i in range(MAX_PICTURE_AMOUNT):
        #     image = files.get(f"{i}", None)
        #     if image:
        #         images.append(utils.save_uploaded_file(image))
        #     else:
        #         break
    except Exception as e:
        #저장된 사진 삭제하기
        for image_to_delete in images:
            file_path = os.path.join(PICTURE_DIR, image_to_delete)
            try:
                os.remove(file_path)
            except Exception as e:
                print(f"An error occurred(setPicture): {e}")
                pass
        raise e

    return images


def set_profile(data, id, images):
    user = utils.get_user(id)
    if not user:
        return {
            "message": "존재하지 않는 유저입니다.",
        }, StatusCode.UNAUTHORIZED

    if user["gender"] is not None:
        return {
            "message": "이미 프로필이 설정되어 있습니다.",
        }, StatusCode.BAD_REQUEST

    update_fields = {
        "age": data["age"],
        "gender": data["gender"],
        "taste": data["taste"],
        "bio": data["bio"],
        "tags": utils.encodeBit(data["tags"]),
        "hate_tags": utils.encodeBit(data["hate_tags"]),
        "pictures": images,
    }

    with conn.cursor(cursor_factory=DictCursor) as cursor:
        set_statements = ", ".join([f'"{key}" = %s' for key in update_fields.keys()])
        sql = f'UPDATE "User" SET {set_statements} WHERE "id" = %s;'
        cursor.execute(sql, tuple(update_fields.values()) + (id,))
        conn.commit()

    return StatusCode.OK


def register(data):
    if not utils.is_valid_email(data["email"]):
        return {
            "message": "유효하지 않은 이메일 형식입니다.",
        }, StatusCode.BAD_REQUEST

    if not utils.is_valid_login_id(data["login_id"]):
        return {
            "message": "이미 사용 중인 로그인 아이디입니다.",
        }, StatusCode.BAD_REQUEST

    login_id = data["login_id"].lower()
    hashed_pw = utils.hashing(data["pw"], login_id)
    email_key = utils.create_email_key(login_id, Key.EMAIL)

    try:
        with conn.cursor(cursor_factory=DictCursor) as cursor:
            sql = 'INSERT INTO "User" (email, email_check, email_key, login_id, password, \
                                        name, last_name, oauth) \
                                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)'
            cursor.execute(
                sql,
                (
                    data["email"],
                    False,
                    email_key,
                    login_id,
                    hashed_pw,
                    data["name"],
                    data["last_name"],
                    Oauth.NONE,
                ),
            )
            conn.commit()

    except psycopg2.Error as e:
        conn.rollback()
        if isinstance(e, psycopg2.errors.UniqueViolation):
            return {"message": "이미 등록된 이메일입니다."}, StatusCode.BAD_REQUEST
        else:
            raise e

    utils.send_email(data["email"], email_key, Key.EMAIL)

    return StatusCode.OK


def register_kakao(data):
    with conn.cursor(cursor_factory=DictCursor) as cursor:
        sql = 'INSERT INTO "User" (email, email_check, login_id, name, oauth) \
                            VALUES (%s, %s, %s, %s, %s)'
        cursor.execute(
            sql, (data["email"], True, data["login_id"], data["name"], Oauth.KAKAO)
        )
        conn.commit()


def profile_detail(id, target_id):
    target = utils.get_user(target_id)
    if not target:
        return {"message": "존재하지 않는 유저입니다."}, StatusCode.BAD_REQUEST

    # History.last_view update
    historyUtils.update_last_view(id, target_id)

    ## (socket) history update alarm
    socketServ.new_history(id)

    return {
        "login_id": target["login_id"],
        "status": socketServ.check_status(target_id),
        "last_online": target["last_online"],
        "taste": target["taste"],
        "bio": target["bio"],
    }, StatusCode.OK


def logout(id):
    # socket 정리 및 last_onlie 업데이트는 handle_disconnect()에서 자동으로 처리될 것

    # redis에서 refresh token 삭제
    # utils.delete_refresh(id)
    # jwt_redis.delete(request.cookies.get('refresh_token_cookie'))

    # jwt token 캐시에서 삭제
    response = make_response("", StatusCode.OK)
    unset_jwt_cookies(response)
    return response


# # def setLocation(data, id):
# #     cursor = conn.cursor(cursor_factory=DictCursor)
# #     sql = 'UPDATE "User" SET "longitude" = %s, "latitude" = %s WHERE "id" = %s;'
# #     cursor.execute(sql, (data['longitude'], data['latitude'], id))
# #     conn.commit()
# #     cursor.close()

# #     #(socket) 거리 업데이트
# #     socketServ.update_distance(id, data['longitude'], data['latitude'])

# #     return {
# #         'message': 'succeed',
# #     }, 200


def find_login_id(email):
    with conn.cursor(cursor_factory=DictCursor) as cursor:

        sql = 'SELECT * FROM "User" WHERE "email" = %s;'
        cursor.execute(sql, (email,))
        user = cursor.fetchone()
        if not user:
            return {
                "message": "이메일이 존재하지 않습니다.",
            }, StatusCode.BAD_REQUEST

        if user["oauth"] != Oauth.NONE:
            return {
                "message": "소셜 로그인 사용자입니다.",
            }, StatusCode.BAD_REQUEST

        return {"login_id": utils.blur_login_id(user["login_id"])}, StatusCode.OK


def request_reset(login_id):
    login_id = login_id.lower()

    user = utils.get_user_by_login_id(login_id)
    if not user:
        return {"message": "없는 로그인 id입니다."}, StatusCode.BAD_REQUEST

    if not user["email_check"]:
        return {
            "message": "인증되지 않은 이메일입니다.",
        }, StatusCode.FORBIDDEN

    email_key = utils.create_email_key(login_id, Key.PASSWORD)

    with conn.cursor(cursor_factory=DictCursor) as cursor:
        sql = 'UPDATE "User" SET "email_key" = %s WHERE "login_id" = %s;'
        cursor.execute(sql, (email_key, login_id))
        conn.commit()

    utils.send_email(user["email"], email_key, Key.PASSWORD)

    return {"email_check": True}, StatusCode.OK


def reset_pw(data, key):
    if key[-1] != str(Key.PASSWORD):
        return {
            "message": "잘못된 key입니다.",
        }, StatusCode.FORBIDDEN

    if not data["pw"]:
        return {
            "message": "변경할 비밀번호를 입력해주세요.",
        }, StatusCode.BAD_REQUEST

    with conn.cursor(cursor_factory=DictCursor) as cursor:
        sql = 'SELECT * FROM "User" WHERE "email_key" = %s;'
        cursor.execute(sql, (key,))

        user = cursor.fetchone()
        if not user:
            return {
                "message": "잘못된 key입니다.",
            }, StatusCode.FORBIDDEN

        hashed_pw = utils.hashing(data["pw"], user["login_id"])
        sql = 'UPDATE "User" SET "password" = %s, "email_key" = %s WHERE "email_key" = %s;'
        cursor.execute(sql, (hashed_pw, None, key))
        conn.commit()

    return StatusCode.OK


def unregister(id):

    logout(id)
    socketServ.unregister(id)

    # TODO 모두 잘 삭제되는지 및 채팅창 에러 안뜨는지 확인 필요
    with conn.cursor(cursor_factory=DictCursor) as cursor:
        sql = 'DELETE FROM "User" WHERE "id" = %s CASCADE;'
        cursor.execute(sql, (id,))
        conn.commit()

    return StatusCode.OK


# # ##### taste
def set_emoji(data, id):
    user = utils.get_user(id)
    if not user:
        return {
            "message": "존재하지 않는 유저입니다.",
        }, StatusCode.UNAUTHORIZED

    if user["emoji"] is not None:
        return {
            "message": "이미 설정된 이모지입니다.",
        }, StatusCode.BAD_REQUEST

    emoji = utils.encodeBit(data["emoji"])
    hate_emoji = utils.encodeBit(data["hate_emoji"])

    with conn.cursor(cursor_factory=DictCursor) as cursor:
        sql = 'UPDATE "User" \
                SET "emoji" = %s, "hate_emoji" = %s, "similar" = %s \
                WHERE "id" = %s;'
        cursor.execute(sql, (emoji, hate_emoji, data["similar"], id))
        conn.commit()

    return StatusCode.OK


# ##### search
def search(data, id):
    tags = utils.encodeBit(data["tags"]) if data.get("tags", None) else Tags.ALL
    distance = (
        int(data["distance"]) * DISTANCE if data.get("distance", None) else MAX_DISTANCE
    )
    fame = data["fame"] if data.get("fame", None) else MIN_FAME
    min_age = data["min_age"] if data.get("min_age", None) else MIN_AGE
    max_age = data["max_age"] if data.get("max_age", None) else MAX_AGE

    user = utils.get_user(id)
    if not user:
        return {
            "message": "존재하지 않는 유저입니다.",
        }, StatusCode.UNAUTHORIZED
    long, lat = user["longitude"], user["latitude"]

    with conn.cursor(cursor_factory=DictCursor) as cursor:
        sql = 'SELECT * FROM ( \
                            SELECT *, \
                                ST_Distance( \
                                    ST_MakePoint("longitude", "latitude"), \
                                    ST_MakePoint(%s, %s) \
                                ) AS distance \
                            FROM "User" \
                        ) AS user_distance \
                WHERE "id" != %s \
                        AND "id" NOT IN ( \
                                SELECT "target_id" \
                                FROM "Block" \
                                WHERE "user_id" = %s ) \
                        AND "emoji" IS NOT NULL \
                        AND "age" BETWEEN %s AND %s \
                        AND "count_fancy"::float / COALESCE("count_view", 1) * %s >= %s \
                        AND "tags" & %s > 0 \
                        AND distance <= %s \
                ORDER BY "last_online" DESC, distance ASC \
                LIMIT %s;'

        cursor.execute(
            sql,
            (
                long,
                lat,
                id,
                id,
                min_age,
                max_age,
                MAX_FAME,
                fame,
                tags,
                distance,
                MAX_SEARCH,
            ),
        )
        db_data = cursor.fetchall()

        result = [utils.get_profile(id, target["id"]) for target in db_data]
        return {
            "profiles": result,
        }, StatusCode.OK


# ##### report && block
def report(data, id):

    if id == int(data["target_id"]):
        return {
            "message": "스스로를 신고할 수 없습니다.",
        }, StatusCode.FORBIDDEN

    target = utils.get_user(data["target_id"])
    if not target:
        return {
            "message": "존재하지 않는 유저입니다.",
        }, StatusCode.BAD_REQUEST

    # report시 자동 block 처리
    block(data, id)

    target_id = data.get("target_id", None)
    reason = data.get("reason", None)
    reason_opt = data.get("reason_opt", None)
    if not target_id or not reason:
        return {
            "message": "신고할 대상과 사유를 입력해주세요.",
        }, StatusCode.BAD_REQUEST

    with conn.cursor(cursor_factory=DictCursor) as cursor:
        sql = 'SELECT * FROM "Report" WHERE "user_id" = %s AND "target_id" = %s'
        cursor.execute(sql, (id, data["target_id"]))
        if cursor.fetchone():
            return {
                "message": "이미 신고한 유저입니다.",
            }, StatusCode.BAD_REQUEST

        sql = 'INSERT INTO "Report" (user_id, target_id, reason, reason_opt) \
                            VALUES (%s, %s, %s, %s)'
        cursor.execute(sql, (id, target_id, reason, reason_opt))
        conn.commit()

    return StatusCode.OK


def block(data, id):
    if id == int(data["target_id"]):
        return {
            "message": "스스로를 block할 수 없습니다.",
        }, StatusCode.FORBIDDEN

    target = utils.get_user(data["target_id"])
    if not target:
        return {
            "message": "존재하지 않는 유저입니다.",
        }, StatusCode.BAD_REQUEST

    with conn.cursor(cursor_factory=DictCursor) as cursor:
        sql = 'SELECT * FROM "Block" WHERE "user_id" = %s AND "target_id" = %s'
        cursor.execute(sql, (id, data["target_id"]))
        if cursor.fetchone():
            return {
                "message": "이미 블록한 유저입니다.",
            }, StatusCode.BAD_REQUEST

        sql = 'INSERT INTO "Block" (user_id, target_id) VALUES (%s, %s)'
        cursor.execute(sql, (id, data["target_id"]))

        sql = 'SELECT * FROM "History" WHERE "user_id" = %s AND "target_id" = %s AND "fancy" = True;'
        cursor.execute(sql, (id, data["target_id"]))
        history = cursor.fetchone()
        # TODO 하기 ["fancy"] 잘 되는지 확인 필요
        if history:
            sql = 'UPDATE "History" SET "fancy" = False WHERE "user_id" = %s AND "target_id" = %s;'
            cursor.execute(sql, (id, data["target_id"]))
            sql = 'UPDATE "User" SET "count_fancy" = "count_fancy" - 1 WHERE "id" = %s;'
            cursor.execute(sql, (data["target_id"],))

        conn.commit()

    return StatusCode.OK
