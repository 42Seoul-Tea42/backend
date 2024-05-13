import gevent.monkey

# Monkey patching을 활성화합니다.
gevent.monkey.patch_all()

from app import create_app
import socketio

socket_io = socketio.Server(
    async_mode="gevent",
    cors_allowed_origins="*",
    logger=True,
)

application = create_app()
application = socketio.WSGIApp(socket_io, application)


if __name__ == "__main__":
    socket_io.run(application, debug=application.config["DEBUG"])
