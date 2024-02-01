from app.db import conn
from app.const import Key
from app.smtp import sendSmtpEmail
import os
import re
import hashlib
from psycopg2.extras import DictCursor


def createJwt(id):
    jwt = 'temporaryJWT'
    refresh = 'temporaryREFRESH'
    #TODO jwt 발급 로직 필요
    return jwt


def createEmailKey(login_id):   
    #TODO email key 생성 (random 값으로 key만들어서 링크 생성)
    random_key = 'asdf' + login_id

    return random_key


def encodeBit(data) -> int:
    result = 0

    #TODO logic 체크
    for n in list(data):
        result |= n

    return result


def decodeBit(n) -> list:
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



def hashing(password):
    #sha256방식
    m = hashlib.sha256()
    m.update(password.encode('utf-8'))
    m.update(os.environ.get('SECRET_KEY').encode('utf-8'))

    return m.hexdigest()


def isValidPassword(password, hashed):
    if hashing(password) == hashed:
        return True
    return False


def getFameRate(id) -> float:
    cursor = conn.cursor(cursor_factory=DictCursor)
    sql = 'SELECT * FROM "User" WHERE "id" = %s;'
    cursor.execute(sql, (id, ))
    user = cursor.fetchone()
    
    if not user:
        raise ValueError('no such user: getFameRate')
    
    return user['count_fancy'] / user['count_view'] * 10