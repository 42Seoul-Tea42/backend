import pytest
from .. import app
from unittest.mock import MagicMock, patch
import redis
from mongomock import MongoClient
import psycopg2


# Redis 테스트 환경 설정
@pytest.fixture(scope="session")
def redis_server():
    redis_server = redis.Redis()
    yield redis_server
    redis_server.flushall()


# MongoDB 테스트 환경 설정
@pytest.fixture(scope="session")
def mongo_client():
    mongo_client = MongoClient()
    yield mongo_client
    mongo_client.drop_database("testdb")


# PostgreSQL Mock 설정
@pytest.fixture
def mock_postgresql():
    # Mock psycopg2.connect 함수
    with patch("psycopg2.connect") as mock_connect:
        # psycopg2.connect가 호출될 때 반환할 Mock connection 객체 생성
        mock_connection = MagicMock()
        # cursor 메서드 호출 시 반환할 Mock cursor 객체 생성
        mock_cursor = MagicMock()
        mock_connection.cursor.return_value = mock_cursor
        # psycopg2.connect 함수가 호출될 때 반환할 Mock connection 객체 설정
        mock_connect.return_value = mock_connection

        yield mock_connection


# Mock create_app 함수
@patch("app.create_app")
def test_app(mock_create_app, redis_server, mongo_client):
    # Mock create_app 함수
    app = MagicMock()
    mock_create_app.return_value = app

    # Redis 연결 설정
    app.config = {}
    app.config["REDIS_HOST"] = redis_server.connection_pool.connection_kwargs["host"]
    app.config["REDIS_PORT"] = redis_server.connection_pool.connection_kwargs["port"]

    # MongoDB 연결 설정
    app.config["MONGO_URI"] = "mongodb://localhost:27017/testdb"

    # 테스트 클라이언트 생성
    client = app.test_client()

    # 예제 테스트: GET /hello 엔드포인트 확인
    response = client.get("/hello")
    assert response.status_code == 200
    assert response.data == b"Hello there, welcome to Tea42"
