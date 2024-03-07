from flask import Flask
from flask_restx import Api
from flask_cors import CORS
# from .config import Config
from .db import conn
import os

api = Api(
    version='1.0',
    title='tea42',
    prefix='/sw',
    # contact_email='tea42fourtwo@gmail.com',
)

def create_app():
        
    app = Flask(__name__)
    CORS(app)
    # app.config.from_object(Config)
    
    # app.config.from_mapping(
    #     SECRET_KEY = os.environ.get('SECRET_KEY'),
    #     BCRYPT_LOG_ROUNDS = 12,
    #     BCRYPT_LEVEL = int(os.environ.get('BCRYPT_LEVEL'))
    # )

    # # Set upload directory
    app.config['MAX_CONTENT_LENGTH'] = 32 * 1024 * 1024 # 예시: 16MB 제한
    app.config['JWT_SECRET_KEY'] = os.environ.get('JWT_KEY')

    #TODO front에 알려주기 (소켓통신)
    app.config['JWT_TOKEN_LOCATION'] = ['headers', 'query_string']

    # app.config['PROFILE_FOLDER'] = './profile/'
    # app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg'}

################ 하기 내용은 swagger 연결 확인 후 블록처리 해주세요 (스웨거 디버깅 모드여서 백엔드 내용 수정 시 db 계속 초기화됨)
    # Create a cursor
    cursor = conn.cursor()
    # Read the content of db_schema.sql
    with open('./app/db_schema.sql') as f:
        db_setup_sql = f.read()
    # Execute the database setup logic from the SQL script
    cursor.execute(db_setup_sql)
    # Commit the changes
    conn.commit()
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
    

    @app.route('/')
    def welcome():
        return 'Hello there, welcome to Tea42'
    
    return app
