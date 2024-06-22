import json
from datetime import datetime
from app.utils.const import StatusCode, KST, TIME_STR_TYPE
from urllib.parse import quote
from app.history.historyService import dummy_fancy as fancy, dummy_unfancy as unfancy


duplicated_login = "dummy1"
valid_pw = "ASDFasdf0"


# history 본 목록 확인
def test_view_history(test_client):
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

    # history 목록 보기 (empty)
    response = test_client.get(
        f"/api/history/history-list?time={quote(datetime.now(KST).strftime(TIME_STR_TYPE))}"
    )
    data = json.loads(response.data.decode("utf-8"))
    assert response.status_code == StatusCode.OK
    assert len(data["profile_list"]) == 0

    response = test_client.get(f"/api/history/history-list?time={first_kst}")
    data = json.loads(response.data.decode("utf-8"))
    assert response.status_code == StatusCode.OK
    assert len(data["profile_list"]) == 0

    # 유저 fancy 하기
    response = test_client.patch(
        f"/api/history/fancy",
        data=json.dumps({"target_id": id + 1}),
        content_type="application/json",
    )
    data = json.loads(response.data.decode("utf-8"))
    assert response.status_code == StatusCode.OK

    response = test_client.patch(
        f"/api/history/fancy",
        data=json.dumps({"target_id": id + 2}),
        content_type="application/json",
    )
    data = json.loads(response.data.decode("utf-8"))
    assert response.status_code == StatusCode.OK

    # fancy 받기
    fancy(id + 2, target_id=id)
    fancy(id + 3, target_id=id)

    # 중간 시간
    second_kst = quote(datetime.now(KST).strftime(TIME_STR_TYPE))

    # profile_detail 체크
    response = test_client.get(f"/api/user/profile-detail?id={id + 3}")
    data = json.loads(response.data.decode("utf-8"))
    assert response.status_code == StatusCode.OK
    assert data["login_id"] == "dummy4"

    response = test_client.get(f"/api/user/profile-detail?id={id + 4}")
    data = json.loads(response.data.decode("utf-8"))
    assert response.status_code == StatusCode.OK
    assert data["login_id"] == "dummy5"

    # history 목록 보기 (all)
    response = test_client.get(
        f"/api/history/history-list?time={quote(datetime.now(KST).strftime(TIME_STR_TYPE))}"
    )
    data = json.loads(response.data.decode("utf-8"))
    assert response.status_code == StatusCode.OK
    assert len(data["profile_list"]) == 4
    assert data["profile_list"][0]["name"] == "dummy5"
    assert data["profile_list"][0]["fancy"] == 0
    assert data["profile_list"][1]["name"] == "dummy4"
    assert data["profile_list"][1]["fancy"] == 2
    assert data["profile_list"][2]["name"] == "dummy3"
    assert data["profile_list"][2]["fancy"] == 3
    assert data["profile_list"][3]["name"] == "dummy2"
    assert data["profile_list"][3]["fancy"] == 1
    target = data["profile_list"][3]
    assert target["name"] == "dummy2"
    assert target["last_name"] == "2"
    assert target["distance"]
    assert target["fancy"] == 1
    assert target["age"] == 18
    assert target["picture"]
    assert target["time"]

    response = test_client.get(
        f"/api/history/history-list?time={quote(datetime.now(KST).strftime(TIME_STR_TYPE))}"
    )
    data = json.loads(response.data.decode("utf-8"))
    assert response.status_code == StatusCode.OK
    assert len(data["profile_list"]) == 4
    assert data["profile_list"][0]["name"] == "dummy5"
    assert data["profile_list"][0]["fancy"] == 0
    assert data["profile_list"][1]["name"] == "dummy4"
    assert data["profile_list"][1]["fancy"] == 2
    assert data["profile_list"][2]["name"] == "dummy3"
    assert data["profile_list"][2]["fancy"] == 3
    assert data["profile_list"][3]["name"] == "dummy2"
    assert data["profile_list"][3]["fancy"] == 1
    target = data["profile_list"][3]
    assert target["name"] == "dummy2"
    assert target["last_name"] == "2"
    assert target["distance"]
    assert target["fancy"] == 1
    assert target["age"] == 18
    assert target["picture"]
    assert target["time"]

    # history 목록 보기 (middle)
    response = test_client.get(f"/api/history/history-list?time={second_kst}")
    data = json.loads(response.data.decode("utf-8"))
    assert response.status_code == StatusCode.OK
    assert len(data["profile_list"]) == 2
    assert data["profile_list"][0]["name"] == "dummy3"
    assert data["profile_list"][0]["fancy"] == 3
    assert data["profile_list"][1]["name"] == "dummy2"
    assert data["profile_list"][1]["fancy"] == 1
    target = data["profile_list"][1]
    assert target["name"] == "dummy2"
    assert target["last_name"] == "2"
    assert target["distance"]
    assert target["fancy"] == 1
    assert target["age"] == 18
    assert target["picture"]
    assert target["time"]

    # history 목록 보기 (empty)
    response = test_client.get(f"/api/history/history-list?time={first_kst}")
    data = json.loads(response.data.decode("utf-8"))
    assert response.status_code == StatusCode.OK
    assert len(data["profile_list"]) == 0

    # profile_detail 체크 (확인 시간 업데이트)
    response = test_client.get(f"/api/user/profile-detail?id={id + 1}")
    data = json.loads(response.data.decode("utf-8"))
    assert response.status_code == StatusCode.OK
    assert data["login_id"] == "dummy2"
    assert data["status"] == 0
    assert data["last_online"]
    assert data["fame"]
    assert data["gender"] == 4
    assert data["taste"] == 2
    assert data["bio"] == "2"
    assert data["tags"] == [4, 11, 12]
    assert data["hate_tags"] == [13]
    assert data["emoji"] == [16]
    assert data["hate_emoji"] == []
    assert data["similar"] == True
    assert data["pictures"]

    # history 목록 보기 (all)
    response = test_client.get(
        f"/api/history/history-list?time={quote(datetime.now(KST).strftime(TIME_STR_TYPE))}"
    )
    data = json.loads(response.data.decode("utf-8"))
    assert response.status_code == StatusCode.OK
    assert len(data["profile_list"]) == 4
    assert data["profile_list"][0]["name"] == "dummy2"
    assert data["profile_list"][0]["fancy"] == 1
    assert data["profile_list"][1]["name"] == "dummy5"
    assert data["profile_list"][1]["fancy"] == 0
    assert data["profile_list"][2]["name"] == "dummy4"
    assert data["profile_list"][2]["fancy"] == 2
    assert data["profile_list"][3]["name"] == "dummy3"
    assert data["profile_list"][3]["fancy"] == 3
    target = data["profile_list"][0]
    assert target["name"] == "dummy2"
    assert target["last_name"] == "2"
    assert target["distance"]
    assert target["fancy"] == 1
    assert target["age"] == 18
    assert target["picture"]
    assert target["time"]

    # 로그아웃
    response = test_client.post(f"/api/user/logout")
    assert response.status_code == StatusCode.OK


# fancy 받은 목록 확인
def test_fancy_history(test_client):
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

    # fancy 받은 목록 보기 (empty)
    response = test_client.get(f"/api/history/fancy-list?time={first_kst}")
    data = json.loads(response.data.decode("utf-8"))
    assert response.status_code == StatusCode.OK
    assert len(data["profile_list"]) == 0

    # 유저 fancy 하기
    response = test_client.patch(
        f"/api/history/fancy",
        data=json.dumps({"target_id": id + 1}),
        content_type="application/json",
    )
    data = json.loads(response.data.decode("utf-8"))
    assert response.status_code == StatusCode.OK

    response = test_client.patch(
        f"/api/history/fancy",
        data=json.dumps({"target_id": id + 2}),
        content_type="application/json",
    )
    data = json.loads(response.data.decode("utf-8"))
    assert response.status_code == StatusCode.OK

    # 스스로 fancy 하기 (실패)
    response = test_client.patch(
        f"/api/history/fancy",
        data=json.dumps({"target_id": id}),
        content_type="application/json",
    )
    data = json.loads(response.data.decode("utf-8"))
    assert response.status_code == StatusCode.BAD_REQUEST

    # fancy 받기 (1)
    fancy(id + 1, target_id=id)

    # 중간 시간
    second_kst = quote(datetime.now(KST).strftime(TIME_STR_TYPE))

    # fancy 받기 (2)
    fancy(id + 3, target_id=id)

    # fancy 받은 목록 보기 (all)
    response = test_client.get(
        f"/api/history/fancy-list?time={quote(datetime.now(KST).strftime(TIME_STR_TYPE))}"
    )
    data = json.loads(response.data.decode("utf-8"))
    assert response.status_code == StatusCode.OK
    assert len(data["profile_list"]) == 2
    assert data["profile_list"][0]["name"] == "dummy4"
    assert data["profile_list"][0]["fancy"] == 2
    assert data["profile_list"][1]["name"] == "dummy2"
    assert data["profile_list"][1]["fancy"] == 3
    target = data["profile_list"][1]
    assert target["name"] == "dummy2"
    assert target["last_name"] == "2"
    assert target["distance"]
    assert target["fancy"] == 3
    assert target["age"] == 18
    assert target["picture"]
    assert target["time"]

    response = test_client.get(
        f"/api/history/fancy-list?time={quote(datetime.now(KST).strftime(TIME_STR_TYPE))}"
    )
    data = json.loads(response.data.decode("utf-8"))
    assert response.status_code == StatusCode.OK
    assert len(data["profile_list"]) == 2
    assert data["profile_list"][0]["name"] == "dummy4"
    assert data["profile_list"][0]["fancy"] == 2
    assert data["profile_list"][1]["name"] == "dummy2"
    assert data["profile_list"][1]["fancy"] == 3
    target = data["profile_list"][1]
    assert target["name"] == "dummy2"
    assert target["last_name"] == "2"
    assert target["distance"]
    assert target["fancy"] == 3
    assert target["age"] == 18
    assert target["picture"]
    assert target["time"]

    # fancy 받은 목록 보기 (middle)
    response = test_client.get(f"/api/history/fancy-list?time={second_kst}")
    data = json.loads(response.data.decode("utf-8"))
    assert response.status_code == StatusCode.OK
    assert len(data["profile_list"]) == 1
    assert data["profile_list"][0]["name"] == "dummy2"
    assert data["profile_list"][0]["fancy"] == 3
    target = data["profile_list"][0]
    assert target["name"] == "dummy2"
    assert target["last_name"] == "2"
    assert target["distance"]
    assert target["fancy"] == 3
    assert target["age"] == 18
    assert target["picture"]
    assert target["time"]

    # unfancy 하기
    response = test_client.patch(
        f"/api/history/unfancy",
        data=json.dumps({"target_id": id + 1}),
        content_type="application/json",
    )
    data = json.loads(response.data.decode("utf-8"))
    assert response.status_code == StatusCode.OK

    # fancy 받은 목록 보기 (all)
    response = test_client.get(
        f"/api/history/fancy-list?time={quote(datetime.now(KST).strftime(TIME_STR_TYPE))}"
    )
    data = json.loads(response.data.decode("utf-8"))
    assert response.status_code == StatusCode.OK
    assert len(data["profile_list"]) == 2
    assert data["profile_list"][0]["name"] == "dummy4"
    assert data["profile_list"][0]["fancy"] == 2
    assert data["profile_list"][1]["name"] == "dummy2"
    assert data["profile_list"][1]["fancy"] == 2
    target = data["profile_list"][1]
    assert target["name"] == "dummy2"
    assert target["last_name"] == "2"
    assert target["distance"]
    assert target["fancy"] == 2
    assert target["age"] == 18
    assert target["picture"]
    assert target["time"]

    # unfancy 받기
    unfancy(id + 3, target_id=id)

    # fancy 받은 목록 보기 (all)
    response = test_client.get(
        f"/api/history/fancy-list?time={quote(datetime.now(KST).strftime(TIME_STR_TYPE))}"
    )
    data = json.loads(response.data.decode("utf-8"))
    assert response.status_code == StatusCode.OK
    assert len(data["profile_list"]) == 1
    assert data["profile_list"][0]["name"] == "dummy2"
    assert data["profile_list"][0]["fancy"] == 2
    target = data["profile_list"][0]
    assert target["name"] == "dummy2"
    assert target["last_name"] == "2"
    assert target["distance"]
    assert target["fancy"] == 2
    assert target["age"] == 18
    assert target["picture"]
    assert target["time"]

    # 로그아웃
    response = test_client.post(f"/api/user/logout")
    assert response.status_code == StatusCode.OK


# fancy 테스트
def test_fancy(test_client):
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

    # history 목록 보기
    response = test_client.get(
        f"/api/history/history-list?time={quote(datetime.now(KST).strftime(TIME_STR_TYPE))}"
    )
    data = json.loads(response.data.decode("utf-8"))
    assert response.status_code == StatusCode.OK
    assert len(data["profile_list"]) == 0

    # 유저 fancy 하기
    response = test_client.patch(
        f"/api/history/fancy",
        data=json.dumps({"target_id": id + 1}),
        content_type="application/json",
    )
    data = json.loads(response.data.decode("utf-8"))
    assert response.status_code == StatusCode.OK

    response = test_client.patch(
        f"/api/history/fancy",
        data=json.dumps({"target_id": id + 2}),
        content_type="application/json",
    )
    data = json.loads(response.data.decode("utf-8"))
    assert response.status_code == StatusCode.OK

    # history 목록 보기
    response = test_client.get(
        f"/api/history/history-list?time={quote(datetime.now(KST).strftime(TIME_STR_TYPE))}"
    )
    data = json.loads(response.data.decode("utf-8"))
    assert response.status_code == StatusCode.OK
    assert len(data["profile_list"]) == 2
    assert data["profile_list"][0]["name"] == "dummy3"
    assert data["profile_list"][0]["fancy"] == 1
    assert data["profile_list"][1]["name"] == "dummy2"
    assert data["profile_list"][1]["fancy"] == 1
    target = data["profile_list"][1]
    assert target["name"] == "dummy2"
    assert target["last_name"] == "2"
    assert target["distance"]
    assert target["fancy"] == 1
    assert target["age"] == 18
    assert target["picture"]
    assert target["time"]

    # 유저 unfancy 하기
    response = test_client.patch(
        f"/api/history/unfancy",
        data=json.dumps({"target_id": id + 1}),
        content_type="application/json",
    )
    data = json.loads(response.data.decode("utf-8"))
    assert response.status_code == StatusCode.OK

    # history 목록 보기
    response = test_client.get(
        f"/api/history/history-list?time={quote(datetime.now(KST).strftime(TIME_STR_TYPE))}"
    )
    data = json.loads(response.data.decode("utf-8"))
    assert response.status_code == StatusCode.OK
    assert len(data["profile_list"]) == 2
    assert data["profile_list"][0]["name"] == "dummy2"
    assert data["profile_list"][0]["fancy"] == 0
    assert data["profile_list"][1]["name"] == "dummy3"
    assert data["profile_list"][1]["fancy"] == 1
    target = data["profile_list"][0]
    assert target["name"] == "dummy2"
    assert target["last_name"] == "2"
    assert target["distance"]
    assert target["fancy"] == 0
    assert target["age"] == 18
    assert target["picture"]
    assert target["time"]

    # 유저 다시 fancy 하기
    response = test_client.patch(
        f"/api/history/fancy",
        data=json.dumps({"target_id": id + 1}),
        content_type="application/json",
    )
    data = json.loads(response.data.decode("utf-8"))
    assert response.status_code == StatusCode.OK

    # history 목록 보기
    response = test_client.get(
        f"/api/history/history-list?time={quote(datetime.now(KST).strftime(TIME_STR_TYPE))}"
    )
    data = json.loads(response.data.decode("utf-8"))
    assert response.status_code == StatusCode.OK
    assert len(data["profile_list"]) == 2
    assert data["profile_list"][0]["name"] == "dummy2"
    assert data["profile_list"][0]["fancy"] == 1
    assert data["profile_list"][1]["name"] == "dummy3"
    assert data["profile_list"][1]["fancy"] == 1
    target = data["profile_list"][0]
    assert target["name"] == "dummy2"
    assert target["last_name"] == "2"
    assert target["distance"]
    assert target["fancy"] == 1
    assert target["age"] == 18
    assert target["picture"]
    assert target["time"]

    # 없는 유저 fancy 하기
    response = test_client.patch(
        f"/api/history/fancy",
        data=json.dumps({"target_id": id + 100}),
        content_type="application/json",
    )
    assert response.status_code == StatusCode.BAD_REQUEST

    # 유저 block 하기
    response = test_client.post(
        f"/api/user/block",
        data=json.dumps({"target_id": id + 2}),
        content_type="application/json",
    )
    assert response.status_code == StatusCode.OK

    # history 목록 보기
    response = test_client.get(
        f"/api/history/history-list?time={quote(datetime.now(KST).strftime(TIME_STR_TYPE))}"
    )
    data = json.loads(response.data.decode("utf-8"))
    assert response.status_code == StatusCode.OK
    assert len(data["profile_list"]) == 1
    assert data["profile_list"][0]["name"] == "dummy2"
    assert data["profile_list"][0]["fancy"] == 1
    target = data["profile_list"][0]
    assert target["name"] == "dummy2"
    assert target["last_name"] == "2"
    assert target["distance"]
    assert target["fancy"] == 1
    assert target["age"] == 18
    assert target["picture"]
    assert target["time"]

    # block한 유저 fancy
    response = test_client.patch(
        f"/api/history/fancy",
        data=json.dumps({"target_id": id + 2}),
        content_type="application/json",
    )
    assert response.status_code == StatusCode.BAD_REQUEST

    # 로그아웃
    response = test_client.post(f"/api/user/logout")
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
