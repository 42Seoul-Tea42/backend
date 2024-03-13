from flask import request
from ...wsgi import socket_io
from flask_socketio import emit
from flask_jwt_extended import get_jwt_identity
from ..chat import chatUtils as chatUtils
from ..const import Status
from . import socket_service as socketServ



#### connect && disconnect ####

@socket_io.on('connect')
# @jwt_required()
def handle_connect():
    id = 1
    #TODO jwt
    # id = get_jwt_identity()['id']
    user_sid = request.sid

    socketServ.id_sid[id] = user_sid
    # socketServ.sid_id[user_sid] = id
    print(f'Client {id}:{user_sid} connected')

    # (socket) status 업데이트
    socketServ.id_match[id] = chatUtils.get_match_user_list(id)
    for target_id in socketServ.id_match[id]:
        socketServ.update_status(id, target_id, Status.ONLINE)


@socket_io.on('disconnect')
# @jwt_required()
def handle_disconnect():
    id = 1
    #TODO jwt
    # id = get_jwt_identity()['id']

    user_sid = request.sid
    if user_sid == socketServ.id_sid[id]:
        socketServ.pop(socketServ.id_sid.pop(id))
    else:
        socketServ.id_sid.pop(id)
        socketServ.pop(user_sid)

    print(f'Client {id} disconnected')

    # (socket) status 업데이트
    for target_id in socketServ.id_match[id]:
        socketServ.update_status(id, target_id, Status.OFFLINE)


#### chat ####
@socket_io.on('send_message')
# @jwt_required()
def send_message(data):
    sender_id = 1
    #TODO jwt
    # sender_id = get_jwt_identity()['id']
    
    if request.sid == socketServ.id_sid[id]:
        recver_id = data.get('recver_id')
        message = data.get('message')

        if recver_id and message:
            chatUtils.save_chat(sender_id, recver_id, message)

            recver_sid = socketServ.id_sid.get(recver_id, None)
            if recver_sid:
                emit('send_message', {'sender_id': sender_id, 'message': message}, room=recver_sid)
        
    # else: # 무시


@socket_io.on('read_message')
# @jwt_required()
def read_message(data):
    recver_id = 1
    #TODO jwt
    # recver_id = get_jwt_identity()['id']
    
    if request.sid == socketServ.id_sid[id]:
        sender_id = data.get('sender_id')
        sender_sid = socketServ.id_sid.get(sender_id, None)

        if sender_sid:
            emit('read_message', {'recver_id': recver_id}, room=sender_sid)
        
        #(DB) message read 처리
        chatUtils.read_chat(recver_id, sender_id)
