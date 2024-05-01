from datetime import timedelta
from dotenv import load_dotenv
import os
from .const import MAX_REQUEST_SIZE

# .env 파일 auto load
load_dotenv()

class Config(object):
    TESTING = False
    DEBUG = False
    SECRET_KEY = os.getenv('SECRET_KEY')


    MAX_CONTENT_LENGTH=MAX_REQUEST_SIZE
    
    # JWT 비밀 키
    # 다음 코드를 통해 비밀 키 생성 - python -c 'import os; print(os.urandom(16))'
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY')
    # 알고리즘 종류
    JWT_DECODE_ALGORITHMS = ['HS256']
    # JWT Token을 점검 할 때 확인할 위치
    JWT_TOKEN_LOCATION = ['cookies']
    # JWT Access token의 만료기간
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(minutes=int(os.getenv('ACCESS_TIME')))
    # JWT refresh token의 만료 기간
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=int(os.getenv('REFRESH_TIME')))
    # production이 아닐 경우 secure를 해제
    JWT_COOKIE_SECURE = False
    # csrf 보호 활성화
    JWT_COOKIE_CSRF_PROTECT = True
    # CSRF에 대해 검사하는 메소드 지정
    JWT_CSRF_METHODS = ['POST', 'PUT', 'PATCH', 'DELETE']
    # form에 대한 csrf 체크
    JWT_CSRF_CHECK_FORM = True
    # 이중 제출 토큰이 쿠키에 추가 저장되는지 여부를 제어
    JWT_CSRF_IN_COOKIES = True

class DevelopmentConfig(Config):
    DEBUG = True
    # SQLALCHEMY_DATABASE_URI = f"mysql://{os.getenv('DB_USER')}:" \
    #                           f"{os.getenv('DB_PWD')}@" \
    #                           f"{os.getenv('DB_HOST')}:" \
    #                           f"{os.getenv('DB_PORT')}/" \
    #                           f"{os.getenv('DB_NAME')}?charset=utf8"

class ProductionConfig(Config):
    # https 적용
    JWT_COOKIE_SECURE = True
    # SQLALCHEMY_DATABASE_URI = f"mysql://{os.getenv('DB_PRODUCT_USER')}:" \
    #                           f"{os.getenv('DB_PRODUCT_PWD')}@" \
    #                           f"{os.getenv('DB_PRODUCT_HOST')}:" \
    #                           f"{os.getenv('DB_PRODUCT_PORT')}/" \
    #                           f"{os.getenv('DB_PRODUCT_NAME')}?charset=utf8"

class TestingConfig(Config):
    TESTING = True