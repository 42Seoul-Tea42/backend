from datetime import datetime
from ..db.mongo import MongoDBFactory
from ..utils.const import UserStatus, RedisOpt, KST, TIME_STR_TYPE, RedisOpt
from ..user import userUtils
from ..utils import redisServ
from ..history import historyUtils
from ..chat import chatUtils as chatUtils
from wsgi import socket_io, socket_lock
import sys

# match된 유저 저장용 id: set()
id_match = dict()


### connect && disconnect ###
def handle_connect(id, user_sid):

    redis_user = redisServ.get_user_info(id, RedisOpt.LOGIN)
    if redis_user is None or redis_user["email"] is None:
        socket_io.emit("conn_fail", {"msg": "존재하지 않는 유저입니다."}, room=user_sid)

    # (redis) user_info 업데이트
    redisServ.update_user_info(id, {"socket_id": user_sid})

    # (redis) socket_id 저장
    socket_io.save_session(user_sid, {"id": id})

    # (socket) status 업데이트
    if id not in id_match:
        id_match[id] = historyUtils.get_match_list(id)
        _update_status(socket_io, id, UserStatus.ONLINE, id_match)

    # (socket) 로그아웃 중 발생한 이벤트 처리
    user = userUtils.get_user(id)
    if user["is_fancy"] or user["is_visitor"] or user["is_match"]:
        with socket_lock:
            if user["is_fancy"]:
                socket_io.emit("new_fancy", {"target_id": id}, room=user_sid)
            if user["is_visitor"]:
                socket_io.emit("new_visitor", room=user_sid)
            if user["is_match"]:
                socket_io.emit("new_match", {"target_id": id}, room=user_sid)
        userUtils.update_event(id)


def handle_disconnect(user_sid):

    # (socket) status 업데이트
    id = socket_io.get_session(user_sid).get("id", None)
    if id is None:
        return

    # match 정보 삭제 및 (redis) 데이터 삭제
    if id in id_match:
        id_match.pop(id)
    if redisServ.delete_socket_id_by_id(id, user_sid):
        # redis에서 유저 삭제 시에만 offline 처리
        _update_status(socket_io, id, UserStatus.OFFLINE, id_match)

    userUtils.update_last_online(id)


def _update_status(socket_io, id, status, id_match):
    # status 업데이트
    for target_id in id_match.get(id, []):
        target_sid_set = redisServ.get_user_info(target_id, RedisOpt.SOCKET)
        for target_sid in target_sid_set:
            with socket_lock:
                socket_io.emit(
                    "update_status",
                    {"target_id": id, "status": status},
                    room=target_sid,
                )


### chat ###
def send_message(data, user_sid=None, sender_id=None):
    # [Pytest]
    if sender_id is None:
        sender_id = socket_io.get_session(user_sid).get("id", None)
        if sender_id is None:
            return

    # TODO type 검사
    recver_id = data.get("recver_id")  # int
    message = data.get("message")  # str

    if sender_id not in id_match.get(recver_id, set()):
        return

    if recver_id and message.strip():
        msg_time = chatUtils.save_chat(sender_id, recver_id, message)

        recver_sid_set = redisServ.get_user_info(recver_id, RedisOpt.SOCKET)
        for recver_sid in recver_sid_set:
            with socket_lock:
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
    recver_id = socket_io.get_session(user_sid).get("id", None)
    if recver_id is None:
        return

    # TODO type 검사
    sender_id = data.get("sender_id")  # int
    sender_sid_set = redisServ.get_user_info(sender_id, RedisOpt.SOCKET)
    for sender_sid in sender_sid_set:
        with socket_lock:
            socket_io.emit("read_message", {"recver_id": recver_id}, room=sender_sid)

    # (DB) message read 처리
    chatUtils.read_chat(recver_id, sender_id)


#### alarm ####
def new_match(id, target_id):
    user_sid_set = redisServ.get_user_info(id, RedisOpt.SOCKET)
    target_sid_set = redisServ.get_user_info(target_id, RedisOpt.SOCKET)

    # MongoDB에 신규 대화 생성
    chatUtils.save_chat(id, target_id, "")

    # socket alarm 발생
    id_match[id] = id_match.get(id, set()) | set([target_id])
    for user_sid in user_sid_set:
        with socket_lock:
            socket_io.emit("new_match", {"target_id": target_id}, room=user_sid)

    id_match[target_id] = id_match.get(target_id, set()) | set([id])
    for target_sid in target_sid_set:
        with socket_lock:
            socket_io.emit("new_match", {"target_id": id}, room=target_sid)


def new_fancy(id, target_id):
    target_sid_set = redisServ.get_user_info(target_id, RedisOpt.SOCKET)
    for target_sid in target_sid_set:
        with socket_lock:
            socket_io.emit("new_fancy", {"target_id": id}, room=target_sid)


def new_unfancy(id, target_id):
    target_sid_set = redisServ.get_user_info(target_id, RedisOpt.SOCKET)
    for target_sid in target_sid_set:
        with socket_lock:
            socket_io.emit("unfancy", {"target_id": id}, room=target_sid)


def new_visitor(id):
    user_sid_set = redisServ.get_user_info(id, RedisOpt.SOCKET)
    for user_sid in user_sid_set:
        with socket_lock:
            socket_io.emit("new_visitor", room=user_sid)


#### update ####
def update_distance(id, lat, long):
    for target_id in id_match.get(id, set()):

        target_sid_set = redisServ.get_user_info(target_id, RedisOpt.SOCKET)
        for target_sid in target_sid_set:
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
    if target_id in id_match.get(id, set()):
        id_match[id].remove(target_id)

    if id in id_match.get(target_id, set()):
        id_match[target_id].remove(id)

    user_sid_set = redisServ.get_user_info(id, RedisOpt.SOCKET)
    for user_sid in user_sid_set:
        with socket_lock:
            socket_io.emit("unmatch", {"target_id": target_id}, room=user_sid)

    target_sid_set = redisServ.get_user_info(target_id, RedisOpt.SOCKET)
    for target_sid in target_sid_set:
        with socket_lock:
            socket_io.emit("unmatch", {"target_id": id}, room=target_sid)


def unregister(id):
    for target_id in id_match.get(id, set()):
        target_sid_set = redisServ.get_user_info(target_id, RedisOpt.SOCKET)
        for target_sid in target_sid_set:
            with socket_lock:
                socket_io.emit("unregister", {"target_id": id}, room=target_sid)


#### Utils ####
def check_status(target_id):
    target_status = redisServ.get_user_info(target_id, RedisOpt.SOCKET)
    if target_status and len(target_status):
        return UserStatus.ONLINE
    return UserStatus.OFFLINE
