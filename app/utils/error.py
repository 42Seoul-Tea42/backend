from werkzeug.exceptions import InternalServerError, Unauthorized, HTTPException
import psycopg2
from flask import jsonify, request
from ..db.db import conn
from .const import TokenError, StatusCode


# Error handling
def error_handle(app):
    @app.errorhandler(Exception)
    def handle_exception(error):
        app.logger.error(f"[Exception] {request.path}: ", exc_info=error)
        response = jsonify(
            {
                "message": "Internal Server Error",
            }
        )
        response.status_code = StatusCode.INTERNAL_ERROR
        conn.rollback()
        return response

    @app.errorhandler(psycopg2.Error)
    def handle_database_error(error):
        if isinstance(error, psycopg2.errors.UniqueViolation):
            response = jsonify(
                {
                    "message": "중복 값이 있어 처리할 수 없습니다.",
                }
            )
            response.status_code = StatusCode.BAD_REQUEST
        else:
            app.logger.error(f"[Database Error] {request.path}: ", exc_info=error)
            response = jsonify(
                {
                    "message": "Internal Server Error",
                }
            )
            response.status_code = StatusCode.INTERNAL_ERROR
        conn.rollback()
        return response

    @app.errorhandler(HTTPException)
    def handle_http_exception(error):
        response = error.get_response()

        # 500 error
        if isinstance(error, InternalServerError):
            # 로그 출력
            app.logger.error(f"[500 Error] {request.path}: ", exc_info=error)
            response.data = jsonify(
                {
                    "message": error.description,
                }
            )
        # 401 error
        elif isinstance(error, Unauthorized):
            response.data = jsonify(
                {
                    "message": error.description,
                    "error": (
                        TokenError.REFRESH
                        if request.path == "/user/resetToken"
                        else TokenError.ACCESS
                    ),
                }
            )
        # 그 외 40x, 50x error
        else:
            response.data = jsonify(
                {
                    "message": error.description,
                }
            )

        conn.rollback()
        return response
