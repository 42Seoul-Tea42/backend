from app import redis_jwt_blocklist
import os


def update_block_list(jti, refresh_jti):

    redis_jwt_blocklist.set(jti, "", ex=int(os.environ.get("ACCESS_TIME")))
    redis_jwt_blocklist.set(refresh_jti, "", ex=int(os.environ.get("REFRESH_TIME")))