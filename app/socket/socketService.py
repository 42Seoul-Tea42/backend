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
    from wsgi import socket_io, socket_lock

    error_flag = 1
    try:
        redis_user = redisServ.get_user_info(id, RedisOpt.LOGIN)
        if redis_user is None:
            with socket_lock:
                socket_io.emit(
                    "conn_fail", {"message": "존재하지 않는 유저입니다."}, room=user_sid
                )

        error_flag += 1
        # (redis) user_info 업데이트
        redisServ.update_user_info(id, {"socket_id": user_sid})

        error_flag += 1
        # (redis) socket_id 저장
        with socket_lock:
            socket_io.save_session(user_sid, {"id": id})

        error_flag += 1
        # (socket) status 업데이트
        id_match[id] = historyUtils.get_match_list(id)
        _update_status(socket_io, socket_lock, id, UserStatus.ONLINE, id_match)

    except Exception as e:
        print("handle_connect" + ("🔥" * error_flag))
        sys.stdout.flush()


def handle_disconnect(user_sid):
    from wsgi import socket_io, socket_lock

    error_flag = 1
    try:
        # (socket) status 업데이트
        id = None
        with socket_lock:
            id = socket_io.get_session(user_sid).get("id", None)
            if id is None:
                return

        error_flag += 1
        _update_status(socket_io, socket_lock, id, UserStatus.OFFLINE, id_match)

        error_flag += 1
        # match 정보 삭제 및 (redis) 데이터 삭제
        if id in id_match:
            id_match.pop(id)
        redisServ.delete_socket_id_by_id(id)

        error_flag += 1
        userUtils.update_last_online(id)

    except Exception as e:
        print("handle_disconnect" + ("🔥" * error_flag))
        sys.stdout.flush()


def _update_status(socket_io, socket_lock, id, status, id_match):

    # status 업데이트
    for target_id in id_match.get(id, []):
        target_sid = redisServ.get_socket_id_by_id(target_id)
        if target_sid:
            with socket_lock:
                socket_io.emit(
                    "update_status",
                    {"target_id": id, "status": status},
                    room=target_sid,
                )


### chat ###
def send_message(data, user_sid=None):
    from wsgi import socket_io, socket_lock

    error_flag = 1
    try:
        # [Test]
        sender_id = None
        with socket_lock:
            sender_id = socket_io.get_session(user_sid).get("id", None)
            if sender_id is None:
                return

        error_flag += 1
        # TODO type 검사
        recver_id = data.get("recver_id")  # int
        message = data.get("message")  # str

        error_flag += 1
        if recver_id and message.strip():
            chatUtils.save_chat(sender_id, recver_id, message)

            error_flag += 1
            recver_sid = redisServ.get_socket_id_by_id(recver_id)

            error_flag += 1
            if recver_sid:

                error_flag += 1
                with socket_lock:
                    socket_io.emit(
                        "send_message",
                        {"sender_id": sender_id, "message": message},
                        room=recver_sid,
                    )
        else:  # [TEST]
            print("send_message ERRRRRRRRRRRR")
            sys.stdout.flush()

    except Exception as e:
        print("send_message" + ("🔥" * error_flag))
        sys.stdout.flush()


def read_message(data, user_sid):
    from wsgi import socket_io, socket_lock

    error_flag = 1
    try:
        recver_id = None
        with socket_lock:
            recver_id = socket_io.get_session(user_sid).get("id", None)
            if recver_id is None:
                return

        error_flag += 1
        # TODO type 검사
        sender_id = data.get("sender_id")  # int
        sender_sid = redisServ.get_socket_id_by_id(sender_id)

        error_flag += 1
        if sender_sid:
            with socket_lock:
                socket_io.emit(
                    "read_message", {"recver_id": recver_id}, room=sender_sid
                )

        error_flag += 1
        # (DB) message read 처리
        chatUtils.read_chat(recver_id, sender_id)

    except Exception as e:
        print("read_message" + ("🔥" * error_flag))
        sys.stdout.flush()


#### alarm ####
def new_match(id, target_id):
    from wsgi import socket_io, socket_lock

    error_flag = 1
    try:

        user_sid = redisServ.get_socket_id_by_id(id)
        target_sid = redisServ.get_socket_id_by_id(target_id)

        error_flag += 1
        # MongoDB에 신규 대화 생성
        chatUtils.save_chat(id, target_id, "")

        error_flag += 1
        # socket alarm 발생
        if user_sid:
            error_flag += 1
            id_match.get(id, set()).add(target_id)
            error_flag += 1
            with socket_lock:
                socket_io.emit("new_match", {"target_id": target_id}, room=user_sid)
        if target_sid:
            error_flag += 3
            id_match.get(target_id, set()).add(id)
            error_flag += 1
            with socket_lock:
                socket_io.emit("new_match", {"target_id": id}, room=target_sid)

    except Exception as e:
        print("new_match" + ("🔥" * error_flag))
        sys.stdout.flush()


def new_fancy(id, target_id):
    from wsgi import socket_io, socket_lock

    error_flag = 1
    try:
        target_sid = redisServ.get_socket_id_by_id(target_id)
        if target_sid:
            with socket_lock:
                socket_io.emit("new_fancy", {"target_id": id}, room=target_sid)

    except Exception as e:
        print("new_fancy" + ("🔥" * error_flag))
        sys.stdout.flush()


def new_history(id):
    from wsgi import socket_io, socket_lock

    error_flag = 1
    try:
        user_sid = redisServ.get_socket_id_by_id(id)
        if user_sid:
            with socket_lock:
                socket_io.emit("new_history", room=user_sid)

    except Exception as e:
        print("new_history" + ("🔥" * error_flag))
        sys.stdout.flush()


#### update ####
def update_distance(id, lat, long):
    from wsgi import socket_io, socket_lock

    error_flag = 1
    try:
        for target_id in id_match.get(id, set()):

            error_flag += 1
            target_sid = redisServ.get_socket_id_by_id(target_id)

            if target_sid:
                target = userUtils.get_user(target_id)
                if target is None:
                    continue

                error_flag += 1
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
    except Exception as e:
        print("update_distance" + ("🔥" * error_flag))
        sys.stdout.flush()


def unmatch(id, target_id):
    from wsgi import socket_io, socket_lock

    error_flag = 1
    try:
        if target_id in id_match.get(id, set()):
            id_match[id].remove(target_id)

        error_flag += 1
        if id in id_match.get(target_id, set()):
            id_match[target_id].remove(id)

        error_flag += 1
        target_sid = redisServ.get_socket_id_by_id(target_id)
        if target_sid:
            with socket_lock:
                socket_io.emit("unmatch", {"target_id": id}, room=target_sid)

    except Exception as e:
        print("unmatch" + ("🔥" * error_flag))
        sys.stdout.flush()


def unregister(id):
    from wsgi import socket_io, socket_lock

    error_flag = 1
    try:
        for target_id in id_match.get(id, set()):
            target_sid = redisServ.get_socket_id_by_id(target_id)
            if target_sid:

                error_flag += 1
                with socket_lock:
                    socket_io.emit("unregister", {"target_id": id}, room=target_sid)

    except Exception as e:
        print("unregister" + ("🔥" * error_flag))
        sys.stdout.flush()


#### Utils ####
def check_status(target_id):
    if target_id in redisServ.get_user_info(target_id, RedisOpt.SOCKET):
        return UserStatus.ONLINE
    return UserStatus.OFFLINE
