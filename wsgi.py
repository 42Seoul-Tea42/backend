import gevent.monkey

# Monkey patching을 활성화합니다.
gevent.monkey.patch_all()

from app import create_app
import socketio
from app.socket import socketService as socketServ
from gevent.lock import Semaphore
import sys

socket_lock = Semaphore(1)

socket_io = socketio.Server(
    async_mode="gevent",
    cors_allowed_origins="*",
    logger=True,
)

application = create_app()
application = socketio.WSGIApp(socket_io, application)


#### connect && disconnect ####
@socket_io.on("connect")
def handle_connect(sid, environ, auth=None):
    from app.user.userUtils import validation

    if not auth or not auth["id"] or not validation(auth["id"], int):
        print("auth error: ", auth)
        sys.stdout.flush()
        return False

    socketServ.handle_connect(int(auth["id"]), sid)


@socket_io.on("disconnect")
def handle_disconnect(sid):
    socketServ.handle_disconnect(sid)


# #### chat ####
@socket_io.on("send_message")
def send_message(sid, data):
    socketServ.send_message(data, sid)


@socket_io.on("read_message")
def read_message(sid, data):
    socketServ.read_message(data, sid)


if __name__ == "__main__":
    # # [TEST]
    # application = create_app()
    # application = socketio.WSGIApp(socket_io, application)

    socket_io.run(application, debug=application.config["DEBUG"])
