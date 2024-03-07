from flask import request
from ...wsgi import socket_io
from flask_socketio import emit
from flask_jwt_extended import get_jwt_identity
from ..chat import chatUtils as chatUtils
from ..const import Status

id_sid = dict()
sid_id = dict()
id_friend = dict()

#### connect && disconnect ####

@socket_io.on('connect')
# @jwt_required()
def handle_connect():
    id = 1
    #TODO jwt
    # id = get_jwt_identity()['id']
    user_sid = request.sid

    id_sid[id] = user_sid
    sid_id[user_sid] = id
    print(f'Client {id}:{user_sid} connected')

    # (socket) status 업데이트
    id_friend[id] = chatUtils.get_match_user_list(id)
    for target_id in id_friend[id]:
        update_status(id, target_id, Status.ONLINE)


@socket_io.on('disconnect')
# @jwt_required()
def handle_disconnect():
    id = 1
    #TODO jwt
    # id = get_jwt_identity()['id']

    user_sid = request.sid
    if user_sid == id_sid[id]:
        sid_id.pop(id_sid.pop(id))
    else:
        id_sid.pop(id)
        sid_id.pop(user_sid)

    print(f'Client {id} disconnected')

    # (socket) status 업데이트
    for target_id in id_friend[id]:
        update_status(id, target_id, Status.OFFLINE)


#### alarm ####
def new_match(id, target_id):
    user_sid = id_sid.get(id, None)
    target_sid = id_sid.get(target_id, None)
    
    if user_sid:
        emit('new_match', {'target_id': target_id}, room=user_sid)
    if target_sid:
        emit('new_match', {'target_id': id}, room=target_sid)


def new_fancy(id, target_id):
    target_sid = id_sid.get(target_id, None)
    if target_sid:
        emit('new_match', {'target_id': id}, room=target_sid)
    

def new_history(id):
    user_sid = id_sid.get(id, None)
    if user_sid:
        emit('new_match', room=user_sid)
    


#### chat ####
@socket_io.on('send_message')
# @jwt_required()
def send_message(data):
    sender_id = 1
    #TODO jwt
    # sender_id = get_jwt_identity()['id']
    
    if request.sid == id_sid[id]:
        recver_id = data.get('recver_id')
        message = data.get('message')

        if recver_id and message:
            chatUtils.save_chat(sender_id, recver_id, message)

            recver_sid = id_sid.get(recver_id, None)
            if recver_sid:
                emit('send_message', {'sender_id': sender_id, 'message': message}, room=recver_sid)
        
    # else: # 무시


@socket_io.on('read_message')
# @jwt_required()
def read_message(data):
    recver_id = 1
    #TODO jwt
    # recver_id = get_jwt_identity()['id']
    
    if request.sid == id_sid[id]:
        sender_id = data.get('sender_id')
        sender_sid = id_sid.get(sender_id, None)

        if sender_sid:
            emit('read_message', {'recver_id': recver_id}, room=sender_sid)
        
        #(DB) message read 처리
        chatUtils.read_chat(recver_id, sender_id)


#### update ####
def update_location(id, target_id, longitude, latitude):
    target_sid = id_sid.get(target_id, None)
    if target_sid:
        emit('update_location', { 'target_id': id,
                                 'longitude': longitude,
                                 'latitude': latitude }, room=target_sid)
        

def update_status(id, target_id, status):
    target_sid = id_sid.get(target_id, None)
    if target_sid:
        emit('update_status', { 'target_id': id, 'status': status }, room=target_sid)


def unmatch(id, target_id):
    target_sid = id_sid.get(target_id, None)
    if target_sid:
        emit('unmatch', { 'target_id': id }, room=target_sid)


#### Utils ####
def check_status(target_id):
    if target_id in id_sid:
        return Status.ONLINE
    return Status.OFFLINE