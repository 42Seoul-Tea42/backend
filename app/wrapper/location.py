from flask import request
from flask_jwt_extended import get_jwt_identity
from ..utils.const import IGNORE_MOVE, RedisOpt
from ..user import userUtils
from ..utils import redisServ
from ..socket import socketServ


def check_location(f):
    def wrapper(*args, **kwargs):
        # TODO [JWT]
        # id = 1
        id = get_jwt_identity()
        redis_user = redisServ.get_user_info(id, RedisOpt.LOCATION)

        # 유저의 위치 정보 가져오기 (long, lat)
        try:
            long = float(request.headers.get("x-user-longitude"))
            lat = float(request.headers.get("x-user-latitude"))
        except Exception:
            lat, long = userUtils.get_location_by_ip(
                request.headers.get("X-Forwarded-For", request.remote_addr),
            )

        # 기존 위치와 거리 비교 => DB & Redis 업데이트
        if (
            userUtils.get_distance(
                redis_user["latitude"], redis_user["longitude"], lat, long
            )
            < IGNORE_MOVE
        ):
            userUtils.update_location(id, lat, long)
            redisServ.update_user_info(id, {"longitude": long, "latitude": lat})
            socketServ.update_distance(id, lat, long)

        return f(*args, **kwargs)

    return wrapper
