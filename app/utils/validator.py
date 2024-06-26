import re
from datetime import datetime
from werkzeug.exceptions import BadRequest
from .const import ValidationConst, Gender, Emoji, Tags, Report, TIME_STR_TYPE, KST


class Validator:

    @staticmethod
    def _check_type(value: object, data_type: type, key: str) -> object:
        try:
            return data_type(value)
        except Exception as e:
            raise BadRequest(f"유효하지 않은 값입니다. ({key})")

    @staticmethod
    def _validate_email(email: str) -> str:
        if type(email) is not str:
            raise BadRequest("유효하지 않은 이메일입니다.")

        email = email.strip().lower()

        reg = r"^[a-zA-Z0-9.+_-]{2,}@[a-zA-Z0-9.]{2,}\.[a-zA-Z]{2,3}$"
        if not re.match(reg, email) or ValidationConst.EMAIL_MAX_LENGTH < len(email):
            raise BadRequest("유효하지 않은 이메일입니다.")

        return email

    @staticmethod
    def _validate_login_id(login_id: str) -> str:
        forbidden_login_id_prefixes = (
            "kakao",
            "google",
            "default",
            "tea",
            "admin",
            "root",
        )

        if type(login_id) is not str:
            raise BadRequest("유효하지 않은 로그인 아이디입니다.")

        login_id = login_id.strip().lower()

        reg = rf"^[a-zA-Z0-9]{{{ValidationConst.LOGIN_ID_MIN_LENGTH},{ValidationConst.LOGIN_ID_MAX_LENGTH}}}$"
        if (
            not re.match(reg, login_id)
            or login_id.startswith(forbidden_login_id_prefixes)
            or re.search(r"[\uAC00-\uD7AF]", login_id)
        ):
            raise BadRequest("유효하지 않은 로그인 아이디입니다.")

        return login_id

    @staticmethod
    def _validate_password(pw: str) -> str:
        if type(pw) is not str:
            raise BadRequest("유효하지 않은 비밀번호입니다.")

        if (
            len(pw) < ValidationConst.PASSWORD_MIN_LENGTH
            or ValidationConst.PASSWORD_MAX_LENGTH < len(pw)
            or not re.search(r"[A-Z]", pw)
            or not re.search(r"[a-z]", pw)
            or not re.search(r"\d", pw)
            or re.search(r"[\uAC00-\uD7AF]", pw)
        ):
            raise BadRequest("유효하지 않은 비밀번호입니다.")

        return pw

    @staticmethod
    def _validate_name(name: str) -> str:
        if type(name) is not str:
            raise BadRequest("유효하지 않은 이름입니다.")

        name = name.strip()

        if len(
            name
        ) < ValidationConst.NAME_MIN_LENGTH or ValidationConst.NAME_MAX_LENGTH < len(
            name
        ):
            raise BadRequest("유효하지 않은 이름입니다.")

        return name

    @staticmethod
    def _validate_age(str_age: str) -> int:
        if type(str_age) is not str and type(str_age) is not int:
            raise BadRequest("유효하지 않은 나이입니다.")

        age = Validator._check_type(str_age, int, "age")
        if age < ValidationConst.AGE_MIN or ValidationConst.AGE_MAX < age:
            raise BadRequest("유효하지 않은 나이입니다.")

        return age

    @staticmethod
    def _validate_gender(str_gender: str) -> int:
        if type(str_gender) is not str and type(str_gender) is not int:
            raise BadRequest("유효하지 않은 성별 값입니다.")

        gender = Validator._check_type(str_gender, int, "gender")

        if gender not in (Gender.OTHER, Gender.FEMALE, Gender.MALE):
            raise BadRequest("유효하지 않은 성별 값입니다.")

        return gender

    @staticmethod
    def _validate_taste(str_taste: str) -> int:
        if type(str_taste) is not str and type(str_taste) is not int:
            raise BadRequest("유효하지 않은 취향 값입니다.")

        taste = Validator._check_type(str_taste, int, "taste")

        if taste not in (Gender.ALL, Gender.FEMALE, Gender.MALE):
            raise BadRequest("유효하지 않은 취향 값입니다.")

        return taste

    @staticmethod
    def _validate_bio(bio: str) -> str:
        if type(bio) is not str:
            raise BadRequest("유효하지 않은 자기소개입니다.")

        if ValidationConst.BIO_MAX_LENGTH < len(bio):
            raise BadRequest("자기소개가 너무 길어요. (500자 이내로 작성해주세요)")

        return bio

    @staticmethod
    def _validate_tags(tags):
        if type(tags) is not list:
            raise BadRequest("올바르지 않은 태그 값입니다.")

        for i, str_tag in enumerate(tags):
            tags[i] = Validator._check_type(str_tag, int, "tags")
            if tags[i] < Tags.MIN or Tags.MAX < tags[i]:
                raise BadRequest("올바르지 않은 태그 값입니다.")
        return tags

    @staticmethod
    def _validate_emoji(emoji):
        if type(emoji) is not list:
            raise BadRequest("올바르지 않은 이모티콘 값입니다.")

        for i, str_emoji in enumerate(emoji):
            emoji[i] = Validator._check_type(str_emoji, int, "emoji")
            if emoji[i] < Emoji.MIN or Emoji.MAX < emoji[i]:
                raise BadRequest("올바르지 않은 이모티콘 값입니다.")
        return emoji

    @staticmethod
    def _validate_similar(similar) -> bool:
        if type(similar) is bool:
            return similar
        elif type(similar) is str:
            similar = similar.lower()
            if similar == "true":
                return True
            elif similar == "false":
                return False
            else:
                raise BadRequest("2: 올바르지 않은 similar 값입니다.")
        else:
            raise BadRequest("1: 올바르지 않은 similar 값입니다.")

    @staticmethod
    def _validate_distance(str_distance: str) -> int:
        if type(str_distance) is not str and type(str_distance) is not int:
            raise BadRequest("올바르지 않은 거리 값입니다.")

        distance = Validator._check_type(str_distance, int, "distance")

        if (
            distance < ValidationConst.DISTANCE_MIN
            or ValidationConst.DISTANCE_MAX < distance
        ):
            raise BadRequest("올바르지 않은 거리 값입니다.")

        return distance

    @staticmethod
    def _validate_fame(str_fame: str) -> int:
        if type(str_fame) is not str and type(str_fame) is not int:
            raise BadRequest("올바르지 않은 fame 값입니다.")

        fame = Validator._check_type(str_fame, int, "fame")

        if fame < ValidationConst.FAME_MIN or ValidationConst.FAME_MAX < fame:
            raise BadRequest("올바르지 않은 fame 값입니다.")

        return fame

    @staticmethod
    def _validate_id(str_id: str) -> int:
        if type(str_id) is not str and type(str_id) is not int:
            raise BadRequest("올바르지 않은 target_id 값입니다.")

        id = Validator._check_type(str_id, int, "target_id")
        if id < ValidationConst.TARGET_ID_MIN:
            raise BadRequest("올바르지 않은 target_id 값입니다.")

        return id

    @staticmethod
    def _validate_reason(str_reason: str) -> int:
        if type(str_reason) is not str and type(str_reason) is not int:
            raise BadRequest("올바르지 않은 신고 값입니다.")

        reason = Validator._check_type(str_reason, int, "reason")
        if reason < Report.MIN or Report.MAX < reason:
            raise BadRequest("올바르지 않은 신고 값입니다.")

        return reason

    @staticmethod
    def _validate_reason_opt(reason_opt: str) -> str:
        if reason_opt is None or reason_opt == "":
            return None

        if type(reason_opt) is not str:
            raise BadRequest("올바르지 않은 신고 이유입니다.")

        reason_opt = reason_opt.strip()
        if len(reason_opt) < ValidationConst.REASON_OPT_MIN:
            raise BadRequest("좀 더 자세히 기재해주시면 분석에 도움이 됩니다.")
        if ValidationConst.REASON_OPT_MAX < len(reason_opt):
            raise BadRequest("신고 이유를 200자 이하로 기재해주세요.")

        return reason_opt

    @staticmethod
    def _validate_time(str_time: str) -> datetime:
        if type(str_time) is not str:
            raise BadRequest("기준 시간이 유효하지 않습니다.")

        try:
            return datetime.strptime(str_time, TIME_STR_TYPE).astimezone(KST)
        except ValueError:
            raise BadRequest("기준 시간이 유효하지 않습니다.")

    @staticmethod
    def _validate_str(value: str) -> str:
        if type(value) is not str:
            raise BadRequest("올바르지 않은 값입니다.")
        if len(value) != ValidationConst.KEY_LENGTH:
            raise BadRequest("올바르지 않은 값입니다.")

        return value

    func = {
        "email": _validate_email,
        "login_id": _validate_login_id,
        "pw": _validate_password,
        "name": _validate_name,
        "last_name": _validate_name,
        "age": _validate_age,
        "gender": _validate_gender,
        "taste": _validate_taste,
        "bio": _validate_bio,
        "tags": _validate_tags,
        "hate_tags": _validate_tags,
        "emoji": _validate_emoji,
        "hate_emoji": _validate_emoji,
        "similar": _validate_similar,
        "min_age": _validate_age,
        "max_age": _validate_age,
        "distance": _validate_distance,
        "fame": _validate_fame,
        "target_id": _validate_id,
        "reason": _validate_id,
        "reason_opt": _validate_reason_opt,
        "time": _validate_time,
        "key": _validate_str,
    }

    @staticmethod
    def validate(data) -> dict:
        result = dict()

        for key, value in data.items():
            if not value:
                if key in ("reason_opt", "fame", "tags"):
                    result[key] = value
                    continue
                raise BadRequest(f"Validation Error: 값이 없습니다. ({key})")

            if key in Validator.func:
                result[key] = Validator.func[key](value)
            else:
                raise BadRequest(f"Validation Error: 잘못된 키 값입니다. ({key})")

        if (
            "reason" in result
            and result["reason"] == Report.MAX
            and ("reason_opt" not in result or not result["reason_opt"])
        ):
            raise BadRequest("신고 이유를 입력해주세요.")

        return result

    @staticmethod
    def validate_setting(data) -> dict:
        result = dict()

        for key, value in data.items():
            if not value:
                if key == "pw":
                    continue
                if key in (
                    "tags",
                    "emoji",
                    "hate_tags",
                    "hate_emoji",
                    "bio",
                    "similar",
                ):
                    result[key] = value
                    continue
                raise BadRequest(f"Validation Error: 값이 없습니다. ({key})")

            if key in Validator.func:
                result[key] = Validator.func[key](value)
            elif key == "pictures":
                result[key] = value
            else:
                raise BadRequest(f"Validation Error: 잘못된 키 값입니다. ({key})")

        if not result:
            raise BadRequest("수정할 값이 없습니다.")

        return result
