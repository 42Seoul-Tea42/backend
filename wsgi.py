from app import create_app
from flask_jwt_extended import JWTManager

application = create_app()
jwt = JWTManager(application)

if __name__ == '__main__':    
    application.run()