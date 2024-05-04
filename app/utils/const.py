# from enum import Enum

# General
KST = "Asia/Seoul"
PICTURE_DIR = "/usr/app/srcs/app/profile/"
DEFAULT_PICTURE = "default.png"
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg"}
MAX_REQUEST_SIZE = 5 * 1024 * 1024  # 5MB


class StatusCode:
    OK = 200
    REDIRECTION = 302
    BAD_REQUEST = 400
    UNAUTHORIZED = 401
    FORBIDDEN = 403
    INTERNAL_ERROR = 500


class TokenError:
    ACCESS = 0
    REFRESH = 1


# Search Result
MAX_SEARCH = 16  # max result limit
DAYS = 365  # age calculation
EARTH_RADIUS = 6_371_000  # (m)
DISTANCE = 1_000  # distance(km)
MIN_AGE = 19
MAX_AGE = 100
MAX_DISTANCE = 1_000
MIN_FAME = 0
MAX_FAME = 5

# User
IGNORE_MOVE = 1000  # 1km 이하의 움직임 무시
MIN_PASSWORD_SIZE = 8
MAX_PICTURE_AMOUNT = 5


# Redis
class RedisOpt:
    LOCATION = 0
    SOCKET = 1
    LOGIN = 2


# Oauth
class Oauth:
    NONE = 0
    KAKAO = 1
    GOOGLE = 2


# KaKao
class Kakao:
    REDIRECT_URI = "/kakao/redirect"
    AUTH_URI = "https://kauth.kakao.com/oauth/authorize"
    TOKEN_URI = "https://kauth.kakao.com/oauth/token"
    DATA_URI = "https://kapi.kakao.com/v2/user/me"


class UserStatus:
    OFFLINE = 0
    ONLINE = 1


BAD_TOKEN = None


class JWT:
    ACCESS = 0
    REFRESH = 1


# User_Email option
class Key:
    NONE = 0
    EMAIL = 1
    PASSWORD = 2


# History
MAX_HISTORY = 16


class FancyOpt:
    ADD = 0
    DEL = 1


class History:
    FANCY = 0
    HISTORY = 1


class Fancy:
    NONE = 0
    SEND = 1
    RECV = 2
    CONN = 3


# Tea Suggestions
MAX_SUGGEST = 5
AGE_GAP = 5
AREA_DISTANCE = 500  # 500m

# Chat / Socket
FIRST_CHAT = 0
MAX_CHAT = 30


# Taste
class Gender:
    OTHER = 1
    FEMALE = 2
    MALE = 4
    ALL = 7


class Tags:
    NONE = 0
    SPORTS = 1
    TRAVEL = 1 << 1
    FOOD = 1 << 2
    GAME = 1 << 3
    BOOK = 1 << 4
    IT = 1 << 5
    VIDEO = 1 << 6
    LANGUE = 1 << 7
    FASHION = 1 << 8
    PETS = 1 << 9
    ART = 1 << 10
    SMOKE = 1 << 11
    DRINK = 1 << 12
    ALL = -1


class Emoji:
    NONE = 0
    EMOJI1 = 1  # 카카오프렌즈
    EMOJI2 = 1 << 1  # 곰식이
    EMOJI3 = 1 << 2  # 옴팡이
    EMOJI4 = 1 << 3  # 토심이
    EMOJI5 = 1 << 4  # 로버트 곽철이 주니어
    EMOJI6 = 1 << 5  # 안아줘요
    EMOJI7 = 1 << 6  # 망그러진곰
    EMOJI8 = 1 << 7  # 입이삐뚫어진오리
    EMOJI9 = 1 << 8  # 오구
    EMOJI10 = 1 << 9  # 대학일기
    EMOJI11 = 1 << 10  # 잔망루피
    EMOJI12 = 1 << 11  # 문상훈
    EMOJI13 = 1 << 12  # 오늘의짤
    EMOJI14 = 1 << 13  # 내시 이모티콘
    EMOJI15 = 1 << 14  # 빵빵이
    EMOJI16 = 1 << 15  # 이과티콘


# Report
class Report:
    NONE = 0
    BULLY = 1
    CONTENT = 2
    FAKE = 3
    SPAM = 4
    MISINFORM = 5
    VIOLATION = 6
    PRIVACY = 7
    SUSPICIOUS = 8
    OTHER = 9
