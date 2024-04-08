from flask import Flask
from flask_restx import Api
from flask_cors import CORS
from .db import conn
from .user.userService import register_dummy
import os

api = Api(
    version='1.0',
    title='tea42',
    prefix='/sw',
    contact_email='tea42fourtwo@gmail.com',
    # doc=False #swagger 표시 안하겠당!
)

def create_app():
        
    app = Flask(__name__)
    CORS(app)

    app.config['MAX_CONTENT_LENGTH'] = 32 * 1024 * 1024 # Set upload directory: 32MB 제한
    app.config['JWT_SECRET_KEY'] = os.environ.get('JWT_KEY')

################ 하기 내용은 DB 세팅 후 블록처리 해주세요 (백앤드 디버깅 모드)
    # Create a cursor
    cursor = conn.cursor()
    # Read the content of db_schema.sql
    with open('./app/db_schema.sql') as f:
        db_setup_sql = f.read()
    # Execute the database setup logic from the SQL script
    cursor.execute(db_setup_sql)
    # Commit the changes
    conn.commit()

    #TODO [TEST] dummy data delete
    data = {
        'login_id': os.environ.get('DUM_ID'),
        'pw': os.environ.get('DUM_PW'),
        'email': os.environ.get('DUM_EMAIL'),
        'name': os.environ.get('DUM_NAME'),
        'last_name': os.environ.get('DUM_LAST_NAME'),
        'birthday': os.environ.get('DUM_BIRTHDAY'),
        'longitude': os.environ.get('DUM_LONG'),
        'latitude': os.environ.get('DUM_LAT'),
    }
    register_dummy(data)

    # Close the cursor
    cursor.close()
################################################################

    api.init_app(app)

    from .user import userController
    api.add_namespace(userController.ns)
    
    from .tea import teaController
    api.add_namespace(teaController.ns)
    
    from .history import historyController
    api.add_namespace(historyController.ns)
    
    from .chat import chatController
    api.add_namespace(chatController.ns)

    from .oauth import kakaoController
    api.add_namespace(kakaoController.ns)
    
    @app.route('/')
    def welcome():
        return 'Hello there, welcome to Tea42'

    return app
