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
