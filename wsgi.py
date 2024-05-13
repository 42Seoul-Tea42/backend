from app import create_app
from flask_socketio import SocketIO, emit, disconnect
from flask import request

application = create_app()
socket_io = SocketIO(application, cors_allowed_origins="*")


@socket_io.on_error_default
def default_error_handler(e):
    application.logger.error(f"[SocketIO Error] {request.path}: ", exc_info=e)


@socket_io.on("connect")
def handle_connect():
    socket_uid = request.sid
    application.logger.critical("On: connected")
    print("On: connected")
    print("Socket UID:", socket_uid)
    emit("connect", room=socket_uid)


@socket_io.on("disconnect")
def handle_disconnect():
    socket_uid = request.sid
    application.logger.critical(f"OFFFFFFF {socket_uid}")
    print("OFFFFFFF", socket_uid)


if __name__ == "__main__":
    # application.run()
    socket_io.run(application, debug=True)
