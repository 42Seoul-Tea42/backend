from datetime import datetime

from ..utils.const import KST, RedisOpt
from ...app import chat_collection
from ..utils import redisServ
from werkzeug.exceptions import Unauthorized


def get_match_user_list(id) -> set:
    user = redisServ.get_user_info(id, RedisOpt.LOCATION)
    if user is None:
        raise Unauthorized("유저 정보를 찾을 수 없습니다.")

    # id와 매칭된 상대들의 리스트를 가져옴
    chat = chat_collection.find_all(
        {
            "participants": {"$elemMatch": {"$in": [id]}},
        },
        {
            "participants": 1,
            "_id": 0,
            "messages": 0,
        },
    )

    user_list = set()
    for c in chat:
        target_id = (
            c["participants"][0] if c["participants"][0] != id else c["participants"][1]
        )
        user_list.add(target_id)

    return user_list


def save_chat(id, target_id, message):
    now_kst = datetime.now(KST)

    # MongoDB에서 해당 사용자들 간의 대화를 검색합니다.
    chat = chat_collection.find_one(
        {"participants": {"$all": [id, target_id]}},
        {"_id": 1},
    )

    new_message = {
        "user_id": id,
        "target_id": target_id,
        "msg": message,
        "msg_time": now_kst,
        "msg_new": True,
    }

    if chat:
        # 대화 문서가 이미 존재하면 메시지를 추가합니다.
        chat_collection.update_one(
            {"_id": chat["_id"]}, {"$push": {"messages": new_message}}
        )
    else:
        # 대화 문서가 존재하지 않으면 새로운 대화 문서를 생성합니다.
        chat_document = {
            "participants": [id, target_id],
            "messages": [new_message],
        }
        chat_collection.insert_one(chat_document)


def read_chat(recver_id, sender_id):
    chat = chat_collection.findone(
        {
            "participants": {"$all": [recver_id, sender_id]},
        },
        {
            "_id": 1,
            "participants": 0,
            "messages": {"$slice": -1},
        },
    )
    if chat["messages"][0]["target_id"] == recver_id and chat["messages"][0]["msg_new"]:
        chat_collection.update_many(
            {"_id": chat["_id"]},
            {"$set": {"messages.$.msg_new": False}},
        )


def is_new_chat(recver_id, sender_id):
    chat = chat_collection.findone(
        {
            "participants": {"$all": [recver_id, sender_id]},
        },
        {
            "_id": 0,
            "messages": {"$slice": -1},
        },
    )
    return (
        chat["messages"][0]["msg_new"]
        if chat["messages"][0]["target_id"] == recver_id
        else False
    )
