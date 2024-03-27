from flask import request
from ...wsgi import socket_io
from flask_socketio import emit
from ..chat import chatUtils as chatUtils
from ..const import Status, SocketErr, EXPIRED_TOKEN
from . import socket_service as socketServ
from ..user import userUtils



#### connect && disconnect ####

@socket_io.on('connect')
def handle_connect():
    user_sid = request.sid

    token = request.args.get('token')
    if not token:
        emit('conn_fail', {'error': SocketErr.NO_TOKEN}, room=user_sid)


    id = userUtils.decode_jwt(token)

    if id is None:
        emit('conn_fail', {'error': SocketErr.BAD_TOKEN}, room=user_sid)
    if id == EXPIRED_TOKEN:
        emit('conn_fail', {'error': SocketErr.EXPIRED_TOKEN}, room=user_sid)
    if not userUtils.get_user_data(id):
        emit('conn_fail', {'error': SocketErr.NO_USER}, room=user_sid)

    socketServ.id_sid[id] = user_sid
    socketServ.sid_id[user_sid] = id
    print(f'Client {id}:{user_sid} connected')

    # (socket) status 업데이트
    socketServ.id_match[id] = chatUtils.get_match_user_list(id)
    for target_id in socketServ.id_match[id]:
        socketServ.update_status(id, target_id, Status.ONLINE)

    emit('connect', room=user_sid)


@socket_io.on('disconnect')
def handle_disconnect():
    user_sid = request.sid
    if user_sid not in socketServ.sid_id:
        print(f'[SOCKET] disconnect :: wrong sid')
        return

    id = socketServ.sid_id[user_sid]
    socketServ.sid_id.pop(user_sid)
    socketServ.id_sid.pop(id)
        
    userUtils.update_last_online(id)
    print(f'Client {id} disconnected')

    # (socket) status 업데이트
    if id in socketServ.id_match:
        for target_id in socketServ.id_match[id]:
            socketServ.update_status(id, target_id, Status.OFFLINE)
        socketServ.id_match.pop(id)


#### chat ####
@socket_io.on('send_message')
def send_message(data):
    user_sid = request.sid
    if user_sid not in socketServ.sid_id:
        print(f'[SOCKET] send_message :: wrong sid')
        return

    sender_id = socketServ.sid_id[user_sid]
    recver_id = data.get('recver_id')
    message = data.get('message')

    if recver_id and message:
        chatUtils.save_chat(sender_id, recver_id, message)

        recver_sid = socketServ.id_sid.get(recver_id, None)
        if recver_sid:
            emit('send_message', {'sender_id': sender_id, 'message': message}, room=recver_sid)


@socket_io.on('read_message')
def read_message(data):
    user_sid = request.sid
    if user_sid not in socketServ.sid_id:
        print(f'[SOCKET] read_message :: wrong sid')
        return

    recver_id = socketServ.sid_id[user_sid]
    sender_id = data.get('sender_id')
    sender_sid = socketServ.id_sid.get(sender_id, None)

    if sender_sid:
        emit('read_message', {'recver_id': recver_id}, room=sender_sid)
    
    #(DB) message read 처리
    chatUtils.read_chat(recver_id, sender_id)
