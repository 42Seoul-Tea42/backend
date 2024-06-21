from ..utils.const import (
    MAX_CHAT,
    Fancy,
    StatusCode,
    RedisOpt,
    Authorization,
    TIME_STR_TYPE,
)
from . import chatUtils
from ..history import historyUtils as hisUtils
from ..socket import socketService as socketServ
from ..user import userUtils
from werkzeug.exceptions import Unauthorized, BadRequest
from datetime import datetime

from ..db.mongo import MongoDBFactory
from ..utils import redisServ


def chat_list(id):
    # 유저 API 접근 권한 확인
    userUtils.check_authorization(id, Authorization.EMOJI)

    redis_user = redisServ.get_user_info(id, RedisOpt.LOCATION)
    if redis_user is None or redis_user["longitude"] is None:
        raise Unauthorized("유저 정보를 찾을 수 없습니다.")
    long, lat = float(redis_user["longitude"]), float(redis_user["latitude"])

    # id와 매칭된 상대들의 리스트를 가져옴
    chat_target = chatUtils.get_match_user_list(id)

    result = []
    for target_id in chat_target:
        target = userUtils.get_user(target_id)
        picture = userUtils.get_picture(target["pictures"][0])
        result.append(
            {
                "id": target["id"],
                "name": target["name"],
                "last_name": target["last_name"],
                "status": socketServ.check_status(target["id"]),
                "distance": userUtils.get_distance(
                    lat, long, target["latitude"], target["longitude"]
                ),
                "fancy": hisUtils.get_fancy_status(id, target["id"]),
                "new": chatUtils.is_new_chat(id, target["id"]),
                "picture": picture,
            }
        )

    return {
        "chat_list": result,
    }, StatusCode.OK


def get_msg(id, data):
    # 유저 API 접근 권한 확인
    userUtils.check_authorization(id, Authorization.EMOJI)

    target_id = data["target_id"]
    if id == target_id:
        raise BadRequest("자기 자신과 채팅할 수 없습니다.")

    if hisUtils.get_fancy_status(id, target_id) < Fancy.CONN:
        raise BadRequest("매칭된 상대가 아닙니다.")

    # message new True인 경우 처리 (읽은 경우)
    chatUtils.read_chat(recver_id=id, sender_id=target_id)

    # time을 기준으로 이전의 메시지를 가져와 최신 MAX_CHAT개 반환
    iso_time = data["time"].isoformat()

    chat_collection = MongoDBFactory.get_collection("tea42", "chat")
    pipeline = [
        # participants가 주어진 id와 target_id를 모두 포함하는 문서 필터링
        {"$match": {"participants": {"$all": [id, target_id]}}},
        # messages를 풀어서 배열로 만듦
        {"$unwind": "$messages"},
        # 주어진 time 이전의 메시지 필터링
        {"$match": {"messages.msg_time": {"$lt": iso_time}}},
        # msg_time 기준으로 내림차순 정렬
        {"$sort": {"messages.msg_time": -1}},
        # 최대 MAX_CHAT 개수 만큼 메시지 선택
        {"$limit": MAX_CHAT},
        # messages를 다시 배열로 모음
        {"$group": {"_id": "$_id", "messages": {"$push": "$messages"}}},
    ]

    # aggregation pipeline 실행
    chat_cursor = chat_collection.aggregate(pipeline)

    messages = []
    for chat in chat_cursor:
        for message in chat.get("messages", []):
            message["msg_time"] = datetime.strptime(
                message["msg_time"], "%Y-%m-%dT%H:%M:%S.%f%z"
            ).strftime(TIME_STR_TYPE)
            if message["msg_new"] and message["sender_id"] == id:
                message["msg_new"] = False
            messages.append(message)

    return {"msg_list": messages}, StatusCode.OK
