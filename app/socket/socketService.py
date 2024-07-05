from datetime import datetime
from ..db.mongo import MongoDBFactory
from ..utils.const import UserStatus, RedisOpt, KST, TIME_STR_TYPE, RedisOpt
from ..user import userUtils
from ..utils import redisServ
from ..history import historyUtils
from ..chat import chatUtils as chatUtils
from wsgi import socket_io, socket_lock
import sys

id_match = dict() # match된 유저 저장용 id: set()
socket_session = dict() # {socket: id} 저장
id_socket = dict() # {id: set(socket)} 저장


### connect && disconnect ###
def handle_connect(id, user_sid):
    print("CONN", id, user_sid, flush=True)

    redis_user = redisServ.get_user_info(id, RedisOpt.LOGIN)
    if redis_user is None or redis_user["email"] is None:
        # socket_io.emit("conn_fail", {"msg": "존재하지 않는 유저입니다."}, room=user_sid)
        return

    # (socket_id 저장)
    if id in id_socket:
        id_socket[id].add(user_sid)
    else:
        id_socket[id] = set([user_sid])

    # socket_id 저장
    socket_session[user_sid] = id

    # (socket) status 업데이트
    if id not in id_match:
        id_match[id] = historyUtils.get_match_list(id)
        _update_status(socket_io, id, UserStatus.ONLINE, id_match)

        # (socket) 로그아웃 중 발생한 이벤트 처리
        is_fancy, is_visitor, is_match = userUtils.get_logout_event(id)
        if any([is_fancy, is_visitor, is_match]):
            with socket_lock:
                if is_fancy:
                    socket_io.emit("new_fancy", {"target_id": id}, room=user_sid)
                if is_visitor:
                    socket_io.emit("new_visitor", room=user_sid)
                if is_match:
                    socket_io.emit("new_match", {"target_id": id}, room=user_sid)
            userUtils.reset_logout_event(id)


def handle_disconnect(user_sid):

    # (socket) status 업데이트
    id = socket_session.get(user_sid, None)
    print("disconn", id, user_sid, flush=True)
    if id is None:
        return

    # match 정보 삭제 및 socket 데이터 삭제
    user_sid_set = id_socket.get(id, set())
    if user_sid in user_sid_set:
        if len(user_sid_set) == 1:
            # 마지막 소켓이었을 경우에만 offline 처리 및 last_online 업데이트
            _update_status(socket_io, id, UserStatus.OFFLINE, id_match)
            userUtils.update_last_online(id)
            id_socket.pop(id)
            print("disconn::offline", id, flush=True)

        else:
            user_sid_set.remove(user_sid)

    if id in id_match:
        id_match.pop(id)


def _update_status(socket_io, id, status, id_match):
    # status 업데이트
    for target_id in id_match.get(id, set()):
        target_sid_set = id_socket.get(target_id, set())
        if target_sid_set:
            with socket_lock:
                for target_sid in target_sid_set:
                    socket_io.emit(
                        "update_status",
                        {"target_id": id, "status": status},
                        room=target_sid,
                    )


### chat ###
def send_message(data, user_sid=None, sender_id=None):
    # [Pytest]
    if sender_id is None:
        sender_id = socket_session.get(user_sid, None)
        if sender_id is None:
            return

    # TODO type 검사
    recver_id = data.get("recver_id")  # int
    message = data.get("message")  # str

    if sender_id not in id_match.get(recver_id, set()):
        return

    if recver_id and message.strip():
        msg_time = chatUtils.save_chat(sender_id, recver_id, message)

        recver_sid_set = id_socket.get(recver_id, set())
        if recver_sid_set:
            with socket_lock:
                for recver_sid in recver_sid_set:
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
        else:
           # 상대방이 오프라인일 경우
            userUtils.update_logout_event(recver_id, "is_match")


def read_message(data, user_sid):
    recver_id = socket_session.get(user_sid, None)
    if recver_id is None:
        return

    # TODO type 검사
    sender_id = data.get("sender_id")  # int
    sender_sid_set = id_socket.get(sender_id, set())
    if sender_sid_set:
        for sender_sid in sender_sid_set:
            with socket_lock:
                socket_io.emit(
                    "read_message", {"recver_id": recver_id}, room=sender_sid
                )

    # (DB) message read 처리
    chatUtils.read_chat(recver_id, sender_id)


#### alarm ####
def new_match(id, target_id):
    user_sid_set = id_socket.get(id, set())
    target_sid_set = id_socket.get(target_id, set())

    # MongoDB에 신규 대화 생성
    chatUtils.save_chat(id, target_id, "")

    # socket alarm 발생
    id_match[id] = id_match.get(id, set()) | set([target_id])
    if user_sid_set:
        with socket_lock:
            for user_sid in user_sid_set:
                socket_io.emit("new_match", {"target_id": target_id}, room=user_sid)

    id_match[target_id] = id_match.get(target_id, set()) | set([id])
    if target_sid_set:
        with socket_lock:
            for target_sid in target_sid_set:
                socket_io.emit("new_match", {"target_id": id}, room=target_sid)
    else: # 상대방이 오프라인일 경우
        userUtils.update_logout_event(target_id, "is_match")


def new_fancy(id, target_id):
    target_sid_set = id_socket.get(target_id, set())
    if target_sid_set:
        with socket_lock:
            for target_sid in target_sid_set:
                socket_io.emit("new_fancy", {"target_id": id}, room=target_sid)
    else: # 오프라인일 경우
        userUtils.update_logout_event(target_id, "is_fancy")


def new_unfancy(id, target_id):
    target_sid_set = id_socket.get(target_id, set())
    if target_sid_set:
        with socket_lock:
            for target_sid in target_sid_set:
                socket_io.emit("unfancy", {"target_id": id}, room=target_sid)


def new_visitor(id):
    user_sid_set = id_socket.get(id, set())
    if user_sid_set:
        with socket_lock:
            for user_sid in user_sid_set:
                socket_io.emit("new_visitor", room=user_sid)
    else: # 오프라인일 경우
        userUtils.update_logout_event(id, "is_visitor")


#### update ####
def update_distance(id, lat, long):
    for target_id in id_match.get(id, set()):

        target_sid_set = id_socket.get(target_id, set())
        if target_sid_set:
            redis_target = redisServ.get_user_info(target_id, RedisOpt.LOCATION)
            distance = userUtils.get_distance(
                float(redis_target["latitude"]),
                float(redis_target["longitude"]),
                lat,
                long,
            )
            with socket_lock:
                for target_sid in target_sid_set:
                    socket_io.emit(
                        "update_distance",
                        {
                            "target_id": id,
                            "distance": distance,
                        },
                        room=target_sid,
                    )


def unmatch(id, target_id):
    if target_id in id_match.get(id, set()):
        id_match[id].remove(target_id)

    if id in id_match.get(target_id, set()):
        id_match[target_id].remove(id)

    user_sid_set = id_socket.get(id, set())
    if user_sid_set:
        with socket_lock:
            for user_sid in user_sid_set:
                socket_io.emit("unmatch", {"target_id": target_id}, room=user_sid)

    target_sid_set = id_socket.get(target_id, set())
    if target_sid_set:
        with socket_lock:
            for target_sid in target_sid_set:
                socket_io.emit("unmatch", {"target_id": id}, room=target_sid)
    else: # 상대방이 오프라인일 경우
        userUtils.update_logout_event(target_id, "is_match")


def unregister(id):
    for target_id in id_match.get(id, set()):
        target_sid_set = id_socket.get(target_id, set())
        if target_sid_set:
            with socket_lock:
                for target_sid in target_sid_set:
                    socket_io.emit("unregister", {"target_id": id}, room=target_sid)
            id_match[target_id].remove(id)
        else: # 상대방이 오프라인일 경우
            userUtils.update_logout_event(target_id, "is_match")
    id_match.pop(id, None)


#### Utils ####
def check_status(target_id):
    target_status = id_socket.get(target_id, set())
    if target_status:
        return UserStatus.ONLINE
    return UserStatus.OFFLINE
