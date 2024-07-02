import gevent.monkey

# Monkey patching을 활성화합니다.
gevent.monkey.patch_all()

from app import create_app
import socketio
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
    if not auth or not auth["id"]:
        print("auth error: ", auth, flush=True)            
        return False
    try:
        int(auth["id"])
    except:
        print("auth error: ", auth, flush=True)
        return False

    from app.socket import socketService as socketServ

    socketServ.handle_connect(int(auth["id"]), sid)


@socket_io.on("disconnect")
def handle_disconnect(sid):
    from app.socket import socketService as socketServ

    socketServ.handle_disconnect(sid)


# #### chat ####
@socket_io.on("send_message")
def send_message(sid, data):
    from app.socket import socketService as socketServ

    socketServ.send_message(data, sid)


@socket_io.on("read_message")
def read_message(sid, data):
    from app.socket import socketService as socketServ

    socketServ.read_message(data, sid)


if __name__ == "__main__":
    # # [TEST]
    # application = create_app()
    # application = socketio.WSGIApp(socket_io, application)

    socket_io.run(application, debug=application.config["DEBUG"])
