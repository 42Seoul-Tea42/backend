from app import redis_client
from .const import RedisOpt


def set_user_info(user):

    redis_client.hmset(
        str(user["id"]),
        {
            "longitude": user["longitude"],
            "latitude": user["latitude"],
            "email_check": user["email_check"],
            "profile_check": (
                1 if all(user["gender"], user["taste"], user["age"]) else 0
            ),
            "emoji_check": 1 if user["emoji"] is not None else 0,
        },
    )


def get_user_info(id, opt):

    if opt == RedisOpt.LOCATION:
        check_fields = ["longitude", "latitude"]
    elif opt == RedisOpt.LOGIN:
        check_fields = ["email_check", "profile_check", "emoji_check"]
    elif opt == RedisOpt.SOCKET:
        check_fields = ["socket_id"]

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


def set_socket_info(socket_id, id):
    redis_client.set(socket_id, id)


def get_id_by_socket_id(socket_id):
    return redis_client.get(socket_id)


def delete_socket_info(socket_id):
    redis_client.delete(socket_id)


### location ###


def get_user_location(id):
    # 사용자의 위치 정보를 가져옴
    location_fields = ["longitude", "latitude"]
    location_values = redis_client.hmget(str(id), *location_fields)

    # 위치 필드와 값을 딕셔너리로 반환
    location_data = dict(zip(location_fields, location_values))
    return location_data
