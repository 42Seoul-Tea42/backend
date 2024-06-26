from flask import request
from flask_jwt_extended import get_jwt_identity
from ..utils.const import IGNORE_MOVE, RedisOpt
from ..user import userUtils
from ..utils import redisServ
from ..socket import socketService as socketServ
from werkzeug.exceptions import Unauthorized
import os


def check_location(f):
    def wrapper(*args, **kwargs):
        # if os.getenv("PYTEST") == "True":
        #     return f(*args, **kwargs)

        id = get_jwt_identity()
        redis_user = redisServ.get_user_info(id, RedisOpt.LOCATION)
        if redis_user is None or redis_user["longitude"] is None:
            raise Unauthorized("refresh: check_location")

        # 유저의 위치 정보 가져오기 (long, lat)
        long, lat = None, None
        try:
            long = float(request.headers.get("x-user-longitude"))
            lat = float(request.headers.get("x-user-latitude"))
        except Exception:
            lat, long = userUtils.get_location_by_ip(
                request.headers.get("X-Forwarded-For", request.remote_addr),
            )

        # 기존 위치와 거리 비교 => DB & Redis 업데이트
        if (
            IGNORE_MOVE < userUtils.get_distance(
                float(redis_user["latitude"]),
                float(redis_user["longitude"]),
                lat,
                long,
            )
        ):
            userUtils.update_location(id, lat, long)
            redisServ.update_user_info(id, {"longitude": long, "latitude": lat})
            socketServ.update_distance(id, lat, long)

        return f(*args, **kwargs)

    return wrapper
