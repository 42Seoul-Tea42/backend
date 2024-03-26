from flask import request
from ...wsgi import socket_io
from flask_socketio import emit
from ..chat import chatUtils as chatUtils
from ..const import Status
from . import socket_service as socketServ
from ..user import userUtils



#### connect && disconnect ####

@socket_io.on('connect')
def handle_connect():
    user_sid = request.sid

    #TODO token 파싱해서 id랑 유효성 검사
    #TODO token 없었을 시의 에러처리(except)
    token = request.args.get('token')

    #TODO 잘못된 token이었을 경우 처리
    #TODO 유효기간 지난 token이었을 경우 refresh로 재요청 처리 필요
    id = userUtils.decode_jwt(token)

    if not id:
        #TODO 유저 없었으면 어떻게 처리..?
        emit('connect', room=user_sid)


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
    if id in socketServ.id_sid:
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
# @jwt_required()
def send_message(data):
    sender_id = 1
    #TODO jwt
    # sender_id = get_jwt_identity()['id']
    
    if request.sid == socketServ.id_sid[sender_id]:
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
    
    if request.sid == socketServ.id_sid[recver_id]:
        sender_id = data.get('sender_id')
        sender_sid = socketServ.id_sid.get(sender_id, None)

        if sender_sid:
            emit('read_message', {'recver_id': recver_id}, room=sender_sid)
        
        #(DB) message read 처리
        chatUtils.read_chat(recver_id, sender_id)
