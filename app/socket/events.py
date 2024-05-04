from flask import request
from ...app import socket_io
from ..chat import chatUtils as chatUtils
from . import socketService as socketServ
from flask_jwt_extended import jwt_required


#### connect && disconnect ####


@jwt_required(refresh=True)
@socket_io.on("connect")
def handle_connect():
    # id = get_jwt_identity()
    # [JWT] delete below
    id = 1
    user_sid = request.sid
    socketServ.handle_connect(id, user_sid)


@socket_io.on("disconnect")
def handle_disconnect():
    user_sid = request.sid
    socketServ.handle_disconnect(user_sid)


#### chat ####
@socket_io.on("send_message")
def send_message(data):
    user_sid = request.sid
    socketServ.send_message(data, user_sid)


@socket_io.on("read_message")
def read_message(data):
    user_sid = request.sid
    socketServ.read_message(data, user_sid)
