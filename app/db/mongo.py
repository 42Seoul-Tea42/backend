import os
from pymongo import MongoClient


class MongoDBFactory:
    _client = None

    @classmethod
    def get_client(cls):
        if cls._client is None:
            cls.create_client()
        return cls._client

    @classmethod
    def create_client(cls):
        host = os.getenv("MONGO_HOST")
        port = int(os.getenv("MONGO_PORT"))
        cls._client = MongoClient(host=host, port=port)

    @classmethod
    def close_client(cls):
        if cls._client:
            cls._client.close()
            cls._client = None

    @classmethod
    def get_database(cls, db_name):
        client = cls.get_client()
        return client[db_name]

    @classmethod
    def get_collection(cls, db_name, collection_name):
        db = cls.get_database(db_name)
        return db[collection_name]

    @classmethod
    def release_collection(cls, collection):
        # 클라이언트를 닫지 않고 컬렉션을 릴리스합니다.
        pass


# 사용 예시
# chat_collection = MongoDBFactory.get_collection("tea42", "chat")
# MongoDBFactory.release_collection(chat_collection)


# # MongoDB chat collection schema
# {
#     # MongoDB에서 자동 생성되는 ObjectId
#     "_id": "ObjectId",
#     # 대화 참여자들의 id
#     "participants": ["string", "string"],
#     # 가장 최근 메시지의 시간
#     "latest_msg_time": "string (ISO 8601 datetime)",
#     # 대화 내용 (리스트)
#     "messages": [
#         {
#             "sender_id": "string",  # 메시지를 보낸 유저의 id
#             "message": "string",  # 메시지 내용
#             "msg_time": "string (ISO 8601 datetime)",  # 메시지 보낸 시간
#             "msg_new": "boolean",  # 상대방이 메시지를 읽었는지 여부
#         }
#     ],
# }
