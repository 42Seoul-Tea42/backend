from flask import Flask, request
from flask_cors import CORS
from .db.db import PostgreSQLFactory
from .db.mongo import MongoDBFactory
import os
from flask_jwt_extended import JWTManager
from .config import DevelopmentConfig, ProductionConfig, TestingConfig
from .utils.routes import add_routes
from dotenv import load_dotenv
from werkzeug.exceptions import BadRequest

# 환경변수 로드
load_dotenv()


def create_app(test=False):

    app = Flask(__name__)
    CORS(
        app,
        origins=[os.getenv("NEXT_PUBLIC_DOMAIN")],
        expose_headers=["Access-Control-Allow-Origin"],
        supports_credentials=True,
    )

    # routes setting
    add_routes(app)

    # config
    config = os.getenv("FLASK_ENV")
    if config == "prod":
        app.config.from_object(ProductionConfig)
    elif test == True:
        app.config.from_object(TestingConfig)
    else:
        app.config.from_object(DevelopmentConfig)

        @app.before_request
        def log_request_info():
            app.logger.error(f"Request to {request.path} received")

    @app.before_request
    def check_content_type():
        if request.method in ["POST", "PUT", "PATCH"]:
            if not request.is_json:
                raise BadRequest("Content-Type은 'application/json'이어야 합니다.")

    jwt = JWTManager(app)

    from .utils.redisBlockList import redis_jwt_blocklist

    @jwt.token_in_blocklist_loader
    def check_if_token_is_revoked(jwt_header, jwt_payload: dict):
        token = jwt_payload["jti"]
        token_in_redis = redis_jwt_blocklist.get(token)
        return token_in_redis is not None

    # # [Postgresql 디비 재설정 (지웠다가 다시 세팅)] ##################################
    # conn = PostgreSQLFactory.get_connection()
    # with conn.cursor() as cursor:
    #     # Read the content of db_schema.sql
    #     with open("/usr/app/srcs/app/db/db_schema.sql") as f:
    #         db_setup_sql = f.read()
    #     # Execute the database setup logic from the SQL script
    #     cursor.execute(db_setup_sql)
    #     # Commit the changes
    #     conn.commit()
    # print("finish setting up DB (Postgresql) ==================", flush=True)

    # # [DUMMY 만들기] #########################################################

    # # TODO [TEST] dummy data delete
    # from .utils.dummy import Dummy

    # Dummy.create_dummy_user(100, use_fancy_opt=True)
    # print("finish setting up dummy data ==================", flush=True)

    # # [Mongo 디비 재설정 (대화 내용 지우기)] ##################################
    # MongoDBFactory.initialize_collection("tea42", "chat")
    # print("finish setting up DB (Mongo) ==================", flush=True)

    # [Redis 디비 재설정 (로그인 내역 지우기)] ##################################
    from .utils.redisServ import redis_client

    redis_client.flushdb()
    print("finish setting up DB (Redis) ==================", flush=True)

    # ################################################################

    # general error handler
    from .utils.error import error_handle

    error_handle(app)

    @app.route("/")
    def welcome():
        return "Hello there, welcome to Tea42"

    return app
