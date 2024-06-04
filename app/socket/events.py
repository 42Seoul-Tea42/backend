from ..chat import chatUtils as chatUtils
from . import socketService as socketServ
from flask_jwt_extended import jwt_required, get_jwt_identity
from wsgi import socket_io


#### connect && disconnect ####
@jwt_required()
@socket_io.on("connect")
def handle_connect(sid, environ, auth):
    # TODO auth에서 token으로 JWT 검증, id 가져오기 => jwt_required()로 되는듯? 체크 필요
    # if not auth:
    #     return False

    # [JWT] delete below
    # id = 1
    id = get_jwt_identity()
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
