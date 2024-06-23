from werkzeug.exceptions import (
    InternalServerError,
    Unauthorized,
    HTTPException,
    Forbidden,
)
import psycopg2
from flask import jsonify, request
from ..db.db import PostgreSQLFactory
from .const import StatusCode


# TODO socket error 처리하기?
# Error handling
def error_handle(app):

    @app.errorhandler(psycopg2.Error)
    def handle_database_error(error):
        conn = PostgreSQLFactory.get_connection()
        if isinstance(error, psycopg2.errors.UniqueViolation):
            response = jsonify(
                {
                    "msg": "중복 값이 있어 처리할 수 없습니다.",
                }
            )
            response.status_code = StatusCode.BAD_REQUEST
        else:
            app.logger.error(f"[Database Error] {request.path}: ", exc_info=error)
            response = jsonify(
                {
                    "msg": "Internal Server Error",
                }
            )
            response.status_code = StatusCode.INTERNAL_ERROR
        conn.rollback()
        return response, response.status_code

    @app.errorhandler(HTTPException)
    def handle_http_exception(error):
        conn = PostgreSQLFactory.get_connection()
        response = error.get_response()

        # 500 error
        if isinstance(error, InternalServerError):
            # 로그 출력
            app.logger.error(f"[500 Error] {request.path}: ", exc_info=error)
            response = jsonify(
                {
                    "msg": error.description,
                }
            )
            response.status_code = StatusCode.INTERNAL_ERROR
        # 401 error
        elif isinstance(error, Unauthorized):
            response = jsonify(
                {
                    "msg": error.description,
                }
            )
            response.status_code = StatusCode.UNAUTHORIZED
        # 403 error
        elif isinstance(error, Forbidden):
            response = jsonify(
                {
                    "msg": error.description,
                }
            )
            response.status_code = StatusCode.FORBIDDEN
        # 그 외 40x, 50x error
        else:
            response = jsonify(
                {
                    "msg": error.description,
                }
            )
            response.status_code = StatusCode.BAD_REQUEST

        conn.rollback()
        return response, response.status_code

    @app.errorhandler(Exception)
    def handle_exception(error):
        conn = PostgreSQLFactory.get_connection()
        app.logger.error(f"[Exception] {request.path}: ", exc_info=error)
        response = jsonify(
            {
                "msg": "Internal Server Error",
            }
        )
        response.status_code = StatusCode.INTERNAL_ERROR
        conn.rollback()
        return response, response.status_code
