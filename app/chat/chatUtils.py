from datetime import datetime
from ..utils.const import KST, RedisOpt
from ..db.mongo import MongoDBFactory
from ..utils import redisServ
from werkzeug.exceptions import Unauthorized


def get_match_user_list(id) -> list[int]:
    redis_user = redisServ.get_user_info(id, RedisOpt.LOCATION)
    if redis_user is None:
        raise Unauthorized("유저 정보를 찾을 수 없습니다.")

    # id와 매칭된 상대들의 리스트를 가져옴
    chat_collection = MongoDBFactory.get_collection("tea42", "chat")
    chat = chat_collection.find(
        {
            "participants": {"$elemMatch": {"$in": [id]}},
        },
        {
            "_id": 0,
            "participants": 1,
            "latest_msg_time": 1,
        },
    ).sort("latest_msg_time", -1)

    user_list = list()
    for c in chat:
        target_id = (
            c["participants"][0] if c["participants"][0] != id else c["participants"][1]
        )
        user_list.append(target_id)

    return user_list


def save_chat(id, target_id, message):

    kst_iso_now = datetime.now(KST).isoformat()

    # MongoDB에서 해당 사용자들 간의 대화 검색
    chat_collection = MongoDBFactory.get_collection("tea42", "chat")
    chat = chat_collection.find_one(
        {"participants": {"$all": [id, target_id]}},
        {"_id": 1},
    )

    new_message = {
        "sender_id": id,
        "message": message,
        "msg_time": kst_iso_now,
        "msg_new": True,
    }

    if chat:  # 대화 문서에 메시지를 추가
        chat_collection.update_one(
            {"_id": chat["_id"]},
            {
                "$push": {"messages": new_message},
                "$set": {"latest_msg_time": kst_iso_now},
            },
        )
    else:  # 대화 문서 생성
        chat_collection.insert_one(
            {
                "participants": [id, target_id],
                "latest_msg_time": kst_iso_now,
                "messages": [new_message],
            }
        )
        
    return kst_iso_now


def read_chat(recver_id, sender_id):
    chat_collection = MongoDBFactory.get_collection("tea42", "chat")
    chat = chat_collection.find_one(
        {
            "participants": {"$all": [recver_id, sender_id]},
        },
        {
            "_id": 1,
            "messages": {"$slice": -1},
        },
    )
    if chat["messages"][0]["msg_new"] and chat["messages"][0]["sender_id"] == sender_id:
        chat_collection.update_one(
            {"_id": chat["_id"]},
            {"$set": {"messages.$[elem].msg_new": False}},
            array_filters=[{"elem.msg_new": True}],
        )


def is_new_chat(recver_id, sender_id):
    chat_collection = MongoDBFactory.get_collection("tea42", "chat")
    chat = chat_collection.find_one(
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
        if chat["messages"][0]["sender_id"] == sender_id
        else False
    )


def delete_chat_by_block(id, target_id):
    chat_collection = MongoDBFactory.get_collection("tea42", "chat")
    chat = chat_collection.find_one(
        {
            "participants": {"$all": [id, target_id]},
        },
        {
            "_id": 1,
        },
    )
    if chat:
        chat_collection.delete_one({"_id": chat["_id"]})
