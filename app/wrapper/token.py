from functools import wraps
from flask import request, make_response
from ..user import userUtils
from ..const import JWT, StatusCode
from app.db import conn
from psycopg2.extras import DictCursor


def custom_jwt_required():
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):

            user_id = userUtils.decode_jwt(
                request.cookies.get("access_token"), JWT.ACCESS
            )

            if user_id is not None:
                if userUtils.get_user(user_id) is not None:
                    return func(user_id, *args, **kwargs)

                response = make_response("", StatusCode.UNAUTHORIZED)
                response.delete_cookie("access_token")
                response.delete_cookie("refresh_token")
                return response

            else:
                refresh_token = request.cookies.get("refresh_token")
                user_id = userUtils.decode_jwt(refresh_token, JWT.REFRESH)

                if not user_id:
                    return {
                        "message": "Unauthorized refresh token",
                    }, StatusCode.UNAUTHORIZED

                with conn.cursor(cursor_factory=DictCursor) as cursor:
                    sql = 'SELECT "refresh" FROM "User" WHERE "id" = %s AND "refresh" = %s;'
                    cursor.execute(sql, (user_id, refresh_token))
                    user = cursor.fetchone()

                    if not user:
                        return {
                            "message": "Unauthorized refresh token",
                        }, StatusCode.UNAUTHORIZED

                new_access_token = userUtils.generate_jwt(refresh_token)

                # TODO [TEST 필요]
                # 생성한 access token을 쿠키에 설정
                response = make_response(func(user["id"], *args, **kwargs))
                response.set_cookie("access_token", new_access_token)
                return response

        return wrapper

    return decorator
