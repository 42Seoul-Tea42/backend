import random
from .const import Gender, Tags, Emoji
from ..user.userService import register_dummy, dummy_profile_detail as profile_detail
from ..history.historyService import dummy_fancy as fancy


first_names = (
    "주현준순형재준광식준경민가나다라마바사아자차카타파하민지희반훈상정장주선산인혁"
)
last_names = "홍김이박최장조윤정강오권황송엄채원도"
valid_password = "ASDFasdf0"


class Dummy:

    @staticmethod
    def create_dummy_user(amount, use_fancy_opt=False):
        for i in range(1, amount + 1):
            data = Dummy._generate_dummy_data(i)
            register_dummy(data)

        if use_fancy_opt:
            for i in range(1, amount + 1):
                target_profile = random.sample(list(range(1, amount + 1)), amount // 20)
                target_fancy = random.sample(list(range(1, amount + 1)), amount // 100)

                for target in target_profile:
                    profile_detail(i, target)
                for target in target_fancy:
                    fancy(i, target)

    def _generate_dummy_data(index):
        login_id = f"dummy{index}"
        name = random.choice(first_names) + random.choice(first_names)

        return {
            "login_id": login_id,
            "pw": valid_password,
            "email": f"{login_id}@tea42.com",
            "name": name,
            "last_name": random.choice(last_names),
            "age": random.randint(20, 35),
            "longitude": random.uniform(37.4676, 37.64),
            "latitude": random.uniform(37.4676, 37.64),
            "gender": random.choice([Gender.FEMALE, Gender.MALE]),
            "taste": random.choice([Gender.FEMALE, Gender.MALE, Gender.ALL]),
            "bio": f"안녕하세요 {name}입니다. {index}번째 더미입니다.",
            "tags": random.sample(
                list(range(Tags.MIN, Tags.MAX + 1)), random.randint(4, 13)
            ),
            "hate_tags": [],
            "emoji": random.sample(list(range(Emoji.MIN, Emoji.MAX + 1)), 4),
            "hate_emoji": [],
            "similar": random.choice([True, False]),
        }
