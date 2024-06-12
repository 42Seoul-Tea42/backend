# from enum import Enum
import pytz

# General
KST = pytz.timezone("Asia/Seoul")
TIME_STR_TYPE = "%Y-%m-%d %H:%M:%S.%f%z"
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
MIN_AGE = 1
MAX_AGE = 100
MAX_DISTANCE = 1_000
MIN_FAME = 0
MAX_FAME = 5

# User
IGNORE_MOVE = 1000  # 1km 이하의 움직임 무시
MIN_PASSWORD_SIZE = 8
MAX_PICTURE_AMOUNT = 5

# Login Id
LOGIN_ID_BLUR_SIZE = 3
LOGIN_ID_MIN_LENGTH = 5


# Redis
class RedisOpt:
    LOCATION = 0
    SOCKET = 1
    LOGIN = 2
    BLOCK = 3
    BAN = 4


class RedisSetOpt:
    UNSET = "0"
    SET = "1"


class Authorization:
    NONE = 0
    EMAIL = 1
    PROFILE = 2
    EMOJI = 3


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
MAX_CHAT = 10


# Taste
class Gender:
    OTHER = 1
    FEMALE = 2
    MALE = 4
    ALL = 7


class EncodeOpt:
    TAGS = 0
    EMOJI = 1


class Tags:
    ALL = 0
    MIN = 1
    MAX = 13
    NONE = 0
    FOOD = 1
    VIDEO = 2
    BOOK = 3
    TRAVEL = 4
    LANGUE = 5
    PETS = 6
    DRINK = 7
    FASHION = 8
    SPORTS = 9
    ART = 10
    IT = 11
    GAME = 12
    SMOKE = 13


class Emoji:
    NONE = 0
    MIN = 1
    MAX = 16
    EMOJI1 = 1  # 카카오프렌즈
    EMOJI2 = 2  # 곰식이
    EMOJI3 = 3  # 옴팡이
    EMOJI4 = 4  # 토심이
    EMOJI5 = 5  # 로버트 곽철이 주니어
    EMOJI6 = 6  # 안아줘요
    EMOJI7 = 7  # 망그러진곰
    EMOJI8 = 8  # 입이삐뚫어진오리
    EMOJI9 = 9  # 오구
    EMOJI10 = 10  # 대학일기
    EMOJI11 = 11  # 잔망루피
    EMOJI12 = 12  # 문상훈
    EMOJI13 = 13  # 오늘의짤
    EMOJI14 = 14  # 내시 이모티콘
    EMOJI15 = 15  # 빵빵이
    EMOJI16 = 16  # 이과티콘


# Report
class Report:
    NONE = 0
    MIN = 1
    MAX = 9
    BULLY = 1
    CONTENT = 2
    FAKE = 3
    SPAM = 4
    MISINFORM = 5
    VIOLATION = 6
    PRIVACY = 7
    SUSPICIOUS = 8
    OTHER = 9
