import random


# Taste
class Gender:
    OTHER = 1
    FEMALE = 2
    MALE = 4
    ALL = 7


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


first_names = (
    "주현준순형재준광식준형경민가나다라마바사아자차카타파하민지희반훈상정장주선산인혁"
)
last_names = "홍김이박최장조윤정강오권황송엄채원도"


def generate_dummy_data(index):
    login_id = f"dummy{index}"
    email = f"{login_id}@tea42.com"
    name = random.choice(first_names) + random.choice(first_names)
    last_name = random.choice(last_names)
    age = random.randint(18, 39)
    latitude = random.uniform(37.225977, 37.661738)
    longitude = random.uniform(126.838502, 127.205925)
    gender = random.choice([Gender.OTHER, Gender.FEMALE, Gender.MALE])
    taste = random.choice([Gender.FEMALE, Gender.MALE, Gender.ALL])
    bio = f"안녕하세요 {name}입니다"
    tags = random.sample(list(range(Tags.MIN, Tags.MAX + 1)), random.randint(1, 13))
    hate_tags = random.sample(
        list(range(Tags.MIN, Tags.MAX + 1)), random.randint(0, 10)
    )
    emoji = random.sample(list(range(Emoji.MIN, Emoji.MAX + 1)), random.randint(1, 4))
    hate_emoji = random.sample(
        list(range(Emoji.MIN, Emoji.MAX + 1)), random.randint(1, 4)
    )
    similar = random.choice([True, False])

    return {
        "login_id": login_id,
        "pw": "ASDFasdf0",
        "email": email,
        "name": name,
        "last_name": last_name,
        "age": age,
        "longitude": longitude,
        "latitude": latitude,
        "gender": gender,
        "taste": taste,
        "bio": bio,
        "tags": tags,
        "hate_tags": hate_tags,
        "emoji": emoji,
        "hate_emoji": hate_emoji,
        "similar": similar,
    }


if __name__ == "__main__":
    dummies = [generate_dummy_data(i) for i in range(1, 5)]
    for d in dummies:
        print(d)
