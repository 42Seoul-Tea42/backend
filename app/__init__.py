from flask import Flask, request
from flask_cors import CORS
from .db.db import PostgreSQLFactory
import os
from flask_jwt_extended import JWTManager
from .config import DevelopmentConfig, ProductionConfig, TestingConfig
import redis
from .utils.routes import add_routes
from dotenv import load_dotenv
from .utils.const import Tags, Emoji, Gender

# 환경변수 로드
load_dotenv()


# redis 클라이언트 생성
redis_client = redis.StrictRedis(
    host=os.getenv("REDIS_HOST"),
    port=int(os.getenv("REDIS_PORT")),
    db=0,
    decode_responses=True,
)
redis_jwt_blocklist = redis.StrictRedis(
    host=os.getenv("REDIS_HOST"),
    port=int(os.getenv("REDIS_PORT")),
    db=1,
    decode_responses=True,
)


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

    jwt = JWTManager(app)

    @jwt.token_in_blocklist_loader
    def check_if_token_is_revoked(jwt_header, jwt_payload: dict):
        token = jwt_payload["jti"]
        token_in_redis = redis_jwt_blocklist.get(token)
        return token_in_redis is not None

    ################ 하기 내용은 DB 세팅 후 블록처리 해주세요 (백앤드 디버깅 모드)
    # # Create a cursor
    # conn = PostgreSQLFactory.get_connection()
    # cursor = conn.cursor()
    # # Read the content of db_schema.sql
    # with open("./app/db/db_schema.sql") as f:
    #     db_setup_sql = f.read()
    # # Execute the database setup logic from the SQL script
    # cursor.execute(db_setup_sql)
    # # Commit the changes
    # conn.commit()

    # # TODO [TEST] dummy data delete
    # from .user.userService import register_dummy
    # from tests.dummy_data import dummy_data

    # for data in dummy_data:
    #     register_dummy(data)

    # # Close the cursor
    # cursor.close()
    ################################################################

    # general error handler
    from .utils.error import error_handle

    error_handle(app)

    @app.route("/")
    def welcome():
        return "Hello there, welcome to Tea42"

    return app
