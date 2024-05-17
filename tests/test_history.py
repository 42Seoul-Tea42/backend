import json
from datetime import datetime
from app.utils.const import StatusCode, KST, TIME_STR_TYPE
from urllib.parse import quote
from app.history.historyService import fancy


duplicated_login = "dummy1"
valid_pw = "ASDFasdf0"


# # history 본 목록 확인
# def test_view_history(test_client):
#     # 로그인
#     response = test_client.post(
#         f"/user/login",
#         data=json.dumps(
#             {
#                 "login_id": duplicated_login,
#                 "pw": valid_pw,
#             }
#         ),
#         content_type="application/json",
#     )
#     data = json.loads(response.data.decode("utf-8"))
#     assert response.status_code == StatusCode.OK
#     id = data["id"]

#     # 최초 시간
#     first_kst = quote(datetime.now(KST).strftime(TIME_STR_TYPE))

#     # history 목록 보기 (empty)
#     response = test_client.get(f"/history/history-list")
#     data = json.loads(response.data.decode("utf-8"))
#     assert response.status_code == StatusCode.OK
#     assert len(data["profiles"]) == 0

#     response = test_client.get(f"/history/history-list?time={first_kst}")
#     data = json.loads(response.data.decode("utf-8"))
#     assert response.status_code == StatusCode.OK
#     assert len(data["profiles"]) == 0

#     # 유저 fancy 하기
#     response = test_client.patch(
#         f"/history/fancy",
#         data=json.dumps({"target_id": id + 1}),
#         content_type="application/json",
#     )
#     data = json.loads(response.data.decode("utf-8"))
#     assert response.status_code == StatusCode.OK

#     response = test_client.patch(
#         f"/history/fancy",
#         data=json.dumps({"target_id": id + 2}),
#         content_type="application/json",
#     )
#     data = json.loads(response.data.decode("utf-8"))
#     assert response.status_code == StatusCode.OK

#     # fancy 받기
#     fancy({"target_id": id}, id + 2)
#     fancy({"target_id": id}, id + 3)

#     # 중간 시간
#     second_kst = quote(datetime.now(KST).strftime(TIME_STR_TYPE))

#     # profile_detail 체크
#     response = test_client.get(f"/user/profile-detail?id={id + 3}")
#     data = json.loads(response.data.decode("utf-8"))
#     assert response.status_code == StatusCode.OK
#     assert data["login_id"] == "dummy4"

#     response = test_client.get(f"/user/profile-detail?id={id + 4}")
#     data = json.loads(response.data.decode("utf-8"))
#     assert response.status_code == StatusCode.OK
#     assert data["login_id"] == "dummy5"

#     # history 목록 보기 (all)
#     response = test_client.get(
#         f"/history/history-list?time={quote(datetime.now(KST).strftime(TIME_STR_TYPE))}"
#     )
#     data = json.loads(response.data.decode("utf-8"))
#     assert response.status_code == StatusCode.OK
#     assert len(data["profiles"]) == 4
#     assert data["profiles"][0]["name"] == "dummy5"
#     assert data["profiles"][0]["fancy"] == 0
#     assert data["profiles"][1]["name"] == "dummy4"
#     assert data["profiles"][1]["fancy"] == 2
#     assert data["profiles"][2]["name"] == "dummy3"
#     assert data["profiles"][2]["fancy"] == 3
#     assert data["profiles"][3]["name"] == "dummy2"
#     assert data["profiles"][3]["fancy"] == 1

#     response = test_client.get(f"/history/history-list")
#     data = json.loads(response.data.decode("utf-8"))
#     assert response.status_code == StatusCode.OK
#     assert len(data["profiles"]) == 4
#     assert data["profiles"][0]["name"] == "dummy5"
#     assert data["profiles"][0]["fancy"] == 0
#     assert data["profiles"][1]["name"] == "dummy4"
#     assert data["profiles"][1]["fancy"] == 2
#     assert data["profiles"][2]["name"] == "dummy3"
#     assert data["profiles"][2]["fancy"] == 3
#     assert data["profiles"][3]["name"] == "dummy2"
#     assert data["profiles"][3]["fancy"] == 1

#     # history 목록 보기 (middle)
#     response = test_client.get(f"/history/history-list?time={second_kst}")
#     data = json.loads(response.data.decode("utf-8"))
#     assert response.status_code == StatusCode.OK
#     assert len(data["profiles"]) == 2
#     assert data["profiles"][0]["name"] == "dummy3"
#     assert data["profiles"][0]["fancy"] == 3
#     assert data["profiles"][1]["name"] == "dummy2"
#     assert data["profiles"][1]["fancy"] == 1

#     # history 목록 보기 (empty)
#     response = test_client.get(f"/history/history-list?time={first_kst}")
#     data = json.loads(response.data.decode("utf-8"))
#     assert response.status_code == StatusCode.OK
#     assert len(data["profiles"]) == 0

#     # profile_detail 체크 (확인 시간 업데이트)
#     response = test_client.get(f"/user/profile-detail?id={id + 1}")
#     data = json.loads(response.data.decode("utf-8"))
#     assert response.status_code == StatusCode.OK
#     assert data["login_id"] == "dummy2"

#     # history 목록 보기 (all)
#     response = test_client.get(f"/history/history-list")
#     data = json.loads(response.data.decode("utf-8"))
#     assert response.status_code == StatusCode.OK
#     assert len(data["profiles"]) == 4
#     assert data["profiles"][0]["name"] == "dummy2"
#     assert data["profiles"][0]["fancy"] == 1
#     assert data["profiles"][1]["name"] == "dummy5"
#     assert data["profiles"][1]["fancy"] == 0
#     assert data["profiles"][2]["name"] == "dummy4"
#     assert data["profiles"][2]["fancy"] == 2
#     assert data["profiles"][3]["name"] == "dummy3"
#     assert data["profiles"][3]["fancy"] == 3


# # fancy 받은 목록 확인
# def test_fancy_history(test_client):
#     # 로그인
#     response = test_client.post(
#         f"/user/login",
#         data=json.dumps(
#             {
#                 "login_id": duplicated_login,
#                 "pw": valid_pw,
#             }
#         ),
#         content_type="application/json",
#     )
#     data = json.loads(response.data.decode("utf-8"))
#     assert response.status_code == StatusCode.OK
#     id = data["id"]

#     # 최초 시간
#     first_kst = quote(datetime.now(KST).strftime(TIME_STR_TYPE))

#     # fancy 받은 목록 보기 (empty)
#     response = test_client.get(f"/history/fancy-list")
#     data = json.loads(response.data.decode("utf-8"))
#     assert response.status_code == StatusCode.OK
#     assert len(data["profiles"]) == 0

#     response = test_client.get(f"/history/fancy-list?time={first_kst}")
#     data = json.loads(response.data.decode("utf-8"))
#     assert response.status_code == StatusCode.OK
#     assert len(data["profiles"]) == 0

#     # 유저 fancy 하기
#     response = test_client.patch(
#         f"/history/fancy",
#         data=json.dumps({"target_id": id + 1}),
#         content_type="application/json",
#     )
#     data = json.loads(response.data.decode("utf-8"))
#     assert response.status_code == StatusCode.OK

#     response = test_client.patch(
#         f"/history/fancy",
#         data=json.dumps({"target_id": id + 2}),
#         content_type="application/json",
#     )
#     data = json.loads(response.data.decode("utf-8"))
#     assert response.status_code == StatusCode.OK

#     # 스스로 fancy 하기 (실패)
#     response = test_client.patch(
#         f"/history/fancy",
#         data=json.dumps({"target_id": id}),
#         content_type="application/json",
#     )
#     data = json.loads(response.data.decode("utf-8"))
#     assert response.status_code == StatusCode.BAD_REQUEST

#     # fancy 받기 (1)
#     fancy({"target_id": id}, id + 1)

#     # 중간 시간
#     second_kst = quote(datetime.now(KST).strftime(TIME_STR_TYPE))

#     # fancy 받기 (2)
#     fancy({"target_id": id}, id + 3)

#     # fancy 받은 목록 보기 (all)
#     response = test_client.get(
#         f"/history/fancy-list?time={quote(datetime.now(KST).strftime(TIME_STR_TYPE))}"
#     )
#     data = json.loads(response.data.decode("utf-8"))
#     assert response.status_code == StatusCode.OK
#     assert len(data["profiles"]) == 2
#     assert data["profiles"][0]["name"] == "dummy4"
#     assert data["profiles"][0]["fancy"] == 2
#     assert data["profiles"][1]["name"] == "dummy2"
#     assert data["profiles"][1]["fancy"] == 3

#     response = test_client.get(f"/history/fancy-list")
#     data = json.loads(response.data.decode("utf-8"))
#     assert response.status_code == StatusCode.OK
#     assert len(data["profiles"]) == 2
#     assert data["profiles"][0]["name"] == "dummy4"
#     assert data["profiles"][0]["fancy"] == 2
#     assert data["profiles"][1]["name"] == "dummy2"
#     assert data["profiles"][1]["fancy"] == 3

#     # fancy 받은 목록 보기 (middle)
#     response = test_client.get(f"/history/fancy-list?time={second_kst}")
#     data = json.loads(response.data.decode("utf-8"))
#     assert response.status_code == StatusCode.OK
#     assert len(data["profiles"]) == 1
#     assert data["profiles"][0]["name"] == "dummy2"
#     assert data["profiles"][0]["fancy"] == 3

#     # unfancy 하기
#     response = test_client.patch(
#         f"/history/fancy",
#         data=json.dumps({"target_id": id + 1}),
#         content_type="application/json",
#     )
#     data = json.loads(response.data.decode("utf-8"))
#     assert response.status_code == StatusCode.OK

#     # fancy 받은 목록 보기 (all)
#     response = test_client.get(f"/history/fancy-list")
#     data = json.loads(response.data.decode("utf-8"))
#     assert response.status_code == StatusCode.OK
#     assert len(data["profiles"]) == 2
#     assert data["profiles"][0]["name"] == "dummy4"
#     assert data["profiles"][0]["fancy"] == 2
#     assert data["profiles"][1]["name"] == "dummy2"
#     assert data["profiles"][1]["fancy"] == 2

#     # unfancy 받기
#     fancy({"target_id": id}, id + 3)

#     # fancy 받은 목록 보기 (all)
#     response = test_client.get(f"/history/fancy-list")
#     data = json.loads(response.data.decode("utf-8"))
#     assert response.status_code == StatusCode.OK
#     assert len(data["profiles"]) == 1
#     assert data["profiles"][0]["name"] == "dummy2"
#     assert data["profiles"][0]["fancy"] == 2


# # fancy 테스트
# def test_fancy(test_client):
#     # 로그인
#     response = test_client.post(
#         f"/user/login",
#         data=json.dumps(
#             {
#                 "login_id": duplicated_login,
#                 "pw": valid_pw,
#             }
#         ),
#         content_type="application/json",
#     )
#     data = json.loads(response.data.decode("utf-8"))
#     assert response.status_code == StatusCode.OK
#     id = data["id"]

#     # history 목록 보기
#     response = test_client.get(f"/history/history-list")
#     data = json.loads(response.data.decode("utf-8"))
#     assert response.status_code == StatusCode.OK
#     assert len(data["profiles"]) == 0

#     # 유저 fancy 하기
#     response = test_client.patch(
#         f"/history/fancy",
#         data=json.dumps({"target_id": id + 1}),
#         content_type="application/json",
#     )
#     data = json.loads(response.data.decode("utf-8"))
#     assert response.status_code == StatusCode.OK

#     response = test_client.patch(
#         f"/history/fancy",
#         data=json.dumps({"target_id": id + 2}),
#         content_type="application/json",
#     )
#     data = json.loads(response.data.decode("utf-8"))
#     assert response.status_code == StatusCode.OK

#     # history 목록 보기
#     response = test_client.get(f"/history/history-list")
#     data = json.loads(response.data.decode("utf-8"))
#     assert response.status_code == StatusCode.OK
#     assert len(data["profiles"]) == 2
#     assert data["profiles"][0]["name"] == "dummy3"
#     assert data["profiles"][0]["fancy"] == 1
#     assert data["profiles"][1]["name"] == "dummy2"
#     assert data["profiles"][1]["fancy"] == 1

#     # 유저 unfancy 하기
#     response = test_client.patch(
#         f"/history/fancy",
#         data=json.dumps({"target_id": id + 1}),
#         content_type="application/json",
#     )
#     data = json.loads(response.data.decode("utf-8"))
#     assert response.status_code == StatusCode.OK

#     # history 목록 보기
#     response = test_client.get(f"/history/history-list")
#     data = json.loads(response.data.decode("utf-8"))
#     assert response.status_code == StatusCode.OK
#     assert len(data["profiles"]) == 2
#     assert data["profiles"][0]["name"] == "dummy2"
#     assert data["profiles"][0]["fancy"] == 0
#     assert data["profiles"][1]["name"] == "dummy3"
#     assert data["profiles"][1]["fancy"] == 1

#     # 유저 다시 fancy 하기
#     response = test_client.patch(
#         f"/history/fancy",
#         data=json.dumps({"target_id": id + 1}),
#         content_type="application/json",
#     )
#     data = json.loads(response.data.decode("utf-8"))
#     assert response.status_code == StatusCode.OK

#     # history 목록 보기
#     response = test_client.get(f"/history/history-list")
#     data = json.loads(response.data.decode("utf-8"))
#     assert response.status_code == StatusCode.OK
#     assert len(data["profiles"]) == 2
#     assert data["profiles"][0]["name"] == "dummy2"
#     assert data["profiles"][0]["fancy"] == 1
#     assert data["profiles"][1]["name"] == "dummy3"
#     assert data["profiles"][1]["fancy"] == 1

#     # 없는 유저 fancy 하기
#     response = test_client.patch(
#         f"/history/fancy",
#         data=json.dumps({"target_id": id + 100}),
#         content_type="application/json",
#     )
#     assert response.status_code == StatusCode.BAD_REQUEST

#     # 유저 block 하기
#     response = test_client.post(
#         f"/user/block",
#         data=json.dumps({"target_id": id + 2}),
#         content_type="application/json",
#     )
#     assert response.status_code == StatusCode.OK

#     # history 목록 보기
#     response = test_client.get(f"/history/history-list")
#     data = json.loads(response.data.decode("utf-8"))
#     assert response.status_code == StatusCode.OK
#     assert len(data["profiles"]) == 1
#     assert data["profiles"][0]["name"] == "dummy2"
#     assert data["profiles"][0]["fancy"] == 1

#     # block한 유저 fancy
#     response = test_client.patch(
#         f"/history/fancy",
#         data=json.dumps({"target_id": id + 2}),
#         content_type="application/json",
#     )
#     assert response.status_code == StatusCode.BAD_REQUEST


############################################################


def setup_function():
    # 테스트 사용자 생성
    from app.user.userService import register_dummy
    from .dummy_data import dummy_data

    for dummy in dummy_data:
        register_dummy(dummy)


def teardown_function():
    from app.db.db import PostgreSQLFactory

    conn = PostgreSQLFactory.get_connection()
    cursor = conn.cursor()

    try:
        # User 테이블의 모든 행 삭제
        cursor.execute('DELETE FROM "User";')
        cursor.execute('DELETE FROM "History";')
        cursor.execute('DELETE FROM "Block";')
        cursor.execute('DELETE FROM "Report";')

        # 모든 변경사항을 커밋
        conn.commit()

    except Exception as e:
        # 롤백 및 예외 처리
        conn.rollback()
        raise e

    finally:
        # 커서와 연결 닫기
        cursor.close()
        PostgreSQLFactory.close_connection()
