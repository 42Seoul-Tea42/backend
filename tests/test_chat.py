import json
from datetime import datetime
from app.utils.const import StatusCode, KST, TIME_STR_TYPE
from urllib.parse import quote
from app.history.historyService import dummy_fancy as fancy


duplicated_login = "dummy1"
valid_pw = "ASDFasdf0"


# chat list 확인
def test_empty_chat_list(test_client):
    # 로그인
    response = test_client.post(
        f"/api/user/login",
        data=json.dumps(
            {
                "login_id": duplicated_login,
                "pw": valid_pw,
            }
        ),
        content_type="application/json",
    )
    data = json.loads(response.data.decode("utf-8"))
    assert response.status_code == StatusCode.OK
    id = data["id"]

    # chat 목록 보기 (empty)
    response = test_client.get(f"/api/chat/list")
    data = json.loads(response.data.decode("utf-8"))
    assert response.status_code == StatusCode.OK
    assert len(data["chat_list"]) == 0

    # 채팅방 내용 확인하기 (fail)
    response = test_client.get(f"/api/chat/msg?target_id={id+1}")
    assert response.status_code == StatusCode.BAD_REQUEST

    response = test_client.get(f"/api/chat/msg?target_id={id}")
    assert response.status_code == StatusCode.BAD_REQUEST

    response = test_client.get(f"/api/chat/msg?target_id={id-1}")
    assert response.status_code == StatusCode.BAD_REQUEST

    # 로그아웃
    response = test_client.post(
        f"/api/user/logout",
        content_type="application/json",
    )
    assert response.status_code == StatusCode.OK


# chat list 확인
def test_chat_list_order(test_client):
    # 로그인
    response = test_client.post(
        f"/api/user/login",
        data=json.dumps(
            {
                "login_id": duplicated_login,
                "pw": valid_pw,
            }
        ),
        content_type="application/json",
    )
    data = json.loads(response.data.decode("utf-8"))
    assert response.status_code == StatusCode.OK
    id = data["id"]

    # 최초 시간
    first_kst = quote(datetime.now(KST).strftime(TIME_STR_TYPE))

    # match case (1): 상대방이 매치 (new_msg == True)
    # 유저 fancy 하기
    response = test_client.patch(
        f"/api/history/fancy",
        data=json.dumps({"target_id": id + 1}),
        content_type="application/json",
    )
    data = json.loads(response.data.decode("utf-8"))
    assert response.status_code == StatusCode.OK

    # fancy 받기
    fancy(id + 1, target_id=id)

    # chat 목록 보기
    response = test_client.get(f"/api/chat/list")
    data = json.loads(response.data.decode("utf-8"))
    assert response.status_code == StatusCode.OK
    assert len(data["chat_list"]) == 1
    assert data["chat_list"][0]["id"] == id + 1
    assert data["chat_list"][0]["name"] == "dummy2"
    assert data["chat_list"][0]["last_name"] == "2"
    assert data["chat_list"][0]["status"] == 0
    assert data["chat_list"][0]["distance"]
    assert data["chat_list"][0]["fancy"] == 3
    assert data["chat_list"][0]["new"] == True

    # 채팅방 내용 확인하기 (empty)
    response = test_client.get(
        f"/api/chat/msg?target_id={id+1}&time={quote(datetime.now(KST).strftime(TIME_STR_TYPE))}"
    )
    data = json.loads(response.data.decode("utf-8"))
    assert response.status_code == StatusCode.OK
    assert len(data["msg_list"]) == 1
    assert data["msg_list"][0]["sender_id"] == id + 1
    assert data["msg_list"][0]["message"] == ""
    assert data["msg_list"][0]["msg_time"]
    assert data["msg_list"][0]["msg_new"] == False

    # chat 목록 보기
    response = test_client.get(f"/api/chat/list")
    data = json.loads(response.data.decode("utf-8"))
    assert response.status_code == StatusCode.OK
    assert len(data["chat_list"]) == 1
    assert data["chat_list"][0]["id"] == id + 1
    assert data["chat_list"][0]["name"] == "dummy2"
    assert data["chat_list"][0]["last_name"] == "2"
    assert data["chat_list"][0]["status"] == 0
    assert data["chat_list"][0]["distance"]
    assert data["chat_list"][0]["fancy"] == 3
    assert data["chat_list"][0]["new"] == False

    # match case (2): 내가 매치 (new_msg == False)
    # fancy 받기
    fancy(id + 2, target_id=id)

    # 유저 fancy 하기
    response = test_client.patch(
        f"/api/history/fancy",
        data=json.dumps({"target_id": id + 2}),
        content_type="application/json",
    )
    data = json.loads(response.data.decode("utf-8"))
    assert response.status_code == StatusCode.OK

    # chat 목록 보기
    response = test_client.get(f"/api/chat/list")
    data = json.loads(response.data.decode("utf-8"))
    assert response.status_code == StatusCode.OK
    assert len(data["chat_list"]) == 2
    assert data["chat_list"][0]["id"] == id + 2
    assert data["chat_list"][0]["name"] == "dummy3"
    assert data["chat_list"][0]["last_name"] == "3"
    assert data["chat_list"][0]["status"] == 0
    assert data["chat_list"][0]["distance"]
    assert data["chat_list"][0]["fancy"] == 3
    assert data["chat_list"][0]["new"] == False
    assert data["chat_list"][1]["id"] == id + 1
    assert data["chat_list"][1]["name"] == "dummy2"
    assert data["chat_list"][1]["last_name"] == "2"
    assert data["chat_list"][1]["status"] == 0
    assert data["chat_list"][1]["distance"]
    assert data["chat_list"][1]["fancy"] == 3
    assert data["chat_list"][1]["new"] == False

    # 채팅방 내용 확인하기 (empty)
    response = test_client.get(f"/api/chat/msg?target_id={id+1}&time={first_kst}")
    data = json.loads(response.data.decode("utf-8"))
    assert response.status_code == StatusCode.OK
    assert len(data["msg_list"]) == 0

    # 채팅방 내용 확인하기 (1)
    response = test_client.get(
        f"/api/chat/msg?target_id={id+1}&time={quote(datetime.now(KST).strftime(TIME_STR_TYPE))}"
    )
    data = json.loads(response.data.decode("utf-8"))
    assert response.status_code == StatusCode.OK
    assert len(data["msg_list"]) == 1
    assert data["msg_list"][0]["sender_id"] == id + 1
    assert data["msg_list"][0]["message"] == ""
    assert data["msg_list"][0]["msg_time"]
    assert data["msg_list"][0]["msg_new"] == False

    # 채팅방 내용 확인하기 (1)
    response = test_client.get(
        f"/api/chat/msg?target_id={id+2}&time={quote(datetime.now(KST).strftime(TIME_STR_TYPE))}"
    )
    data = json.loads(response.data.decode("utf-8"))
    assert response.status_code == StatusCode.OK
    assert len(data["msg_list"]) == 1
    assert data["msg_list"][0]["sender_id"] == id
    assert data["msg_list"][0]["message"] == ""
    assert data["msg_list"][0]["msg_time"]
    assert data["msg_list"][0]["msg_new"] == False

    # 채팅 받기
    from app.socket.socketService import send_message

    send_message({"recver_id": id, "message": "hello"}, sender_id=id + 1)

    # chat 목록 보기
    response = test_client.get(f"/api/chat/list")
    data = json.loads(response.data.decode("utf-8"))
    assert response.status_code == StatusCode.OK
    assert len(data["chat_list"]) == 2
    assert data["chat_list"][0]["id"] == id + 1
    assert data["chat_list"][0]["name"] == "dummy2"
    assert data["chat_list"][0]["last_name"] == "2"
    assert data["chat_list"][0]["status"] == 0
    assert data["chat_list"][0]["distance"]
    assert data["chat_list"][0]["fancy"] == 3
    assert data["chat_list"][0]["new"] == True
    assert data["chat_list"][1]["id"] == id + 2
    assert data["chat_list"][1]["name"] == "dummy3"
    assert data["chat_list"][1]["last_name"] == "3"
    assert data["chat_list"][1]["status"] == 0
    assert data["chat_list"][1]["distance"]
    assert data["chat_list"][1]["fancy"] == 3
    assert data["chat_list"][1]["new"] == False

    # 채팅방 내용 확인하기
    response = test_client.get(
        f"/api/chat/msg?target_id={id+1}&time={quote(datetime.now(KST).strftime(TIME_STR_TYPE))}"
    )
    data = json.loads(response.data.decode("utf-8"))
    assert response.status_code == StatusCode.OK
    assert len(data["msg_list"]) == 2
    assert data["msg_list"][0]["sender_id"] == id + 1
    assert data["msg_list"][0]["message"] == "hello"
    assert data["msg_list"][0]["msg_time"]
    assert data["msg_list"][0]["msg_new"] == False
    assert data["msg_list"][1]["sender_id"] == id + 1
    assert data["msg_list"][1]["message"] == ""
    assert data["msg_list"][1]["msg_time"]
    assert data["msg_list"][1]["msg_new"] == False

    # chat 목록 보기
    response = test_client.get(f"/api/chat/list")
    data = json.loads(response.data.decode("utf-8"))
    assert response.status_code == StatusCode.OK
    assert len(data["chat_list"]) == 2
    assert data["chat_list"][0]["id"] == id + 1
    assert data["chat_list"][0]["name"] == "dummy2"
    assert data["chat_list"][0]["last_name"] == "2"
    assert data["chat_list"][0]["status"] == 0
    assert data["chat_list"][0]["distance"]
    assert data["chat_list"][0]["fancy"] == 3
    assert data["chat_list"][0]["new"] == False
    assert data["chat_list"][1]["id"] == id + 2

    # 로그아웃
    response = test_client.post(
        f"/api/user/logout",
        content_type="application/json",
    )
    assert response.status_code == StatusCode.OK


# chat msg 확인
def test_chat_msg(test_client):
    # 로그인
    response = test_client.post(
        f"/api/user/login",
        data=json.dumps(
            {
                "login_id": duplicated_login,
                "pw": valid_pw,
            }
        ),
        content_type="application/json",
    )
    data = json.loads(response.data.decode("utf-8"))
    assert response.status_code == StatusCode.OK
    id = data["id"]

    # 유저 fancy 하기
    response = test_client.patch(
        f"/api/history/fancy",
        data=json.dumps({"target_id": id + 1}),
        content_type="application/json",
    )
    data = json.loads(response.data.decode("utf-8"))
    assert response.status_code == StatusCode.OK

    # fancy 받기
    fancy(id + 1, target_id=id)

    # 채팅방 내용 확인하기 (최신)
    response = test_client.get(
        f"/api/chat/msg?target_id={id+1}&time={quote(datetime.now(KST).strftime(TIME_STR_TYPE))}"
    )
    data = json.loads(response.data.decode("utf-8"))
    assert response.status_code == StatusCode.OK
    assert len(data["msg_list"]) == 1
    assert data["msg_list"][0]["sender_id"] == id + 1
    assert data["msg_list"][0]["message"] == ""
    assert data["msg_list"][0]["msg_new"] == False

    # 채팅 받기
    from app.socket.socketService import send_message

    send_message({"recver_id": id, "message": "hello"}, sender_id=id + 1)

    # chat 목록 보기
    response = test_client.get(f"/api/chat/list")
    data = json.loads(response.data.decode("utf-8"))
    assert response.status_code == StatusCode.OK
    assert len(data["chat_list"]) == 1
    assert data["chat_list"][0]["id"] == id + 1
    assert data["chat_list"][0]["name"] == "dummy2"
    assert data["chat_list"][0]["last_name"] == "2"
    assert data["chat_list"][0]["status"] == 0
    assert data["chat_list"][0]["distance"]
    assert data["chat_list"][0]["fancy"] == 3
    assert data["chat_list"][0]["new"] == True

    # 채팅 보내기
    send_message({"recver_id": id + 1, "message": "hello dummy"}, sender_id=id)

    # chat 목록 보기
    response = test_client.get(f"/api/chat/list")
    data = json.loads(response.data.decode("utf-8"))
    assert response.status_code == StatusCode.OK
    assert len(data["chat_list"]) == 1
    assert data["chat_list"][0]["id"] == id + 1
    assert data["chat_list"][0]["name"] == "dummy2"
    assert data["chat_list"][0]["last_name"] == "2"
    assert data["chat_list"][0]["status"] == 0
    assert data["chat_list"][0]["distance"]
    assert data["chat_list"][0]["fancy"] == 3
    assert data["chat_list"][0]["new"] == False

    # 채팅 받기
    send_message({"recver_id": id, "message": "1"}, sender_id=id + 1)
    send_message({"recver_id": id, "message": "2"}, sender_id=id + 1)
    send_message({"recver_id": id, "message": "3"}, sender_id=id + 1)

    # chat 목록 보기
    response = test_client.get(f"/api/chat/list")
    data = json.loads(response.data.decode("utf-8"))
    assert response.status_code == StatusCode.OK
    assert len(data["chat_list"]) == 1
    assert data["chat_list"][0]["id"] == id + 1
    assert data["chat_list"][0]["name"] == "dummy2"
    assert data["chat_list"][0]["last_name"] == "2"
    assert data["chat_list"][0]["status"] == 0
    assert data["chat_list"][0]["distance"]
    assert data["chat_list"][0]["fancy"] == 3
    assert data["chat_list"][0]["new"] == True

    # 채팅방 내용 확인하기 (최신)
    response = test_client.get(
        f"/api/chat/msg?target_id={id+1}&time={quote(datetime.now(KST).strftime(TIME_STR_TYPE))}"
    )
    data = json.loads(response.data.decode("utf-8"))
    assert response.status_code == StatusCode.OK
    assert len(data["msg_list"]) == 5  # const.py에 정의된 MAX_CHAT_MSG_COUNT
    assert data["msg_list"][0]["sender_id"] == id + 1
    assert data["msg_list"][0]["message"] == "3"
    assert data["msg_list"][0]["msg_new"] == False
    assert data["msg_list"][1]["sender_id"] == id + 1
    assert data["msg_list"][1]["message"] == "2"
    assert data["msg_list"][1]["msg_new"] == False
    assert data["msg_list"][2]["sender_id"] == id + 1
    assert data["msg_list"][2]["message"] == "1"
    assert data["msg_list"][2]["msg_new"] == False
    assert data["msg_list"][3]["sender_id"] == id
    assert data["msg_list"][3]["message"] == "hello dummy"
    assert data["msg_list"][3]["msg_new"] == False
    assert data["msg_list"][4]["sender_id"] == id + 1
    assert data["msg_list"][4]["message"] == "hello"
    assert data["msg_list"][4]["msg_new"] == False

    # 채팅방 내용 확인하기 (중간1)
    response = test_client.get(
        f"/api/chat/msg?target_id={id+1}&time={quote(data['msg_list'][2]['msg_time'])}"
    )
    data = json.loads(response.data.decode("utf-8"))
    assert response.status_code == StatusCode.OK
    assert len(data["msg_list"]) == 3
    assert data["msg_list"][0]["sender_id"] == id
    assert data["msg_list"][0]["message"] == "hello dummy"
    assert data["msg_list"][0]["msg_new"] == False
    assert data["msg_list"][1]["sender_id"] == id + 1
    assert data["msg_list"][1]["message"] == "hello"
    assert data["msg_list"][1]["msg_new"] == False
    assert data["msg_list"][2]["sender_id"] == id + 1
    assert data["msg_list"][2]["message"] == ""
    assert data["msg_list"][2]["msg_new"] == False

    # 채팅방 내용 확인하기 (중간2)
    response = test_client.get(
        f"/api/chat/msg?target_id={id+1}&time={quote(data['msg_list'][0]['msg_time'])}"
    )
    data = json.loads(response.data.decode("utf-8"))
    assert response.status_code == StatusCode.OK
    assert len(data["msg_list"]) == 2
    assert data["msg_list"][0]["sender_id"] == id + 1
    assert data["msg_list"][0]["message"] == "hello"
    assert data["msg_list"][0]["msg_new"] == False
    assert data["msg_list"][1]["sender_id"] == id + 1
    assert data["msg_list"][1]["message"] == ""
    assert data["msg_list"][1]["msg_new"] == False

    # chat 목록 보기
    response = test_client.get(f"/api/chat/list")
    data = json.loads(response.data.decode("utf-8"))
    assert response.status_code == StatusCode.OK
    assert len(data["chat_list"]) == 1
    assert data["chat_list"][0]["id"] == id + 1
    assert data["chat_list"][0]["name"] == "dummy2"
    assert data["chat_list"][0]["last_name"] == "2"
    assert data["chat_list"][0]["status"] == 0
    assert data["chat_list"][0]["distance"]
    assert data["chat_list"][0]["fancy"] == 3
    assert data["chat_list"][0]["new"] == False

    # 로그아웃
    response = test_client.post(
        f"/api/user/logout",
        content_type="application/json",
    )
    assert response.status_code == StatusCode.OK


############################################################


def setup_function():
    from app.db.db import PostgreSQLFactory

    conn = PostgreSQLFactory.get_connection()
    conn.rollback()

    # 테스트 사용자 생성
    from app.user.userService import register_dummy
    from dummy_data import dummy_data

    for dummy in dummy_data:
        register_dummy(dummy)


def teardown_function():
    from app.db.db import PostgreSQLFactory

    conn = PostgreSQLFactory.get_connection()
    cursor = conn.cursor()

    try:
        # User 테이블의 모든 행 삭제
        cursor.execute('DELETE FROM "History";')
        cursor.execute('DELETE FROM "Block";')
        cursor.execute('DELETE FROM "Report";')
        cursor.execute('DELETE FROM "User";')

        # 모든 변경사항을 커밋
        conn.commit()

    except Exception as e:
        # 롤백 및 예외 처리
        conn.rollback()
        # raise e

    finally:
        # 커서와 연결 닫기
        cursor.close()
        PostgreSQLFactory.close_connection()
