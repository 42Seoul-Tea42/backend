from app import redis_client
from .const import RedisOpt
import os


def set_user_info(user):
    id = str(user["id"])

    redis_client.hset(str(id), "longitude", user["longitude"])
    redis_client.hset(str(id), "latitude", user["latitude"])
    redis_client.hset(str(id), "email_check", 1 if user["email_check"] else 0)
    redis_client.hset(
        str(id),
        "profile_check",
        1 if all([user["gender"], user["taste"], user["age"]]) else 0,
    )
    redis_client.hset(str(id), "emoji_check", 1 if user["emoji"] is not None else 0)
    redis_client.hset(str(id), "refresh_jti", user["refresh_jti"])
    redis_client.hset(str(id), "login_id", user["login_id"])
    redis_client.hset(str(id), "email", user["email"])

    # 만료 시간 설정 (refresh token 만료 시간과 동일하게 설정)
    redis_client.expire(str(user["id"]), int(os.getenv("REFRESH_TIME")) * 24 * 60 * 60)


def get_user_info(id, opt):

    if opt == RedisOpt.LOCATION:
        check_fields = ["longitude", "latitude"]
    elif opt == RedisOpt.LOGIN:
        check_fields = [
            "email_check",
            "profile_check",
            "emoji_check",
            "email",
            "login_id",
        ]
    elif opt == RedisOpt.SOCKET:
        check_fields = ["socket_id"]
    else:
        return None

    check_values = redis_client.hmget(str(id), *check_fields)

    # 요청 필드와 값을 딕셔너리로 반환
    if check_values:
        return dict(zip(check_fields, check_values))
    else:
        return None


def update_user_info(id, fields):

    if "longitude" in fields:
        redis_client.hset(str(id), "longitude", fields["longitude"])
    if "latitude" in fields:
        redis_client.hset(str(id), "latitude", fields["latitude"])
    if "email_check" in fields:
        redis_client.hset(str(id), "email_check", fields["email_check"])
    if "gender" in fields and "taste" in fields and "age" in fields:
        redis_client.hset(str(id), "profile_check", 1)
    if "emoji" in fields:
        redis_client.hset(str(id), "emoji_check", 1)
    if "socket_id" in fields:
        redis_client.hset(str(id), "socket_id", fields["socket_id"])
    if "refresh_jti" in fields:
        redis_client.hset(str(id), "refresh_jti", fields["refresh_jti"])
    if "email" in fields:
        redis_client.hset(str(id), "email", fields["email"])
        redis_client.hset(str(id), "email_check", 0)


def delete_user_info(id):
    redis_client.delete(str(id))


### jti ###


def get_refresh_jti_by_id(id):
    return redis_client.hget(str(id), "refresh_jti")


### socket ###


def get_socket_id_by_id(id):
    return redis_client.hget(str(id), "socket_id")


def delete_socket_id_by_id(id):
    redis_client.hdel(str(id), "socket_id")
