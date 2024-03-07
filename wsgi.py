from app import create_app
from flask_jwt_extended import JWTManager
from flask_socketio import SocketIO

application = create_app()
jwt = JWTManager(application)
socket_io = SocketIO(application)

if __name__ == '__main__':    
    application.run()