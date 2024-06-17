from datetime import datetime
from ..db.mongo import MongoDBFactory
from ..utils.const import UserStatus, RedisOpt, KST, TIME_STR_TYPE, RedisOpt
from ..user import userUtils
from ..utils import redisServ
from ..history import historyUtils
from ..chat import chatUtils as chatUtils
import sys

# match된 유저 저장용 id: set()
id_match = dict()


### connect && disconnect ###
def handle_connect(id, user_sid):
    from wsgi import socket_io

    redis_user = redisServ.get_user_info(id, RedisOpt.LOGIN)
    if redis_user is None:
        socket_io.emit(
            "conn_fail", {"message": "존재하지 않는 유저입니다."}, room=user_sid
        )

    # (redis) user_info 업데이트
    redisServ.update_user_info(id, {"socket_id": user_sid})

    # (redis) socket_id 저장
    socket_io.save_session(user_sid, {"id": id})

    # (socket) status 업데이트
    id_match[id] = historyUtils.get_match_list(id)
    _update_status(socket_io, id, UserStatus.ONLINE, id_match)


def handle_disconnect(user_sid):
    from wsgi import socket_io

    # (socket) status 업데이트
    id = socket_io.get_session(user_sid).get("id", None)
    if id is None:
        return

    _update_status(socket_io, id, UserStatus.OFFLINE, id_match)

    # match 정보 삭제 및 (redis) 데이터 삭제
    if id in id_match:
        id_match.pop(id)
    redisServ.delete_socket_id_by_id(id)

    userUtils.update_last_online(id)


def _update_status(socket_io, id, status, id_match):
    # status 업데이트
    for target_id in id_match.get(id, []):
        target_sid = redisServ.get_socket_id_by_id(target_id)
        if target_sid:
            socket_io.emit(
                "update_status",
                {"target_id": id, "status": status},
                room=target_sid,
            )


### chat ###
def send_message(data, user_sid=None):
    from wsgi import socket_io

    # [Test]
    sender_id = socket_io.get_session(user_sid).get("id", None)
    if sender_id is None:
        return

    # TODO type 검사
    recver_id = data.get("recver_id")  # int
    message = data.get("message")  # str

    if recver_id not in id_match.get(sender_id, set()):
        return

    if recver_id and message.strip():
        msg_time = chatUtils.save_chat(sender_id, recver_id, message)
        recver_sid = redisServ.get_socket_id_by_id(recver_id)
        if recver_sid:
            socket_io.emit(
                "send_message",
                {
                    "sender_id": sender_id,
                    "message": message,
                    "msg_time": msg_time,
                    "msg_new": True,
                },
                room=recver_sid,
            )


def read_message(data, user_sid):
    from wsgi import socket_io

    recver_id = socket_io.get_session(user_sid).get("id", None)
    if recver_id is None:
        return

    # TODO type 검사
    sender_id = data.get("sender_id")  # int
    sender_sid = redisServ.get_socket_id_by_id(sender_id)

    if sender_sid:
        socket_io.emit("read_message", {"recver_id": recver_id}, room=sender_sid)

    # (DB) message read 처리
    chatUtils.read_chat(recver_id, sender_id)


#### alarm ####
def new_match(id, target_id):
    from wsgi import socket_io, socket_lock

    user_sid = redisServ.get_socket_id_by_id(id)
    target_sid = redisServ.get_socket_id_by_id(target_id)

    # MongoDB에 신규 대화 생성
    chatUtils.save_chat(id, target_id, "")

    # socket alarm 발생
    if user_sid:
        id_match.get(id, set()).add(target_id)
        with socket_lock:
            socket_io.emit("new_match", {"target_id": target_id}, room=user_sid)

    if target_sid:
        id_match.get(target_id, set()).add(id)
        with socket_lock:
            socket_io.emit("new_match", {"target_id": id}, room=target_sid)


def new_fancy(id, target_id):
    from wsgi import socket_io, socket_lock

    target_sid = redisServ.get_socket_id_by_id(target_id)
    if target_sid:
        with socket_lock:
            socket_io.emit("new_fancy", {"target_id": id}, room=target_sid)


def new_unfancy(id, target_id):
    from wsgi import socket_io, socket_lock

    target_sid = redisServ.get_socket_id_by_id(target_id)
    if target_sid:
        with socket_lock:
            socket_io.emit("unfancy", {"target_id": id}, room=target_sid)


def new_history(id):
    from wsgi import socket_io, socket_lock

    user_sid = redisServ.get_socket_id_by_id(id)
    if user_sid:
        with socket_lock:
            socket_io.emit("new_history", room=user_sid)


#### update ####
def update_distance(id, lat, long):
    from wsgi import socket_io, socket_lock

    for target_id in id_match.get(id, set()):

        target_sid = redisServ.get_socket_id_by_id(target_id)
        if target_sid:
            target = userUtils.get_user(target_id)
            if target is None:
                continue

            with socket_lock:
                socket_io.emit(
                    "update_distance",
                    {
                        "target_id": id,
                        "distance": userUtils.get_distance(
                            lat, long, target["latitude"], target["longitude"]
                        ),
                    },
                    room=target_sid,
                )


def unmatch(id, target_id):
    from wsgi import socket_io, socket_lock

    if target_id in id_match.get(id, set()):
        id_match[id].remove(target_id)

    if id in id_match.get(target_id, set()):
        id_match[target_id].remove(id)

    user_sid = redisServ.get_socket_id_by_id(id)
    if user_sid:
        with socket_lock:
            socket_io.emit("unmatch", {"target_id": target_id}, room=user_sid)

    target_sid = redisServ.get_socket_id_by_id(target_id)
    if target_sid:
        with socket_lock:
            socket_io.emit("unmatch", {"target_id": id}, room=target_sid)


def unregister(id):
    from wsgi import socket_io, socket_lock

    for target_id in id_match.get(id, set()):
        target_sid = redisServ.get_socket_id_by_id(target_id)
        if target_sid:
            with socket_lock:
                socket_io.emit("unregister", {"target_id": id}, room=target_sid)


#### Utils ####
def check_status(target_id):
    target_status = redisServ.get_user_info(target_id, RedisOpt.SOCKET)
    if target_status["socket_id"] is not None:
        return UserStatus.ONLINE
    return UserStatus.OFFLINE
