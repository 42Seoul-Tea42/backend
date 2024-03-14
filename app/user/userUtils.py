from app.smtp import sendSmtpEmail
import os, re, random, string
import bcrypt
from datetime import datetime, timedelta
import pytz
from ..const import KST, EARTH_RADIUS
import math
from app.db import conn
from psycopg2.extras import DictCursor


def generate_jwt(id):
    from ...wsgi import jwt
    jwt_time = datetime.now(pytz.timezone(KST)) \
            + timedelta(minutes=int(os.environ.get('JWT_TIME')))
    jwt_json = {
        "id": id,
        "exp": jwt_time
    }
    return jwt.encode(jwt_json, os.environ.get('JWT_KEY'))


def generate_refresh(id):
    from ...wsgi import jwt
    refresh_time = datetime.now(pytz.timezone(KST)) \
            + timedelta(minutes=int(os.environ.get('REFRESH_TIME')))
    refresh_json = {
        "exp": refresh_time
    }
    return jwt.encode(refresh_json, os.environ.get('REFRESH_KEY'))


def check_refresh(refresh):
    from ...wsgi import jwt
    refresh_decoded = jwt.decode(refresh, os.environ.get('REFRESH_KEY'))

    #TODO refresh_decoded['exp'] 로 바로 날짜 비교 할 수 있는지 체크 필요
    if refresh_decoded['exp'] <= datetime.now(pytz.timezone(KST)):
        return True

    return False


def update_last_online(id):
    cursor = conn.cursor(cursor_factory=DictCursor)
    sql = 'UPDATE "User" SET "refresh" = %s, last_online = %s WHERE "id" = %s;'
    cursor.execute(sql, (None, datetime.now(pytz.timezone(KST)), id))
    conn.commit()
    cursor.close()


def createEmailKey(login_id, key):   
    random_key = login_id + ''.join(random.choices(string.ascii_letters + string.digits, k=10)) + str(key)
    return random_key


def encodeBit(data) -> int:
    result = 0

    #TODO logic 체크
    for n in list(data):
        result |= n

    return result


def decodeBit(encoded_data) -> list:
    result = []
    bit_position = 1
    while encoded_data > 0:
        if encoded_data & 1:
            result.append(bit_position)
        encoded_data >>= 1
        bit_position += 1
    return result


def sendEmail(addr_to, key, opt):
    sendSmtpEmail(addr_to, key, opt)


def isValidEmail(email):
    reg = r"^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9.]+\.[a-zA-Z]{2,3}$"  # 유효성 검사를 위한 정규표현식
    if re.match(reg, email):
        return True
    return False



def hashing(password, login_id):
    #TODO bcrypt, sha256 등 해시 관련 내용 블로그 정리
    encrypted = bcrypt.hashpw((password + login_id).encode("utf-8"), bcrypt.gensalt())  # str 객체, bytes로 인코드, salt를 이용하여 암호화
    return encrypted.decode("uft-8")

    #sha256방식
    # m = hashlib.sha256()
    # m.update((password + login_id).encode('utf-8'))
    # m.update(os.environ.get('SECRET_KEY').encode('utf-8'))
    # return m.hexdigest()


def isValidPassword(password, login_id, hashed_pw):
    return bcrypt.checkpw((password + login_id).encode("utf-8"), hashed_pw)

    #sha256방식
    # if hashing(password, login_id) == hashed:
    #     return True
    # return False


def get_distance(lat1, long1, lat2, long2):

    # 위도와 경도의 라디안 차이 계산
    diff_long = math.radians(long2) - math.radians(long1)
    diff_lat = math.radians(lat2) - math.radians(lat1)
    
    # Haversine 공식 계산
    a = math.sin(diff_lat / 2) ** 2 \
        + math.cos(lat1) * math.cos(lat2) * math.sin(diff_long / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    
    # 거리 계산 (m)
    return EARTH_RADIUS * c / 1000