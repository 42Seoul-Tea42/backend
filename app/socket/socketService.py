from datetime import datetime
from ..db.mongo import MongoDBFactory
from wsgi import socket_io
from ..utils.const import UserStatus, RedisOpt, KST, TIME_STR_TYPE
from ..user import userUtils
from ..utils import redisServ
from ..history import historyUtils
from ..chat import chatUtils as chatUtils


# match된 유저 저장용 id: set()
id_match = dict()


### connect && disconnect ###
def handle_connect(id, user_sid):
    redis_user = redisServ.get_login_check(id)
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
    _update_status(id, UserStatus.ONLINE, id_match)

    print(f"Client {id}:{user_sid} connected")
    socket_io.emit("connect", room=user_sid)


def handle_disconnect(user_sid):
    # (socket) status 업데이트
    id = socket_io.get_session(user_sid).get("id", None)
    if id is None:
        return

    _update_status(id, UserStatus.OFFLINE, id_match)

    # match 정보 삭제 및 (redis) 데이터 삭제
    id_match.pop(id)
    redisServ.delete_socket_id_by_id(id)

    # TODO 아래 맞는지 확인
    socket_io.delete_session(user_sid)

    userUtils.update_last_online(id)
    print(f"Client {id} disconnected")


def _update_status(id, status, id_match):
    # status 업데이트
    for target_id in id_match.get(id, []):
        target_sid = redisServ.get_socket_id_by_id(target_id)
        if target_sid:
            socket_io.emit(
                "update_status", {"target_id": id, "status": status}, room=target_sid
            )


### chat ###
def send_message(data, user_sid=None, sender_id=None):
    # [Test]
    if sender_id is None:
        sender_id = socket_io.get_session(user_sid).get("id", None)
        if sender_id is None:
            return

    # TODO type 검사
    recver_id = data.get("recver_id")  # int
    message = data.get("message")  # str

    if recver_id and message:
        chatUtils.save_chat(sender_id, recver_id, message)

        recver_sid = redisServ.get_socket_id_by_id(recver_id)
        if recver_sid:
            socket_io.emit(
                "send_message",
                {"sender_id": sender_id, "message": message},
                room=recver_sid,
            )


def read_message(data, user_sid):
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
    user_sid = redisServ.get_socket_id_by_id(id)
    target_sid = redisServ.get_socket_id_by_id(target_id)

    # MongoDB에 신규 대화 생성
    chatUtils.save_chat(id, target_id, "")

    # socket alarm 발생
    if user_sid:
        id_match.get(id, set()).add(target_id)
        socket_io.emit("new_match", {"target_id": target_id}, room=user_sid)
    if target_sid:
        id_match.get(target_id, set()).add(id)
        socket_io.emit("new_match", {"target_id": id}, room=target_sid)


def new_fancy(id, target_id):
    target_sid = redisServ.get_socket_id_by_id(target_id)
    if target_sid:
        socket_io.emit("new_fancy", {"target_id": id}, room=target_sid)


def new_history(id):
    user_sid = redisServ.get_socket_id_by_id(id)
    if user_sid:
        socket_io.emit("new_history", room=user_sid)


#### update ####
def update_distance(id, lat, long):
    for target_id in id_match.get(id, set()):
        target_sid = redisServ.get_socket_id_by_id(target_id)

        if target_sid:
            target = userUtils.get_user(target_id)
            if target is None:
                continue

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

    target_sid = redisServ.get_socket_id_by_id(target_id)
    if target_sid:
        socket_io.emit("unmatch", {"target_id": id}, room=target_sid)


def unregister(id):
    for target_id in id_match.get(id, set()):
        target_sid = redisServ.get_socket_id_by_id(target_id)
        if target_sid:
            socket_io.emit("unregister", {"target_id": id}, room=target_sid)


#### Utils ####
def check_status(target_id):
    if target_id in redisServ.get_user_info(target_id, RedisOpt.SOCKET):
        return UserStatus.ONLINE
    return UserStatus.OFFLINE
