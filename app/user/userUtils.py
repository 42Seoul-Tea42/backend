from app.smtp import sendSmtpEmail
import os, re, random, string
import bcrypt
from datetime import datetime, timedelta
import pytz
from ..const import KST


def createJwt(id):
    #상호참조 이슈로 하기에 배치
    from ...wsgi import jwt

    now_kst = datetime.now(pytz.timezone(KST))    
    jwt_time = now_kst + timedelta(minutes=int(os.environ.get('JWT_TIME')))
    refresh_time = now_kst + timedelta(days=int(os.environ.get('REFRESH_TIME')))
    
    jwt_json = {
        "id": id,
        "exp": jwt_time
    }
    refresh_json = { "exp": refresh_time }
    
    token = jwt.encode(jwt_json, os.environ.get('JWT_KEY'))
    refresh = jwt.encode(refresh_json, os.environ.get('REFRESH_KEY'))

    #TODO refresh 토큰 확인 로직 필요
    # jwt_decoded = jwt.decode(token, os.environ.get('JWT_KEY'))  # dict
    # refresh_decoded = jwt.decode(refresh, os.environ.get('REFRESH_KEY'))  # dict

    return token, refresh


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
    #TODO os.environ.get('SECRET_KEY') 추가할 수 있는지 확인 필요
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
