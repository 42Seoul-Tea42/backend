from ..chat import chatUtils as chatUtils
from . import socketService as socketServ
from flask_jwt_extended import jwt_required
from wsgi import socket_io


#### connect && disconnect ####
@jwt_required()
@socket_io.on("connect")
def handle_connect(sid, environ, auth):
    # TODO auth에서 token으로 JWT 검증, id 가져오기
    # if not auth:
    #     return False

    # [JWT] delete below
    # id = 1
    socketServ.handle_connect(id, sid)


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
