from enum import Enum

# Search Result
MAX_SEARCH = 16     #max result limit
DAYS = 365          #age calculation
DISTANCE = 1_000    #distance(km)

# History
MAX_HISTORY = 16
class History(Enum):
    FANCY = 0
    HISTORY = 1

# Key generate option
class Key(Enum):
    EMAIL = 0
    PASSWORD = 1

# Tea Suggestions
MAX_SUGGEST = 5
AGE_GAP = 5
AREA_DISTANCE = 500 #500m

# Chat
FIRST = 0
MAX_CHAT = 20

class Gender(Enum):
    OTHER = 1
    FEMALE = 2
    MALE = 4
    ALL = 7

class Status(Enum):
    OFFLINE = 0
    ONLINE = 1

class Fancy(Enum):
    NONE = 0
    SEND = 1
    RECV = 2
    CONN = 3

class Tags(Enum):
    NONE = 0
    SPORTS = 1
    TRAVEL = 2
    FOOD = 2 ** 2
    GAME = 2 ** 3
    BOOK = 2 ** 4
    IT = 2 ** 5
    VIDEO = 2 ** 6
    LANGUE = 2 ** 7
    FASHION = 2 ** 8
    PETS = 2 ** 9
    ART = 2 ** 10
    SMOKE = 2 ** 11
    DRINK = 2 ** 12


class Emoji(Enum):
    NONE = 0
    EMOJI1 = 1 # 내시 이모티콘
    EMOJI2 = 2 # 곰식이
    EMOJI3 = 2 ** 2 # 입이삐뚫어진오리
    EMOJI4 = 2 ** 3 # 로버트 곽철이 주니어
    EMOJI5 = 2 ** 4 # 잔망루피
    EMOJI6 = 2 ** 5 # 문상훈
    EMOJI7 = 2 ** 6 # 빵빵이
    EMOJI8 = 2 ** 7 # 토심이
    EMOJI9 = 2 ** 8 # 이과티콘
    EMOJI10 = 2 ** 9 # 옴팡이
    EMOJI11 = 2 ** 10 # 오구
    EMOJI12 = 2 ** 11 # 대학일기
    EMOJI13 = 2 ** 12 # 오늘의짤
    EMOJI14 = 2 ** 13 # 안아줘요
    EMOJI15 = 2 ** 14 # 망그러진곰
    EMOJI16 = 2 ** 15 # 카카오프렌즈