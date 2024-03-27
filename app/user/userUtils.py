from app.smtp import sendSmtpEmail
import os, re, random, string
import bcrypt
from datetime import datetime, timedelta
import pytz
from ..const import KST, EARTH_RADIUS, IGNORE_MOVE
import math
from app.db import conn
from psycopg2.extras import DictCursor
from flask import request
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut
from flask_jwt_extended import get_jwt_identity


def update_location_DB(id, long, lat):
    from ..socket import socket_service as socketServ

    cursor = conn.cursor(cursor_factory=DictCursor)
    sql = 'SELECT * FROM "User" WHERE "id" = %s;'
    cursor.execute(sql, (id, ))

    user = cursor.fetchone()
    if not user:
        cursor.close()
        return
    
    if not user['longitude'] or not user['latitude'] \
        or IGNORE_MOVE < get_distance(user['latitude'], user['longitude'], lat, long):
        #update location
        sql = 'UPDATE "User" SET "longitude" = %s, "latitude" = %s WHERE "id" = %s;'
        cursor.execute(sql, (long, lat, id))
        conn.commit()
        cursor.close()

        #(socket) 거리 업데이트
        socketServ.update_distance(id, long, lat)


def update_location(f):
    def wrapper(*args, **kwargs):
        try:
            #TODO [JWT]
            id = 1
            # id = get_jwt_identity()['id']

            long = request.header.get('longitude')
            lat = request.header.get('latitude')
            
            if not long or not lat:
                ip_addr = request.remote_addr
                geolocator = Nominatim(user_agent="geoapiExercises")
                location = geolocator.geocode(ip_addr)

                if not location:
                    raise Exception('no location returned from geopy')

                long = location.longitude
                lat = location.latitude

            update_location_DB(id, long, lat)
        
        except GeocoderTimedOut:
            print("Error: geocode failed due to timeout")

        except Exception as e:
            print(f'Error: while update_location on DB: {e}')

        return f(*args, **kwargs)
    
    return wrapper


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


def check_refresh(refresh) -> bool:
    from ...wsgi import jwt

    #TODO 잘못된 refresh decode 하려고 하면 어떻게 되는지 확인 필요
    refresh_decoded = jwt.decode(refresh, os.environ.get('REFRESH_KEY'))

    #TODO refresh_decoded['exp'] 로 바로 날짜 비교 할 수 있는지 체크 필요
    if refresh_decoded['exp'] <= datetime.now(pytz.timezone(KST)):
        return True
    
    return False


def decode_jwt(jwt):
    from ...wsgi import jwt

    #TODO 잘못된 jwt decode 하려고 하면 어떻게 되는지 확인 필요
    jwt_decoded = jwt.decode(jwt, os.environ.get('JWT_KEY'))

    #TODO refresh_decoded['exp'] 로 바로 날짜 비교 할 수 있는지 체크 필요
    if jwt_decoded['exp'] <= datetime.now(pytz.timezone(KST)):
        return jwt_decoded['id']
    
    return None


def delete_refresh(id):
    cursor = conn.cursor(cursor_factory=DictCursor)
    sql = 'UPDATE "User" SET "refresh" = NULL WHERE "id" = %s;'
    cursor.execute(sql, (id, ))
    conn.commit()
    cursor.close()


def update_last_online(id):
    cursor = conn.cursor(cursor_factory=DictCursor)
    sql = 'SELECT * FROM "User" WHERE "id" = %s;'
    cursor.execute(sql, (id, ))
    user = cursor.fetchone()
    if user:
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
    return encrypted.decode("utf-8")

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


def allowed_file(filename, id):
    if '.' in filename:
        name, extension = filename.rsplit('.', 1)
        if 0 <= int(name) < 5 and extension.lower() in {'png', 'jpg', 'jpeg'}:
            return str(id) + "_" + name + '.' + extension
    return None