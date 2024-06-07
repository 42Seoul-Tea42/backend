from datetime import timedelta
from dotenv import load_dotenv
import os
from .utils.const import MAX_REQUEST_SIZE

# .env 파일 auto load
load_dotenv()


class Config(object):
    TESTING = False
    DEBUG = False
    SECRET_KEY = os.getenv("SECRET_KEY")

    MAX_CONTENT_LENGTH = MAX_REQUEST_SIZE

    # JWT 비밀 키
    # 다음 코드를 통해 비밀 키 생성 - python -c 'import os; print(os.urandom(16))'
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
    # 알고리즘 종류
    JWT_DECODE_ALGORITHMS = ["HS256"]
    # JWT Token을 점검 할 때 확인할 위치
    JWT_TOKEN_LOCATION = ["cookies"]
    # JWT Access token의 만료기간
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(minutes=int(os.getenv("ACCESS_TIME")))
    # JWT refresh token의 만료 기간
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=int(os.getenv("REFRESH_TIME")))
    # https로만 받을건지 체크
    JWT_COOKIE_SECURE = False
    # csrf 보호 활성화

    # JWT_COOKIE_CSRF_PROTECT = True
    JWT_COOKIE_CSRF_PROTECT = False
    # # CSRF에 대해 검사하는 메소드 지정
    # JWT_CSRF_METHODS = ["POST", "PUT", "PATCH", "DELETE"]
    # # form에 대한 csrf 체크
    # JWT_CSRF_CHECK_FORM = True
    # # 이중 제출 토큰이 쿠키에 추가 저장되는지 여부를 제어
    # JWT_CSRF_IN_COOKIES = True

    # Default: None, which is treated as "Lax" by browsers.
    JWT_COOKIE_SAMESITE = "Lax"

    JWT_REFRESH_COOKIE_PATH = "/api/user/reset-token"


class DevelopmentConfig(Config):
    DEBUG = True


class ProductionConfig(Config):
    # https 적용
    JWT_COOKIE_SECURE = True
    PROPAGATE_EXCEPTIONS = True


class TestingConfig(Config):
    TESTING = True
