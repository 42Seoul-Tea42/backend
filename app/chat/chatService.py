from ..utils.const import MAX_CHAT, Fancy, StatusCode, RedisOpt, Authorization
from . import chatUtils
from ..history import historyUtils as hisUtils
from ..socket import socketService as socketServ
from ..user import userUtils
from werkzeug.exceptions import Unauthorized, BadRequest, Forbidden

# from app import chat_collection
from ..db.mongo import MongoDBFactory
from ..utils import redisServ


def chat_list(id):
    # 유저 API 접근 권한 확인
    userUtils.check_authorization(id, Authorization.EMOJI)

    redis_user = redisServ.get_user_info(id, RedisOpt.LOCATION)
    if redis_user is None:
        raise Unauthorized("유저 정보를 찾을 수 없습니다.")
    long, lat = redis_user["longitude"], redis_user["latitude"]

    # id와 매칭된 상대들의 리스트를 가져옴
    chat_target = chatUtils.get_match_user_list(id)

    result = []
    for target_id in chat_target:
        target = userUtils.get_user(target_id)
        picture = userUtils.get_picture(target["picture"][0])
        result.append(
            {
                "id": target["id"],
                "name": target["name"],
                "last_name": target["last_name"],
                "status": socketServ.check_status(target["id"]),
                "distance": userUtils.get_distance(
                    lat, long, target["latitude"], target["longitude"]
                ),
                "fancy": hisUtils.get_fancy(id, target["id"]),
                "new": chatUtils.get_new_chat(id, target["id"]),
                "picture": picture,
            }
        )

    return {
        "chat_list": result,
    }, StatusCode.OK


def get_msg(id, target_id, time):
    # 유저 API 접근 권한 확인
    userUtils.check_authorization(id, Authorization.EMOJI)

    if userUtils.get_user(target_id) is None:
        raise BadRequest("유저 정보를 찾을 수 없습니다.")

    if hisUtils.get_fancy(id, target_id) < Fancy.CONN:
        raise Forbidden("매칭된 상대가 아닙니다.")

    # message new True인 경우 처리 (읽은 경우)
    chatUtils.read_chat(recver_id=id, sender_id=target_id)

    # time을 기준으로 이전의 메시지를 가져와 최신 MAX_CHAT개 반환
    chat_collection = MongoDBFactory.get_collection("tea42", "chat")
    chat = chat_collection.find(
        {
            "participants": {"$all": [id, target_id]},
            "messages.msg_time": {"$lt": time},
        },
        {
            "_id": 0,
            "messages": {"$slice": -MAX_CHAT},
        },
    )

    # TODO [TEST]
    return {"msg_list": list(reversed(chat["messages"])) if chat else []}, StatusCode.OK
