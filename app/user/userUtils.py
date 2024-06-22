import os, re, random, string
import requests
import bcrypt

from datetime import datetime
import math

import base64
from ..db.db import PostgreSQLFactory
from psycopg2.extras import DictCursor

from ..history import historyUtils
from ..utils import smtp, redisServ
from ..utils.const import (
    KST,
    EARTH_RADIUS,
    ALLOWED_EXTENSIONS,
    PICTURE_DIR,
    MAX_FAME,
    FancyOpt,
    DEFAULT_PICTURE,
    RedisOpt,
    RedisSetOpt,
    Authorization,
    LOGIN_ID_BLUR_SIZE,
)
from werkzeug.exceptions import Unauthorized, BadRequest, Forbidden


def create_email_key(key):
    random_key = (
        "".join(random.choices(string.ascii_letters + string.digits, k=10))
        + str(key)
    )
    return random_key


def encode_bit(data) -> int:
    result = 0
    for n in data:
        result |= 1 << n - 1

    return result


def decode_bit(encoded_data) -> list:
    result = []
    bit_position = 1
    while encoded_data > 0:
        if encoded_data & 1:
            result.append(bit_position)
        encoded_data >>= 1
        bit_position += 1
    return result


def send_email(addr_to, key, opt):
    smtp.send_smtp_email(addr_to, key, opt)




def hashing(password):
    # TODO bcrypt, sha256 등 해시 관련 내용 블로그 정리
    encrypted = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())
    return encrypted

    # sha256방식
    # m = hashlib.sha256()
    # m.update((password + login_id).encode('utf-8'))
    # m.update(os.getenv('SECRET_KEY').encode('utf-8'))
    # return m.hexdigest()


def matched_password(password, hashed_pw):
    if password is None or hashed_pw is None:
        return False

    return bcrypt.checkpw(password.encode("utf-8"), bytes(hashed_pw))

    # sha256방식
    # if hashing(password, login_id) == hashed:
    #     return True
    # return False


def allowed_file(filename, id):
    if "." in filename:
        name, extension = filename.rsplit(".", 1)
        if 0 <= int(name) < 5 and extension.lower() in {"png", "jpg", "jpeg"}:
            return str(id) + "_" + name + "." + extension
    return None


def get_user(id):
    conn = PostgreSQLFactory.get_connection()
    with conn.cursor(cursor_factory=DictCursor) as cursor:
        sql = 'SELECT * FROM "User" WHERE "id" = %s;'
        cursor.execute(sql, (id,))
        user = cursor.fetchone()

    return user


def get_user_by_login_id(login_id):
    conn = PostgreSQLFactory.get_connection()
    with conn.cursor(cursor_factory=DictCursor) as cursor:
        sql = 'SELECT * FROM "User" WHERE "login_id" = %s;'
        cursor.execute(sql, (login_id,))
        user = cursor.fetchone()

    return dict(user) if user else None




def blur_login_id(login_id):
    return login_id[: len(login_id) - LOGIN_ID_BLUR_SIZE] + "*" * LOGIN_ID_BLUR_SIZE


def get_extension(image_info):
    match = re.match(r"data:image/(?P<extension>[\w]+);base64", image_info)
    if match:
        extension = match.group("extension")
    else:
        raise ValueError("Invalid image data format")

    if extension not in ALLOWED_EXTENSIONS:
        raise ValueError("Invalid image extension")

    return extension


def get_picture(filename):
    image_path = os.path.join(PICTURE_DIR, filename)
    extension = filename.split(".")[-1]

    with open(image_path, "rb") as image_file:
        image_data = f"data:image/{extension};base64,{base64.b64encode(image_file.read()).decode("utf-8")}"
        
    return image_data


def get_pictures(filenames):
    images = []
    for filename in filenames:
        images.append(get_picture(filename))

    # 이미지 파일이 없을 경우 default 이미지 추가
    if not images:
        images.append(get_picture(DEFAULT_PICTURE))

    return images


def get_user_profile(id):
    user = get_user(id)
    if not user:
        raise Unauthorized("유저 정보를 찾을 수 없습니다.")

    # 이미지 파일 생성
    images = get_pictures(user["pictures"])

    # 유저 정보 및 이미지 파일을 포함한 응답 생성
    return {
        "login_id": user["login_id"],
        "name": user["name"],
        "last_name": user["last_name"],
        "email": user["email"],
        "age": user["age"],
        "gender": user["gender"],
        "taste": user["taste"],
        "bio": user["bio"],
        "tags": decode_bit(user["tags"]),
        "hate_tags": decode_bit(user["hate_tags"]),
        "emoji": decode_bit(user["emoji"]),
        "hate_emoji": decode_bit(user["hate_emoji"]),
        "similar": user["similar"],
        "pictures": images,
    }


def get_target_profile(id, target_id, time=None):
    redis_user = redisServ.get_user_info(id, RedisOpt.LOCATION)
    if redis_user is None or redis_user['longitude'] is None or redis_user['latitude'] is None:
        raise Unauthorized("유저 정보를 찾을 수 없습니다.")

    target = get_user(target_id)
    if not target:
        raise BadRequest("존재하지 않는 유저입니다.")

    # 첫 이미지 파일 생성
    image = get_picture(target["pictures"][0])

    # 유저 정보 및 이미지 파일을 포함한 응답 생성
    return {
        "id": target["id"],
        "name": target["name"],
        "last_name": target["last_name"],
        "distance": get_distance(
            float(redis_user["latitude"]),
            float(redis_user["longitude"]),
            target["latitude"],
            target["longitude"],
        ),
        "fancy": historyUtils.get_fancy_status(id, target_id),
        "age": target["age"],
        "tags": decode_bit(target["tags"]),
        "fame": (
            (target["count_fancy"] / target["count_view"] * MAX_FAME)
            if target["count_view"]
            else 0
        ),
        "picture": image,
        "time": time,
    }


def update_last_online(id):
    conn = PostgreSQLFactory.get_connection()
    with conn.cursor(cursor_factory=DictCursor) as cursor:
        sql = 'SELECT * FROM "User" WHERE "id" = %s;'
        cursor.execute(sql, (id,))
        user = cursor.fetchone()
        if user:
            sql = 'UPDATE "User" SET last_online = %s WHERE "id" = %s;'
            cursor.execute(sql, (datetime.now(KST), id))
            conn.commit()


def update_count_view(target_id):
    conn = PostgreSQLFactory.get_connection()
    with conn.cursor(cursor_factory=DictCursor) as cursor:
        sql = 'UPDATE "User" SET count_view = COALESCE("count_view", 0) + 1 \
                    WHERE "id" = %s'
        cursor.execute(sql, (target_id,))
        conn.commit()


def update_count_fancy(target_id, opt):
    conn = PostgreSQLFactory.get_connection()
    with conn.cursor(cursor_factory=DictCursor) as cursor:
        if opt == FancyOpt.ADD:
            sql = 'UPDATE "User" SET count_fancy = COALESCE("count_fancy", 0) + 1 \
                        WHERE "id" = %s'
        else:
            sql = 'UPDATE "User" SET count_fancy = COALESCE("count_fancy", 0) - 1 \
                        WHERE "id" = %s'
        cursor.execute(sql, (target_id,))
        conn.commit()


def update_event(id):
    conn = PostgreSQLFactory.get_connection()
    with conn.cursor(cursor_factory=DictCursor) as cursor:
        sql = 'UPDATE "User" SET "is_fancy" = %s, "is_visitor" = %s, "is_match" = %s WHERE "id" = %s'
        cursor.execute(sql, (id, False, False, False))
        conn.commit()


### location & distance ###


def get_location_by_ip(ip_address=None):
    if ip_address is None or os.getenv("PYTEST"):
        return 37.5660, 126.9784

    # API로 위도ㅡ경도 받아오기
    api_uri = os.getenv("IP_API_URI")
    api_key = os.getenv("IP_API_KEY")
    url = f"{api_uri}{ip_address}?token={api_key}"

    # API에 HTTP GET 요청 보내기
    response = requests.get(url)
    data = response.json()

    if "bogon" in data:
        return 37.5660, 126.9784

    # 위도와 경도 추출
    lat, long = [float(i) for i in data["loc"].split(",")]
    if lat is None or long is None:
        print('[ERROR] get_location_by_ip (None) =>', data["loc"])
        return 37.5660, 126.9784

    return lat, long


def get_distance(lat1, long1, lat2, long2):

    # 위도와 경도의 라디안 차이 계산
    diff_long = math.radians(long2) - math.radians(long1)
    diff_lat = math.radians(lat2) - math.radians(lat1)

    # Haversine 공식 계산
    a = (
        math.sin(diff_lat / 2) ** 2
        + math.cos(lat1) * math.cos(lat2) * math.sin(diff_long / 2) ** 2
    )
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    # 거리 계산 (m)
    return EARTH_RADIUS * c / 1000


# 위치 정보 DB에 저장
def update_location(id, lat, long):
    conn = PostgreSQLFactory.get_connection()
    with conn.cursor(cursor_factory=DictCursor) as cursor:
        sql = 'UPDATE "User" SET "longitude" = %s, "latitude" = %s WHERE "id" = %s;'
        cursor.execute(sql, (long, lat, id))
        conn.commit()


def check_authorization(id, opt):
    redis_user = redisServ.get_user_info(id, RedisOpt.LOGIN)
    if redis_user is None or redis_user['email'] is None:
        raise Unauthorized("유저 정보를 찾을 수 없습니다.")

    if Authorization.EMAIL <= opt and redis_user["email_check"] == RedisSetOpt.UNSET:
        raise Forbidden("이메일 인증이 필요합니다.")

    if (
        Authorization.PROFILE <= opt
        and redis_user["profile_check"] == RedisSetOpt.UNSET
    ):
        raise Forbidden("프로필 작성이 필요합니다.")

    if Authorization.EMOJI <= opt and redis_user["emoji_check"] == RedisSetOpt.UNSET:
        raise Forbidden("이모지 선택이 필요합니다.")


def get_block_list(id):
    conn = PostgreSQLFactory.get_connection()
    with conn.cursor(cursor_factory=DictCursor) as cursor:
        sql = 'SELECT "target_id" FROM "Block" WHERE "user_id" = %s;'
        cursor.execute(sql, (id,))
        block = cursor.fetchall()

    return [row["target_id"] for row in block]


def get_ban_list(id):
    conn = PostgreSQLFactory.get_connection()
    with conn.cursor(cursor_factory=DictCursor) as cursor:
        sql = 'SELECT "user_id" FROM "Block" WHERE "target_id" = %s;'
        cursor.execute(sql, (id,))
        ban = cursor.fetchall()

    return [row["user_id"] for row in ban]
