import json
from app.utils.const import StatusCode

duplicated_login = "dummy1"
valid_pw = "ASDFasdf0"


# 유저 검색 등
def test_user_api(test_client):
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

    # 유저 검색
    response = test_client.post(
        f"/api/user/search",
        data=json.dumps(
            {
                "min_age": 10,
                "max_age": 40,
                "distance": 40,
                "tags": [4, 11],
                "fame": 0,
            }
        ),
        content_type="application/json",
    )
    data = json.loads(response.data.decode("utf-8"))
    assert response.status_code == StatusCode.OK
    assert len(data["profile_list"]) == 1
    target_id = data["profile_list"][0]["id"]

    # tea 추천
    response = test_client.get(f"/api/tea/")
    data = json.loads(response.data.decode("utf-8"))
    assert response.status_code == StatusCode.OK
    assert len(data["profile_list"]) == 3
    assert data["profile_list"][0]["name"] == "dummy4"
    assert data["profile_list"][1]["name"] == "dummy2"
    assert data["profile_list"][2]["name"] == "dummy3"
    target = data["profile_list"][1]
    assert target["name"] == "dummy2"
    assert target["last_name"] == "2"
    assert target["distance"]
    assert target["fancy"] == 0
    assert target["age"] == 18
    assert target["picture"]
    assert target["time"] is None

    # 신고 (성공)
    response = test_client.post(
        f"/api/user/report",
        data=json.dumps({"target_id": target_id, "reason": 1}),
        content_type="application/json",
    )
    assert response.status_code == StatusCode.OK

    # (신고, 블록 후) tea 추천
    response = test_client.get(f"/api/tea/")
    data = json.loads(response.data.decode("utf-8"))
    assert response.status_code == StatusCode.OK
    assert len(data["profile_list"]) == 2
    assert data["profile_list"][0]["name"] == "dummy4"
    assert data["profile_list"][1]["name"] == "dummy3"

    # 로그아웃
    response = test_client.post(f"/api/user/logout")
    assert response.status_code == StatusCode.OK


############################################################


def setup_function():
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
