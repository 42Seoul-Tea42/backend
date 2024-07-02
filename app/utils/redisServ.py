# from app import redis_client
from .const import RedisOpt
from ..user import userUtils
import os, json
import redis

redis_client = redis.StrictRedis(
    host=os.getenv("REDIS_HOST"),
    port=int(os.getenv("REDIS_PORT")),
    db=0,
    decode_responses=True,
)


def set_user_info(user):
    str_id = str(user["id"])

    redis_client.hset(str_id, "longitude", user["longitude"])
    redis_client.hset(str_id, "latitude", user["latitude"])
    redis_client.hset(str_id, "email_check", 1 if user["email_check"] else 0)
    redis_client.hset(
        str_id,
        "profile_check",
        1 if all([user["gender"], user["taste"], user["age"]]) else 0,
    )
    redis_client.hset(str_id, "emoji_check", 1 if user["emoji"] is not None else 0)
    redis_client.hset(str_id, "refresh_token", user["refresh_token"])
    redis_client.hset(str_id, "refresh_jti", user["refresh_jti"])
    redis_client.hset(str_id, "email", user["email"])

    block = userUtils.get_block_list(user["id"])
    ban = userUtils.get_ban_list(user["id"])
    redis_client.hset(str_id, "block", json.dumps(block))
    redis_client.hset(str_id, "ban", json.dumps(ban))

    # 만료 시간 설정 (refresh token 만료 시간과 동일하게 설정)
    redis_client.expire(str_id, int(os.getenv("REFRESH_TIME")) * 24 * 60 * 60)


def get_user_info(id, opt):
    str_id = str(id)
    if not redis_client.exists(str_id):
        return None

    if opt == RedisOpt.LOCATION:
        check_fields = ["longitude", "latitude"]
    elif opt == RedisOpt.LOGIN:
        check_fields = [
            "email_check",
            "profile_check",
            "emoji_check",
            "email",
        ]
    elif opt == RedisOpt.BLOCK:
        if redis_client.hget(str_id, "block") is None:
            return set()
        return set(json.loads(redis_client.hget(str_id, "block")))
    elif opt == RedisOpt.BAN:
        if redis_client.hget(str_id, "ban") is None:
            return set()
        return set(json.loads(redis_client.hget(str_id, "ban")))
    else:
        return None

    check_values = redis_client.hmget(str_id, *check_fields)

    # 요청 필드와 값을 딕셔너리로 반환
    if check_values:
        return dict(zip(check_fields, check_values))
    else:
        return None


def update_user_info(id, fields):
    str_id = str(id)
    if redis_client.exists(str_id):
        if "longitude" in fields:
            redis_client.hset(str_id, "longitude", fields["longitude"])
        if "latitude" in fields:
            redis_client.hset(str_id, "latitude", fields["latitude"])
        if "email_check" in fields:
            redis_client.hset(str_id, "email_check", fields["email_check"])
        if "gender" in fields and "taste" in fields and "age" in fields:
            redis_client.hset(str_id, "profile_check", 1)
        if "emoji" in fields:
            redis_client.hset(str_id, "emoji_check", 1)
        
        if "refresh_jti" in fields:
            redis_client.hset(str_id, "refresh_jti", fields["refresh_jti"])

        if "email" in fields:
            redis_client.hset(str_id, "email", fields["email"])
            redis_client.hset(str_id, "email_check", 0)

        if "block" in fields:
            prev_block = redis_client.hget(str_id, "block")
            if prev_block:
                block = json.loads(prev_block)
                block.append(fields["block"])
                redis_client.hset(id, "block", json.dumps(block))
            else:
                redis_client.hset(id, "block", json.dumps([fields["block"]]))

        if "ban" in fields:
            prev_ban = redis_client.hget(str_id, "ban")
            if prev_ban:
                ban = json.loads(prev_ban)
                ban.append(fields["ban"])
                redis_client.hset(id, "ban", json.dumps(ban))
            else:
                redis_client.hset(id, "ban", json.dumps([fields["ban"]]))


def delete_user_info(id):
    redis_client.delete(str(id))


### jti ###
def get_refresh_token_by_id(id):
    return redis_client.hget(str(id), "refresh_token")


def get_refresh_jti_by_id(id):
    return redis_client.hget(str(id), "refresh_jti")
    

# # Redis user schema (db=0)
# {
#     "user_id": {
#         # 유저 위치 정보
#         "longitude": "string",
#         "latitude": "string",
#         # 유저 설정 정보 (서비스 이용 권한 확인용)
#         "email_check": "integer (0 or 1)",
#         "profile_check": "integer (0 or 1)",
#         "emoji_check": "integer (0 or 1)",
#         # 유저 refresh token 정보
#         "refresh_jti": "string",
#         # 유저 정보
#         "email": "string",
#         # 유저 차단 및 차단된 정보
#         "block": "JSON string (array of blocked user IDs)",
#         "ban": "JSON string (array of banned user IDs)",
#     }
# }
