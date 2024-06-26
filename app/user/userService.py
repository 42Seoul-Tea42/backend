from flask import make_response, jsonify, request
from werkzeug.exceptions import Unauthorized, BadRequest, Forbidden
import os, base64
from datetime import datetime, timedelta
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    set_access_cookies,
    set_refresh_cookies,
    unset_jwt_cookies,
    get_jwt,
    get_jti,
)
from ..utils.const import (
    MAX_SEARCH,
    Key,
    KST,
    PICTURE_DIR,
    Oauth,
    Gender,
    Tags,
    MAX_PICTURE_AMOUNT,
    StatusCode,
    RedisOpt,
    DEFAULT_PICTURE,
    RedisSetOpt,
    Authorization,
    Report,
    AGE_GAP,
    AREA_DISTANCE,
    MAX_SUGGEST,
    TIME_DETAIL_PAGE_STR_TYPE,
    MAX_FAME
)
from ..db.db import PostgreSQLFactory
from psycopg2.extras import DictCursor
from . import userUtils as utils
import app.history.historyUtils as historyUtils
from ..socket import socketService as socketServ
from ..utils import redisServ, redisBlockList
from ..chat import chatUtils


# TODO update, insert, delete count확인 후 리턴 처리

# db result 접근 전 에러 처리 (user 없을 경우 등)


def login(data):
    user = utils.get_user_by_login_id(data["login_id"])
    if not user:
        raise BadRequest("존재하지 않는 유저입니다.")

    if not utils.matched_password(data["pw"], user["password"]):
        raise BadRequest("잘못된 비밀번호입니다.")

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
    
    #JWT 토큰 생성 및 쿠키 설정
    access_token = create_access_token(identity=user["id"])
    set_access_cookies(response, access_token, max_age=int(os.getenv("ACCESS_TIME"))*60)

    redis_user = redisServ.get_user_info(id, RedisOpt.LOGIN)
    if redis_user and redis_user["email"]:
        #기 로그인 유저
        refresh_token = redisServ.get_refresh_token_by_id(user["id"])
    else:
        #신규 로그인 유저
        refresh_token = create_refresh_token(identity=user["id"])

        #IP기반 위치 정보 업데이트
        user["latitude"], user["longitude"] = utils.get_location_by_ip(
            ip_address=request.headers.get("X-Forwarded-For", request.remote_addr)
        )
        utils.update_location(user["id"], user["latitude"], user["longitude"])

        #Redis에 유저 정보 저장
        user["refresh_token"] = refresh_token
        user["refresh_jti"] = get_jti(refresh_token)
        redisServ.set_user_info(user)
    
    set_refresh_cookies(response, refresh_token, max_age=int(os.getenv("REFRESH_TIME"))*60*60*24)

    return response


def login_check(id):
    #Redis에서 유저 정보 가져오기
    redis_user = redisServ.get_user_info(id, RedisOpt.LOGIN)
    
    if redis_user is None or redis_user['email'] is None:
        raise Unauthorized("유저 정보를 찾을 수 없습니다.")

    response = make_response(
        jsonify(
            {
                "email_check": True if redis_user["email_check"] == RedisSetOpt.SET else False,
                "profile_check": True if redis_user["profile_check"] == RedisSetOpt.SET else False,
                "emoji_check": True if redis_user["emoji_check"] == RedisSetOpt.SET else False
            }
        ),
        StatusCode.OK,
    )
    return response


def login_oauth(login_id):
    user = utils.get_user_by_login_id(login_id)
    if not user:
        raise BadRequest("존재하지 않는 유저입니다.")

    response = make_response(
        jsonify(
            {
                "id": user["id"],
                "name": user["name"],
                "last_name": user["last_name"],
                "age": user["age"],
                "email_check": True,
                "profile_check": True if user["gender"] else False,
                "emoji_check": True if user["emoji"] is not None else False,
                "oauth": user["oauth"],
            }
        ),
        StatusCode.OK,
    )

    #JWT 토큰 생성 및 쿠키 설정
    access_token = create_access_token(identity=user["id"])
    refresh_token = create_refresh_token(identity=user["id"])
    set_access_cookies(response, access_token, max_age=int(os.getenv("ACCESS_TIME"))*60)
    set_refresh_cookies(response, refresh_token, max_age=int(os.getenv("REFRESH_TIME"))*60*60*24)
    
    #IP기반 위치 정보 업데이트
    user["latitude"], user["longitude"] = utils.get_location_by_ip(
        ip_address=request.headers.get("X-Forwarded-For", request.remote_addr)
    )
    utils.update_location(user["id"], user["latitude"], user["longitude"])

    #Redis에 유저 정보 저장
    user["refresh_jti"] = get_jti(refresh_token)
    redisServ.set_user_info(user)

    return response


# def google():
# return


def check_id(login_id):
    conn = PostgreSQLFactory.get_connection()
    with conn.cursor(cursor_factory=DictCursor) as cursor:

        sql = 'SELECT * FROM "User" WHERE "login_id" = %s;'
        cursor.execute(sql, (login_id,))
        user = cursor.fetchone()
        if user is not None:
            raise BadRequest("이미 존재하는 아이디입니다.")
        
        return {
            "msg": "success",
        }, StatusCode.OK


# # ##### email
def check_email(email):
    conn = PostgreSQLFactory.get_connection()
    with conn.cursor(cursor_factory=DictCursor) as cursor:

        sql = 'SELECT * FROM "User" WHERE "email" = %s;'
        cursor.execute(sql, (email,))
        user = cursor.fetchone()

        if user is not None:
            raise BadRequest("이미 존재하는 이메일입니다.")
        
        return {
            "msg": "success",
        }, StatusCode.OK


def get_email(id):
    redis_user = redisServ.get_user_info(id, RedisOpt.LOGIN)
    if redis_user is None or redis_user['email'] is None:
        raise Unauthorized("유저 정보를 찾을 수 없습니다.")
    
    if redis_user["email_check"] == RedisSetOpt.SET:
        raise Forbidden("이미 인증된 메일입니다.")

    return {"email": redis_user["email"]}, StatusCode.OK


def change_email(id, email):
    redis_user = redisServ.get_user_info(id, RedisOpt.LOGIN)
    if redis_user is None or redis_user['email'] is None:
        raise Unauthorized("유저 정보를 찾을 수 없습니다.")

    if redis_user["email_check"] == RedisSetOpt.SET:
        raise Forbidden("이미 인증된 메일입니다.")
    
    if redis_user["email"] == email:
        raise BadRequest("기존과 동일한 이메일입니다.")

    email_key = utils.create_email_key(Key.EMAIL)
    conn = PostgreSQLFactory.get_connection()
    with conn.cursor(cursor_factory=DictCursor) as cursor:
        # update
        sql = 'UPDATE "User" SET "email" = %s, "email_key" = %s WHERE "id" = %s;'
        cursor.execute(sql, (email, email_key, id))
        conn.commit()
        
    #Redis 업데이트
    redisServ.update_user_info(id, {"email": email})

    if os.getenv("PYTEST") == "True":
        return {
            "email_check": False,
            "profile_check": True if redis_user["profile_check"] == RedisSetOpt.SET else False,
            "emoji_check": True if redis_user["emoji_check"] == RedisSetOpt.SET else False,
            "key": email_key,
        }, StatusCode.OK
        
    # send verify email
    try:
        utils.send_email(email, email_key, Key.EMAIL)
    except Exception:
        pass

    return {
        "email_check": False,
        "profile_check": True if redis_user["profile_check"] == RedisSetOpt.SET else False,
        "emoji_check": True if redis_user["emoji_check"] == RedisSetOpt.SET else False
    }, StatusCode.OK


def resend_email(id):
    redis_user = redisServ.get_user_info(id, RedisOpt.LOGIN)
    if redis_user is None or redis_user['email'] is None:
        raise Unauthorized("유저 정보를 찾을 수 없습니다.")
    
    if redis_user["email_check"] == RedisSetOpt.SET:
        raise Forbidden("이미 인증된 메일입니다.")
    
    email = redis_user["email"]
    email_key = utils.get_user(id)["email_key"]

    if os.getenv("PYTEST") == "True":
        return {
            "email_check": False,
            "profile_check": True if redis_user["profile_check"] == RedisSetOpt.SET else False,
            "emoji_check": True if redis_user["emoji_check"] == RedisSetOpt.SET else False,
            "key": email_key,
        }, StatusCode.OK

    try:
        utils.send_email(email, email_key, Key.EMAIL)
    except Exception:
        pass

    return {
        "email_check": False,
        "profile_check": True if redis_user["profile_check"] == RedisSetOpt.SET else False,
        "emoji_check": True if redis_user["emoji_check"] == RedisSetOpt.SET else False,
    }, StatusCode.OK


def verify_email(key):
    if key[-1] != str(Key.EMAIL):
        raise BadRequest("유효하지 않은 인증키입니다.")

    conn = PostgreSQLFactory.get_connection()
    with conn.cursor(cursor_factory=DictCursor) as cursor:
        sql = 'SELECT "id" FROM "User" WHERE "email_key" = %s;'
        cursor.execute(sql, (key,))
        user = cursor.fetchone()
        if not user:
            raise BadRequest("유효하지 않은 인증키입니다.")

        id = user["id"]
        
        sql = 'UPDATE "User" SET "email_check" = %s, "email_key" = %s WHERE "email_key" = %s;'
        cursor.execute(sql, (True, None, key))
        num_rows_updated = cursor.rowcount
        conn.commit()

    if num_rows_updated:
        redisServ.update_user_info(id, {"email_check": 1})
        return {
            "msg": "success",
        }, StatusCode.OK

    raise BadRequest("유효하지 않은 인증키입니다.")


# # ##### register && setting
def setting(id, data, images):
    user = utils.get_user(id)
    if not user:
        raise Unauthorized("유저 정보를 찾을 수 없습니다.")

    utils.check_authorization(id, Authorization.EMAIL)

    # 업데이트할 항목 정리
    update_fields = dict()
    categories = ("last_name", "name", "age", "gender", "taste", "bio", "similar")
    for category in categories:
        if category in data:
            update_fields[category] = data[category]

    if data.get("email") and user["email"] != data["email"]:
        update_fields["email"] = data["email"]
        update_fields["email_key"] = utils.create_email_key(Key.EMAIL)
    if user["oauth"] == Oauth.NONE and data.get("pw"):
        update_fields["password"] = utils.hashing(data["pw"])

    if "tags" in data:
        update_fields["tags"] = utils.encode_bit(data["tags"])
    if "hate_tags" in data:
        update_fields["hate_tags"] = utils.encode_bit(data["hate_tags"])
    if "emoji" in data:
        update_fields["emoji"] = utils.encode_bit(data["emoji"])
    if "hate_emoji" in data:
        update_fields["hate_emoji"] = utils.encode_bit(data["hate_emoji"])
    

    # TODO 이미지 있을 수 밖에 없음... (if문 삭제)
    if images:
        # 이전 프로필 사진 지우기
        pictures = user["pictures"]
        for file_to_delete in pictures:
            if file_to_delete == DEFAULT_PICTURE:
                continue
            file_path = os.path.join(PICTURE_DIR, file_to_delete)
            try:
                os.remove(file_path)
            except Exception as e:
                # import app
                print(f"사진 삭제 시 에러 발생(setting): {e}")
                # app.logger.error(f"사진 삭제 시 에러 발생(setting): {e}")
                pass
        update_fields["pictures"] = images

    conn = PostgreSQLFactory.get_connection()
    with conn.cursor(cursor_factory=DictCursor) as cursor:
        set_statements = ", ".join(
            [f'"{key}" = %s' for key in update_fields.keys()]
        )
        sql = f'UPDATE "User" SET {set_statements} WHERE "id" = %s;'
        cursor.execute(sql, tuple(update_fields.values()) + (id,))

        if "email" in update_fields:
            sql = f'UPDATE "User" SET "email_check" = %s WHERE "id" = %s;'
            cursor.execute(sql, (False, id))

        conn.commit()


    if "email" in update_fields:
        try:
            utils.send_email(update_fields["email"], update_fields["email_key"], Key.EMAIL)
        except Exception:
            pass
        logout(id)
        
    #Redis 업데이트
    redisServ.update_user_info(id, update_fields)

    return {
        "email_check": False if "email" in update_fields else True,
        "profile_check": True if (user["gender"] or "gender" in update_fields) else False,
        "emoji_check": True if (user["emoji"] is not None or "emoji" in update_fields) else False,
    }, StatusCode.OK


# TODO [TEST] dummy data
def register_dummy(data):
    hashed_pw = utils.hashing(data["pw"])
    now_kst = datetime.now(KST)
    pictures = [DEFAULT_PICTURE]

    conn = PostgreSQLFactory.get_connection()
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
                data["gender"],
                data["taste"],
                data["bio"],
                utils.encode_bit(data["tags"]),
                utils.encode_bit(data["hate_tags"]),
                utils.encode_bit(data["emoji"]),
                utils.encode_bit(data["hate_emoji"]),
                data["similar"]
            ),
        )
        conn.commit()



def save_pictures(id, files):
    images = []
    try:
        for idx, image_data in enumerate(files):
            if MAX_PICTURE_AMOUNT <= idx: # 최대 5장까지
                break
            
            image_info, encoded_data = image_data.split(",", 1)

            extension = utils.get_extension(image_info)
            decoded_data = base64.b64decode(encoded_data)

            filename = f"{id}_{idx}_{datetime.now(KST).strftime("%Y%m%d%H%M%S")}.{extension}"
            
            # 파일 저장
            file_path = os.path.join(PICTURE_DIR, filename)

            with open(file_path, 'wb') as f:
                f.write(decoded_data)

            # 저장된 파일명 리스트에 추가
            images.append(filename)

    except Exception as e:
        #저장된 사진 삭제하기
        for image_to_delete in images:
            if image_to_delete == DEFAULT_PICTURE:
                continue
            file_path = os.path.join(PICTURE_DIR, image_to_delete)
            try:
                os.remove(file_path)
            except Exception as e:
                # import app
                print(f"사진 삭제 시 에러 발생(save_pictures): {e}")
                # app.logger.error(f"사진 삭제 시 에러 발생(save_pictures): {e}")
                pass
        raise e

    return images


def register(data):
    login_id = data["login_id"]
    hashed_pw = utils.hashing(data["pw"])
    email_key = utils.create_email_key(Key.EMAIL)

    conn = PostgreSQLFactory.get_connection()
    with conn.cursor(cursor_factory=DictCursor) as cursor:
        sql = 'INSERT INTO "User" (email, email_check, email_key, login_id, password, \
                                    name, last_name, oauth, pictures, last_online) \
                            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)'
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
                [DEFAULT_PICTURE],
                datetime.now(KST)
            ),
        )
        conn.commit()

    if os.getenv("PYTEST") == "True":
        return {
            "key": email_key,
        }, StatusCode.OK
        
    try:
        utils.send_email(data["email"], email_key, Key.EMAIL)
    except Exception:
        pass

    return {
        "msg": "success",
    }, StatusCode.OK


def register_oauth(data, oauthOpt):
    conn = PostgreSQLFactory.get_connection()
    with conn.cursor(cursor_factory=DictCursor) as cursor:
        sql = 'INSERT INTO "User" (email, email_check, login_id, name, last_name, oauth, pictures, last_online) \
                            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)'
        cursor.execute(
            sql, (data["email"], True, data["login_id"], data["name"], data["last_name"], oauthOpt, [DEFAULT_PICTURE], datetime.now(KST))
        )
        conn.commit()


def profile_detail(id, target_id):
    # 유저 API 접근 권한 확인
    utils.check_authorization(id, Authorization.EMOJI)
    
    # block check
    block_set = redisServ.get_user_info(id, RedisOpt.BLOCK)
    if target_id in block_set:
        raise BadRequest("차단한 유저입니다.")

    # ban check
    ban_set = redisServ.get_user_info(id, RedisOpt.BAN)
    if target_id in ban_set:
        return BadRequest("잘못된 접근입니다.")
    
    target = utils.get_user(target_id)
    if not target:
        raise BadRequest("존재하지 않는 유저입니다.")

    # History.last_view update
    historyUtils.update_last_view(id, target_id)

    ## (socket) history update alarm
    socketServ.new_visitor(target_id)

    images = utils.get_pictures(target["pictures"])

    return {
        "login_id": target["login_id"],
        "status": socketServ.check_status(target_id),
        "last_online": (target["last_online"]+timedelta(hours=9)).strftime(TIME_DETAIL_PAGE_STR_TYPE),
        "fame": (
            (target["count_fancy"] / target["count_view"] * MAX_FAME)
            if target["count_view"]
            else 0
        ),
        "gender": target["gender"],
        "taste": target["taste"],
        "bio": target["bio"],
        "tags": utils.decode_bit(target["tags"]),
        "hate_tags": utils.decode_bit(target["hate_tags"]),
        "emoji": utils.decode_bit(target["emoji"]),
        "hate_emoji": utils.decode_bit(target["hate_emoji"]),
        "similar": target["similar"],
        "pictures": images,
    }, StatusCode.OK


def logout(id):
    # socket 정리 및 last_online 업데이트는 handle_disconnect()에서 자동으로 처리될 것

    # 유저의 토큰을 redis 블록리스트에 추가
    jti = get_jwt()["jti"]
    refresh_jti = redisServ.get_refresh_jti_by_id(id)

    redisBlockList.update_block_list(jti, refresh_jti)
    
    #redis 정보 삭제
    redisServ.delete_user_info(id)
    
    # jwt token 캐시에서 삭제
    response = make_response(jsonify({"msg": "success"}), StatusCode.OK)
    unset_jwt_cookies(response)
    
    return response


def find_login_id(email):
    conn = PostgreSQLFactory.get_connection()
    with conn.cursor(cursor_factory=DictCursor) as cursor:

        sql = 'SELECT * FROM "User" WHERE "email" = %s;'
        cursor.execute(sql, (email,))
        user = cursor.fetchone()
        if not user:
            raise BadRequest("이메일이 존재하지 않습니다.")

        if user["oauth"] != Oauth.NONE:
            raise BadRequest("소셜 로그인 사용자입니다.")

        return {"login_id": utils.blur_login_id(user["login_id"])}, StatusCode.OK


def request_reset(login_id):
    user = utils.get_user_by_login_id(login_id)
    if not user:
        raise BadRequest("존재하지 않는 로그인 id입니다.")

    if not user["email_check"]:
        raise Forbidden("인증되지 않은 이메일입니다.")

    email_key = utils.create_email_key(Key.PASSWORD)

    conn = PostgreSQLFactory.get_connection()
    with conn.cursor(cursor_factory=DictCursor) as cursor:
        sql = 'UPDATE "User" SET "email_key" = %s WHERE "login_id" = %s;'
        cursor.execute(sql, (email_key, login_id))
        conn.commit()

    if os.getenv("PYTEST") == "True":
        return {
            "email_check": True,
            "key": email_key,
        }, StatusCode.OK

    try:
        utils.send_email(user["email"], email_key, Key.PASSWORD)
    except Exception:
        pass
        
    return {"email_check": True}, StatusCode.OK


def reset_pw(pw, key):
    if not pw:
        raise BadRequest("변경할 비밀번호를 입력해주세요.")
    
    if key[-1] != str(Key.PASSWORD):
        raise BadRequest("유효하지 않은 인증키입니다.")

    hashed_pw = utils.hashing(pw)

    conn = PostgreSQLFactory.get_connection()
    with conn.cursor(cursor_factory=DictCursor) as cursor:
        
        sql = 'UPDATE "User" SET "password" = %s, "email_key" = %s WHERE "email_key" = %s;'
        cursor.execute(sql, (hashed_pw, None, key))

        if cursor.rowcount < 1:
            raise BadRequest("유효하지 않은 인증키입니다.")

        conn.commit()

    return {
        "msg": "success",
    }, StatusCode.OK


def unregister(id):
    # 유저 API 접근 권한 확인
    utils.check_authorization(id, Authorization.EMOJI)

    logout(id)
    # if os.getenv("PYTEST") != "True":
    socketServ.unregister(id)
    redisServ.delete_user_info(id)

    # TODO 모두 잘 삭제되는지 및 채팅창 에러 안뜨는지 확인 필요
    conn = PostgreSQLFactory.get_connection()
    with conn.cursor(cursor_factory=DictCursor) as cursor:
        sql = 'DELETE FROM "User" WHERE "id" = %s CASCADE;'
        cursor.execute(sql, (id,))
        conn.commit()

    return {
        "msg": "success",
    }, StatusCode.OK



##### search
def get_profile(id):
    # 유저 API 접근 권한 확인
    utils.check_authorization(id, Authorization.EMOJI)
    
    return utils.get_user_profile(id), StatusCode.OK
    
    
def search(id, data):
    # 유저 API 접근 권한 확인
    utils.check_authorization(id, Authorization.EMOJI)
    
    tags = utils.encode_bit(data["tags"]) if data["tags"] else Tags.ALL
    distance = data["distance"]
    fame = data["fame"]
    min_age = data["min_age"]
    max_age = data["max_age"]

    redis_user = redisServ.get_user_info(id, RedisOpt.LOCATION)
    if redis_user is None or redis_user['longitude'] is None:
        raise Unauthorized("유저 정보를 찾을 수 없습니다.")
    long, lat = redis_user["longitude"], redis_user["latitude"]

    conn = PostgreSQLFactory.get_connection()
    with conn.cursor(cursor_factory=DictCursor) as cursor:
        sql = 'SELECT * FROM ( \
                            SELECT *, 6371 * acos( \
                                        cos(radians(%s)) * cos(radians(latitude)) * cos(radians(longitude) - radians(%s)) + \
                                        sin(radians(%s)) * sin(radians(latitude)) \
                                    ) AS distance \
                            FROM "User" \
                        ) AS user_distance \
                WHERE "id" != %s \
                        AND "id" NOT IN ( \
                                SELECT "target_id" \
                                FROM "Block" \
                                WHERE "user_id" = %s ) \
                        AND "id" NOT IN ( \
                                SELECT "user_id" \
                                FROM "Block" \
                                WHERE "target_id" = %s ) \
                        AND "age" BETWEEN %s AND %s \
                        AND "emoji" IS NOT NULL \
                        AND "tags" & %s = %s \
                        AND "count_fancy"::float / COALESCE("count_view", 1) * %s >= %s \
                        AND distance <= %s \
                ORDER BY "last_online" DESC, distance ASC \
                LIMIT %s;'

        cursor.execute(
            sql,
            (
                lat,
                long,
                lat,
                id,
                id,
                id,
                min_age,
                max_age,
                tags,
                tags,
                MAX_FAME,
                fame,
                distance,
                MAX_SEARCH,
            ),
        )
        db_data = cursor.fetchall()
        
        result = [utils.get_target_profile(id, target["id"]) for target in db_data]
        return {
            "profile_list": result,
        }, StatusCode.OK


##### tea suggest
def suggest(id):
    # 유저 API 접근 권한 확인
    utils.check_authorization(id, Authorization.EMOJI)

    # 성적 취향이 서로 맞고
    # 싫은게 하나도 없고 (hate_tag, hate_emoji)
    # 겹치는거 많은 순(tag, emoji)
    # 유저와 같은 지역에 fame rating 높은 사람으로

    user = utils.get_user(id)
    if user is None:
        raise Unauthorized("유저 정보를 찾을 수 없습니다.")

    tags, hate_tags = user["tags"], user["hate_tags"]
    emoji, hate_emoji = user["emoji"], user["hate_emoji"]
    long, lat = user["longitude"], user["latitude"]
    similar = user["similar"]
    min_age = user["age"] - AGE_GAP
    max_age = user["age"] + AGE_GAP
    
    find_taste = user["gender"] | Gender.OTHER
    find_gender = Gender.ALL if user["taste"] & Gender.OTHER else user["taste"]

    db_data = []
    conn = PostgreSQLFactory.get_connection()

    with conn.cursor(cursor_factory=DictCursor) as cursor:
        sql = 'SELECT * FROM ( \
                            SELECT *, 6371 * acos( \
                                        cos(radians(%s)) * cos(radians(latitude)) * cos(radians(longitude) - radians(%s)) + \
                                        sin(radians(%s)) * sin(radians(latitude)) \
                                    ) AS distance \
                            FROM "User" \
                        ) AS user_distance \
                WHERE "id" != %s \
                    AND "id" NOT IN ( \
                            SELECT "target_id" \
                            FROM "Block" \
                            WHERE "user_id" = %s ) \
                    AND "id" NOT IN ( \
                            SELECT "user_id" \
                            FROM "Block" \
                            WHERE "target_id" = %s ) \
                    AND "age" BETWEEN %s AND %s \
                    AND "emoji" IS NOT NULL \
                    AND "taste" & %s > 0 \
                    AND "gender" & %s > 0 \
                    AND "hate_tags" & %s = 0 \
                    AND "tags" & %s = 0 \
                    AND "hate_emoji" & %s = 0 \
                    AND "emoji" & %s = 0 \
                    AND "tags" & %s >= 0 \
                    AND CASE WHEN %s THEN "emoji" & %s >= 0 \
                            ELSE "emoji" & %s = 0 \
                        END \
                    AND "distance" <= %s \
                ORDER BY CASE WHEN %s THEN "emoji" & %s \
                        END DESC, \
                        "tags" & %s DESC, \
                        distance ASC, \
                        "count_fancy"::float / COALESCE("count_view", 1) DESC \
                LIMIT %s ;'

        cursor.execute(
            sql,
            (
                lat,
                long,
                lat,
                id,
                id,
                id,
                min_age,
                max_age,
                find_taste,
                find_gender,
                tags,
                hate_tags,
                emoji,
                hate_emoji,
                tags,
                similar,
                emoji,
                emoji,
                AREA_DISTANCE,
                similar,
                emoji,
                tags,
                MAX_SUGGEST,
            ),
        )
        db_data = cursor.fetchall()

        result = [utils.get_target_profile(id, target["id"]) for target in db_data]
        return {
            "profile_list": result,
        }, StatusCode.OK


##### report && block
def report(id, data):
    # 유저 API 접근 권한 확인
    utils.check_authorization(id, Authorization.EMOJI)
    
    if id == int(data["target_id"]):
        raise BadRequest("스스로를 신고할 수 없습니다.")

    target_id = data.get("target_id")
    target = utils.get_user(target_id)
    if not target:
        raise BadRequest("존재하지 않는 유저입니다.")

    reason = data.get("reason")
    if reason < Report.MIN or Report.MAX < reason:
        raise BadRequest("유효하지 않은 신고 사유입니다.")
    
    reason_opt = None
    if reason == Report.OTHER:
        reason_opt = data.get("reason_opt", None)
        if reason_opt is None:
            raise BadRequest("사유를 입력해주세요.")
    
    # report시 자동 block 처리
    block(id, target_id)

    conn = PostgreSQLFactory.get_connection()
    with conn.cursor(cursor_factory=DictCursor) as cursor:
        sql = 'INSERT INTO "Report" (user_id, target_id, reason, reason_opt) \
                            VALUES (%s, %s, %s, %s)'
        cursor.execute(sql, (id, target_id, reason, reason_opt))
        conn.commit()

    return {
        "msg": "success",
    }, StatusCode.OK


def block(id, target_id):
    # 유저 API 접근 권한 확인
    utils.check_authorization(id, Authorization.EMOJI)
    
    if id == target_id:
        raise BadRequest("스스로를 block할 수 없습니다.")

    target = utils.get_user(target_id)
    if not target:
        raise BadRequest("존재하지 않는 유저입니다.")

    # block check
    block_set = redisServ.get_user_info(id, RedisOpt.BLOCK)
    if target_id in block_set:
        raise BadRequest("이미 블록한 유저입니다.")

    conn = PostgreSQLFactory.get_connection()
    with conn.cursor(cursor_factory=DictCursor) as cursor:
        sql = 'INSERT INTO "Block" (user_id, target_id) VALUES (%s, %s)'
        cursor.execute(sql, (id, target_id))

        # user -> target
        sql = 'SELECT * FROM "History" WHERE "user_id" = %s AND "target_id" = %s;'
        cursor.execute(sql, (id, target_id))
        user_history = cursor.fetchone()
        if user_history:
            if user_history["fancy"]:
                sql = 'UPDATE "User" SET "count_fancy" = "count_fancy" - 1 WHERE "id" = %s;'
                cursor.execute(sql, (target_id,))
            #TODO [Later] soft delete
            sql = 'DELETE FROM "History" WHERE "user_id" = %s AND "target_id" = %s;'
            cursor.execute(sql, (id, target_id))
        
        # target -> user
        sql = 'SELECT * FROM "History" WHERE "user_id" = %s AND "target_id" = %s;'
        cursor.execute(sql, (target_id, id))
        target_history = cursor.fetchone()
        if target_history:
            if target_history["fancy"]:
                sql = 'UPDATE "User" SET "count_fancy" = "count_fancy" - 1 WHERE "id" = %s;'
                cursor.execute(sql, (id,))
            #TODO [Later] soft delete
            sql = 'DELETE FROM "History" WHERE "user_id" = %s AND "target_id" = %s;'
            cursor.execute(sql, (target_id, id))

        conn.commit()
        
    #redis update
    redisServ.update_user_info(id, {"block": target_id})
    redisServ.update_user_info(target_id, {"ban": id})
    
    #delete chat
    chatUtils.delete_chat(id, target_id)

    return {
        "msg": "success",
    }, StatusCode.OK


def reset_token(id):
    redis_user = redisServ.get_user_info(id, RedisOpt.LOGIN)
    if redis_user is None or redis_user['email'] is None:
        raise Unauthorized("refresh: reset_token")

    response = make_response(jsonify({"msg": "success"}), StatusCode.OK)
    
    #JWT 토큰 생성 및 쿠키 설정
    access_token = create_access_token(identity=id)
    set_access_cookies(response, access_token, max_age=int(os.getenv("ACCESS_TIME"))*60)
    
    return response


def dummy_profile_detail(id, target_id):
    target = utils.get_user(target_id)
    if not target:
        raise BadRequest("존재하지 않는 유저입니다.")

    # History.last_view update
    historyUtils.update_last_view(id, target_id)

    images = utils.get_pictures(target["pictures"])

    return {
        "login_id": target["login_id"],
        "status": socketServ.check_status(target_id),
        "last_online": (target["last_online"]+timedelta(hours=9)).strftime(TIME_DETAIL_PAGE_STR_TYPE),
        "fame": (
            (target["count_fancy"] / target["count_view"] * MAX_FAME)
            if target["count_view"]
            else 0
        ),
        "gender": target["gender"],
        "taste": target["taste"],
        "bio": target["bio"],
        "tags": utils.decode_bit(target["tags"]),
        "hate_tags": utils.decode_bit(target["hate_tags"]),
        "emoji": utils.decode_bit(target["emoji"]),
        "hate_emoji": utils.decode_bit(target["hate_emoji"]),
        "similar": target["similar"],
        "pictures": images,
    }, StatusCode.OK