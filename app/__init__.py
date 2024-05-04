from flask import Flask
from flask_cors import CORS
from .db import conn
import os
from flask_jwt_extended import JWTManager
from flask_socketio import SocketIO
from .config import DevelopmentConfig
import redis
from .routes import add_routes


# redis 클라이언트 생성
redis_client = redis.StrictRedis(host="redis", port=6379, db=0, decode_responses=True)
redis_jwt_blocklist = redis.StrictRedis(
    host="redis", port=6379, db=1, decode_responses=True
)

# jwt
jwt = JWTManager()


@jwt.token_in_blocklist_loader
def check_if_token_is_revoked(jwt_header, jwt_payload: dict):
    token = jwt_payload["jti"]
    token_in_redis = redis_jwt_blocklist.get(token)
    return token_in_redis is not None


# socket io
socket_io = SocketIO()


def create_app():

    app = Flask(__name__)
    CORS(app)

    # config

    app.config.from_object(DevelopmentConfig)
    add_routes(app)

    # config = app.config.get('ENV')
    # if config == 'production':
    #     app.config.from_object('config.ProductionConfig')
    # elif config == 'testing':
    #     app.config.from_object('config.TestingConfig')
    # else:
    #     app.config.from_object('config.DevelopmentConfig')

    jwt.init_app(app)
    socket_io.init_app(app)

    ################ 하기 내용은 DB 세팅 후 블록처리 해주세요 (백앤드 디버깅 모드)
    # # Create a cursor
    # cursor = conn.cursor()
    # # Read the content of db_schema.sql
    # with open("./app/db_schema.sql") as f:
    #     db_setup_sql = f.read()
    # # Execute the database setup logic from the SQL script
    # cursor.execute(db_setup_sql)
    # # Commit the changes
    # conn.commit()

    # # TODO [TEST] dummy data delete
    # from .user.userService import register_dummy
    # data = {
    #     "login_id": os.environ.get("DUM_ID"),
    #     "pw": os.environ.get("DUM_PW"),
    #     "email": os.environ.get("DUM_EMAIL"),
    #     "name": os.environ.get("DUM_NAME"),
    #     "last_name": os.environ.get("DUM_LAST_NAME"),
    #     "age": os.environ.get("DUM_AGE"),
    #     "longitude": os.environ.get("DUM_LONG"),
    #     "latitude": os.environ.get("DUM_LAT"),
    # }
    # register_dummy(data)

    # # Close the cursor
    # cursor.close()
    ################################################################

    # # general error handler
    # from .common.errors import error_handle
    # error_handle(app)

    @app.route("/")
    def welcome():
        return "Hello there, welcome to Tea42"

    return app
