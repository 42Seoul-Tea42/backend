import json
from app.utils.const import StatusCode

invalid_email = "dummy1@tea42"
invalid_email_2 = "d@tea42.com"
invalid_email_3 = "dummy1@t.com"
invalid_email_4 = "dummy1@tea42.c"
invalid_email_5 = "dummy1tea42.com"
invalid_email_6 = "dummy1@.com"
invalid_email_7 = "duasdfasdfasdfmmy1@teasdfasdfa42.comm"
duplicated_email = "dummy1@tea42.com"
valid_email = "dummy11@tea42.com"
valid_email_2 = "dummy1111@tea42.com"

invalid_login = "dum"
invalid_login_2 = "dumakskdkgksndek"
invalid_login_3 = "dum!sdfasdf"
invalid_login_4 = "dumasdf현"
duplicated_login = "dummy1"
valid_login = "dummy1111"
not_registered_login = "dummy2222"

short_pw = "pw"
not_valid_pw_1 = "password"
not_valid_pw_2 = "PASSWORD"
not_valid_pw_3 = "12345678"
not_valid_pw_4 = "pass1234"
not_valid_pw_5 = "PASS1234"
not_valid_pw_6 = "PASSword"
not_valid_pw_7 = "PASSword0현"
valid_pw = "ASDFasdf0"


# 이메일 중복 확인
def test_check_email_duplication(test_client):

    response = test_client.get(f"/api/user/check-email")
    assert response.status_code == StatusCode.BAD_REQUEST

    response = test_client.get(f"/api/user/check-email?email=")
    assert response.status_code == StatusCode.BAD_REQUEST

    response = test_client.get(f"/api/user/check-email?email=0000")
    assert response.status_code == StatusCode.BAD_REQUEST

    response = test_client.get(f"/api/user/check-email?email={invalid_email}")
    assert response.status_code == StatusCode.BAD_REQUEST

    response = test_client.get(f"/api/user/check-email?email={invalid_email_2}")
    assert response.status_code == StatusCode.BAD_REQUEST

    response = test_client.get(f"/api/user/check-email?email={invalid_email_3}")
    assert response.status_code == StatusCode.BAD_REQUEST

    response = test_client.get(f"/api/user/check-email?email={invalid_email_4}")
    assert response.status_code == StatusCode.BAD_REQUEST

    response = test_client.get(f"/api/user/check-email?email={invalid_email_5}")
    assert response.status_code == StatusCode.BAD_REQUEST

    response = test_client.get(f"/api/user/check-email?email={invalid_email_6}")
    assert response.status_code == StatusCode.BAD_REQUEST

    response = test_client.get(f"/api/user/check-email?email={invalid_email_7}")
    assert response.status_code == StatusCode.BAD_REQUEST

    response = test_client.get(f"/api/user/check-email?email={duplicated_email}")
    assert response.status_code == StatusCode.BAD_REQUEST

    response = test_client.get(
        f"/api/user/check-email?email={duplicated_email.upper()}"
    )
    assert response.status_code == StatusCode.BAD_REQUEST

    response = test_client.get(f"/api/user/check-email?email={valid_email}")
    assert response.status_code == StatusCode.OK

    response = test_client.get(f"/api/user/check-email?email={valid_email.upper()}")
    assert response.status_code == StatusCode.OK


# 로그인 아이디 중복 확인
def test_check_login_id_duplication(test_client):

    response = test_client.get(f"/api/user/check-id")
    assert response.status_code == StatusCode.BAD_REQUEST

    response = test_client.get(f"/api/user/check-id?")
    assert response.status_code == StatusCode.BAD_REQUEST

    response = test_client.get(f"/api/user/check-id?login_id=")
    assert response.status_code == StatusCode.BAD_REQUEST

    response = test_client.get(f"/api/user/check-id?login_id=0000")
    assert response.status_code == StatusCode.BAD_REQUEST

    response = test_client.get(f"/api/user/check-id?login_id={invalid_login}")
    assert response.status_code == StatusCode.BAD_REQUEST

    response = test_client.get(f"/api/user/check-id?login_id={invalid_login_2}")
    assert response.status_code == StatusCode.BAD_REQUEST

    response = test_client.get(f"/api/user/check-id?login_id={invalid_login_3}")
    assert response.status_code == StatusCode.BAD_REQUEST

    response = test_client.get(f"/api/user/check-id?login_id={invalid_login_4}")
    assert response.status_code == StatusCode.BAD_REQUEST

    response = test_client.get(f"/api/user/check-id?login_id={duplicated_login}")
    assert response.status_code == StatusCode.BAD_REQUEST

    response = test_client.get(
        f"/api/user/check-id?login_id={duplicated_login.upper()}"
    )
    assert response.status_code == StatusCode.BAD_REQUEST

    response = test_client.get(f"/api/user/check-id?login_id={valid_login}")
    assert response.status_code == StatusCode.OK

    response = test_client.get(f"/api/user/check-id?login_id={valid_login.upper()}")
    assert response.status_code == StatusCode.OK


# 패스워드 재설정 메일 요청
def test_request_pw_reset_mail(test_client):

    response = test_client.get(f"/api/user/reset-pw")
    assert response.status_code == StatusCode.BAD_REQUEST

    response = test_client.get(f"/api/user/reset-pw?login_id=")
    assert response.status_code == StatusCode.BAD_REQUEST

    response = test_client.get(f"/api/user/reset-pw?")
    assert response.status_code == StatusCode.BAD_REQUEST

    response = test_client.get(f"/api/user/reset-pw?login_id=0000")
    assert response.status_code == StatusCode.BAD_REQUEST

    response = test_client.get(f"/api/user/reset-pw?login_id={invalid_login}")
    assert response.status_code == StatusCode.BAD_REQUEST

    response = test_client.get(f"/api/user/reset-pw?login_id={not_registered_login}")
    assert response.status_code == StatusCode.BAD_REQUEST

    response = test_client.get(f"/api/user/reset-pw?login_id={duplicated_login}")
    data = json.loads(response.data.decode("utf-8"))
    prev_key = data["key"]
    assert response.status_code == StatusCode.OK
    assert data["key"]

    response = test_client.get(f"/api/user/reset-pw?login_id={duplicated_login.upper()}")
    data = json.loads(response.data.decode("utf-8"))
    assert response.status_code == StatusCode.OK
    assert data["key"]
    assert data["key"] != prev_key

    # 비밀번호 재설정하기
    response = test_client.post(
        f"/api/user/reset-pw",
        data=json.dumps({"pw": valid_pw}),
        content_type="application/json",
    )
    assert response.status_code == StatusCode.BAD_REQUEST

    response = test_client.post(
        f"/api/user/reset-pw?",
        data=json.dumps({"pw": valid_pw}),
        content_type="application/json",
    )
    assert response.status_code == StatusCode.BAD_REQUEST

    response = test_client.post(
        f"/api/user/reset-pw?key=",
        data=json.dumps({"pw": valid_pw}),
        content_type="application/json",
    )
    assert response.status_code == StatusCode.BAD_REQUEST

    response = test_client.post(
        f"/api/user/reset-pw?key=0001",
        data=json.dumps({"pw": valid_pw}),
        content_type="application/json",
    )
    assert response.status_code == StatusCode.BAD_REQUEST

    response = test_client.post(
        f"/api/user/reset-pw?key={data["key"] + '11'}",
        data=json.dumps({"pw": valid_pw}),
        content_type="application/json",
    )
    assert response.status_code == StatusCode.BAD_REQUEST

    response = test_client.post(
        f"/api/user/reset-pw?key={data["key"]}",
        content_type="application/json",
    )
    assert response.status_code == StatusCode.BAD_REQUEST

    response = test_client.post(
        f"/api/user/reset-pw?key={data["key"]}",
        data=json.dumps({"pw": None}),
        content_type="application/json",
    )
    assert response.status_code == StatusCode.BAD_REQUEST

    response = test_client.post(
        f"/api/user/reset-pw?key={data["key"]}",
        data=json.dumps({"pw": short_pw}),
        content_type="application/json",
    )
    assert response.status_code == StatusCode.BAD_REQUEST

    response = test_client.post(
        f"/api/user/reset-pw?key={data["key"]}",
        data=json.dumps({"pw": not_valid_pw_1}),
        content_type="application/json",
    )
    assert response.status_code == StatusCode.BAD_REQUEST

    response = test_client.post(
        f"/api/user/reset-pw?key={data["key"]}",
        data=json.dumps({"pw": valid_pw}),
        content_type="application/json",
    )
    assert response.status_code == StatusCode.OK


# email로 login_id 찾기
def test_find_login_id_by_email(test_client):

    response = test_client.get(f"/api/user/login-id")
    assert response.status_code == StatusCode.BAD_REQUEST

    response = test_client.get(f"/api/user/login-id?")
    assert response.status_code == StatusCode.BAD_REQUEST

    response = test_client.get(f"/api/user/login-id?email=")
    assert response.status_code == StatusCode.BAD_REQUEST

    response = test_client.get(f"/api/user/login-id?email={invalid_email}")
    assert response.status_code == StatusCode.BAD_REQUEST

    response = test_client.get(f"/api/user/login-id?email={valid_email}")
    assert response.status_code == StatusCode.BAD_REQUEST

    response = test_client.get(f"/api/user/login-id?email={duplicated_email}")
    data = json.loads(response.data.decode("utf-8"))
    assert response.status_code == StatusCode.OK
    assert data["login_id"] == "dum***"


# 유저 로그인 확인
def test_check_login_using_jwt(test_client):
    response = test_client.get(f"/api/user/login")
    assert response.status_code == StatusCode.UNAUTHORIZED


# 유저 회원가입
def test_register_user(test_client):
    # 항목 없음
    response = test_client.post(
        f"/api/user/profile",
        data=json.dumps(
            {
                "login_id": valid_login,
                "pw": valid_pw,
                "last_name": "last_name",
                "name": "이름",
            }
        ),
        content_type="application/json",
    )
    assert response.status_code == StatusCode.BAD_REQUEST

    response = test_client.post(
        f"/api/user/profile",
        data=json.dumps(
            {
                "email": valid_email,
                "pw": valid_pw,
                "last_name": "last_name",
                "name": "이름",
            }
        ),
        content_type="application/json",
    )
    assert response.status_code == StatusCode.BAD_REQUEST

    response = test_client.post(
        f"/api/user/profile",
        data=json.dumps(
            {
                "email": valid_email,
                "login_id": valid_login,
                "last_name": "last_name",
                "name": "이름",
            }
        ),
        content_type="application/json",
    )
    assert response.status_code == StatusCode.BAD_REQUEST

    response = test_client.post(
        f"/api/user/profile",
        data=json.dumps(
            {
                "email": valid_email,
                "login_id": valid_login,
                "pw": valid_pw,
                "name": "이름",
            }
        ),
        content_type="application/json",
    )
    assert response.status_code == StatusCode.BAD_REQUEST

    response = test_client.post(
        f"/api/user/profile",
        data=json.dumps(
            {
                "email": valid_email,
                "login_id": valid_login,
                "pw": valid_pw,
                "last_name": "last_name",
            }
        ),
        content_type="application/json",
    )
    assert response.status_code == StatusCode.BAD_REQUEST

    # 값 없음
    response = test_client.post(
        f"/api/user/profile",
        data=json.dumps(
            {
                "email": "",
                "login_id": valid_login,
                "pw": valid_pw,
                "last_name": "last_name",
                "name": "이름",
            }
        ),
        content_type="application/json",
    )
    assert response.status_code == StatusCode.BAD_REQUEST

    response = test_client.post(
        f"/api/user/profile",
        data=json.dumps(
            {
                "email": None,
                "login_id": valid_login,
                "pw": valid_pw,
                "last_name": "last_name",
                "name": "이름",
            }
        ),
        content_type="application/json",
    )
    assert response.status_code == StatusCode.BAD_REQUEST

    response = test_client.post(
        f"/api/user/profile",
        data=json.dumps(
            {
                "email": valid_email,
                "login_id": "",
                "pw": valid_pw,
                "last_name": "last_name",
                "name": "이름",
            }
        ),
        content_type="application/json",
    )
    assert response.status_code == StatusCode.BAD_REQUEST

    response = test_client.post(
        f"/api/user/profile",
        data=json.dumps(
            {
                "email": valid_email,
                "login_id": None,
                "pw": valid_pw,
                "last_name": "last_name",
                "name": "이름",
            }
        ),
        content_type="application/json",
    )
    assert response.status_code == StatusCode.BAD_REQUEST

    response = test_client.post(
        f"/api/user/profile",
        data=json.dumps(
            {
                "email": valid_email,
                "login_id": valid_login,
                "pw": "",
                "last_name": "last_name",
                "name": "이름",
            }
        ),
        content_type="application/json",
    )
    assert response.status_code == StatusCode.BAD_REQUEST

    response = test_client.post(
        f"/api/user/profile",
        data=json.dumps(
            {
                "email": valid_email,
                "login_id": valid_login,
                "pw": None,
                "last_name": "last_name",
                "name": "이름",
            }
        ),
        content_type="application/json",
    )
    assert response.status_code == StatusCode.BAD_REQUEST

    response = test_client.post(
        f"/api/user/profile",
        data=json.dumps(
            {
                "email": valid_email,
                "login_id": valid_login,
                "pw": valid_pw,
                "last_name": "",
                "name": "이름",
            }
        ),
        content_type="application/json",
    )
    assert response.status_code == StatusCode.BAD_REQUEST

    response = test_client.post(
        f"/api/user/profile",
        data=json.dumps(
            {
                "email": valid_email,
                "login_id": valid_login,
                "pw": valid_pw,
                "last_name": None,
                "name": "이름",
            }
        ),
        content_type="application/json",
    )
    assert response.status_code == StatusCode.BAD_REQUEST

    response = test_client.post(
        f"/api/user/profile",
        data=json.dumps(
            {
                "email": valid_email,
                "login_id": valid_login,
                "pw": valid_pw,
                "last_name": "last_name",
                "name": "",
            }
        ),
        content_type="application/json",
    )
    assert response.status_code == StatusCode.BAD_REQUEST

    response = test_client.post(
        f"/api/user/profile",
        data=json.dumps(
            {
                "email": valid_email,
                "login_id": valid_login,
                "pw": valid_pw,
                "last_name": "last_name",
                "name": None,
            }
        ),
        content_type="application/json",
    )
    assert response.status_code == StatusCode.BAD_REQUEST

    # 잘못된 값
    user_data = {
        "email": invalid_email,
        "login_id": valid_login,
        "pw": valid_pw,
        "last_name": "last_name",
        "name": "이름",
    }

    response = test_client.post(
        f"/api/user/profile",
        data=json.dumps(user_data),
        content_type="application/json",
    )
    assert response.status_code == StatusCode.BAD_REQUEST

    user_data["email"] = duplicated_email
    response = test_client.post(
        f"/api/user/profile",
        data=json.dumps(user_data),
        content_type="application/json",
    )
    assert response.status_code == StatusCode.BAD_REQUEST

    user_data["email"] = valid_email
    user_data["login_id"] = invalid_login
    response = test_client.post(
        f"/api/user/profile",
        data=json.dumps(user_data),
        content_type="application/json",
    )
    assert response.status_code == StatusCode.BAD_REQUEST

    user_data["login_id"] = duplicated_login
    response = test_client.post(
        f"/api/user/profile",
        data=json.dumps(user_data),
        content_type="application/json",
    )
    assert response.status_code == StatusCode.BAD_REQUEST

    user_data["login_id"] = valid_login
    user_data["pw"] = short_pw
    response = test_client.post(
        f"/api/user/profile",
        data=json.dumps(user_data),
        content_type="application/json",
    )
    assert response.status_code == StatusCode.BAD_REQUEST

    user_data["pw"] = not_valid_pw_1
    response = test_client.post(
        f"/api/user/profile",
        data=json.dumps(user_data),
        content_type="application/json",
    )
    assert response.status_code == StatusCode.BAD_REQUEST

    user_data["pw"] = not_valid_pw_2
    response = test_client.post(
        f"/api/user/profile",
        data=json.dumps(user_data),
        content_type="application/json",
    )
    assert response.status_code == StatusCode.BAD_REQUEST

    user_data["pw"] = not_valid_pw_3
    response = test_client.post(
        f"/api/user/profile",
        data=json.dumps(user_data),
        content_type="application/json",
    )
    assert response.status_code == StatusCode.BAD_REQUEST

    user_data["pw"] = not_valid_pw_4
    response = test_client.post(
        f"/api/user/profile",
        data=json.dumps(user_data),
        content_type="application/json",
    )
    assert response.status_code == StatusCode.BAD_REQUEST

    user_data["pw"] = not_valid_pw_5
    response = test_client.post(
        f"/api/user/profile",
        data=json.dumps(user_data),
        content_type="application/json",
    )
    assert response.status_code == StatusCode.BAD_REQUEST

    user_data["pw"] = not_valid_pw_6
    response = test_client.post(
        f"/api/user/profile",
        data=json.dumps(user_data),
        content_type="application/json",
    )
    assert response.status_code == StatusCode.BAD_REQUEST

    user_data["pw"] = not_valid_pw_7
    response = test_client.post(
        f"/api/user/profile",
        data=json.dumps(user_data),
        content_type="application/json",
    )
    assert response.status_code == StatusCode.BAD_REQUEST

    user_data["pw"] = valid_pw
    user_data["last_name"] = ""
    user_data["name"] = ""
    response = test_client.post(
        f"/api/user/profile",
        data=json.dumps(user_data),
        content_type="application/json",
    )
    assert response.status_code == StatusCode.BAD_REQUEST

    user_data["last_name"] = "성"
    user_data["name"] = "이름"
    response = test_client.post(
        f"/api/user/profile",
        data=json.dumps(user_data),
        content_type="application/json",
    )
    data = json.loads(response.data.decode("utf-8"))
    assert response.status_code == StatusCode.OK
    assert data["key"]


# 회원가입 후 이메일 인증 전
def test_unauthrized_email(test_client):
    user_data = {
        "email": valid_email,
        "login_id": valid_login,
        "pw": valid_pw,
        "last_name": "last_name",
        "name": "이름",
    }

    # 회원가입
    response = test_client.post(
        f"/api/user/profile",
        data=json.dumps(user_data),
        content_type="application/json",
    )
    assert response.status_code == StatusCode.OK

    # 패스워드 재설정 메일 요청
    response = test_client.get(f"/api/user/reset-pw?login_id={valid_login}")
    assert response.status_code == StatusCode.FORBIDDEN

    # 이메일로 로그인 아이디 찾기
    response = test_client.get(f"/api/user/login-id?email={valid_email}")
    data = json.loads(response.data.decode("utf-8"))
    assert response.status_code == StatusCode.OK
    assert data["login_id"] == "dummy1***"

    # 로그인
    response = test_client.post(
        f"/api/user/login",
        data=json.dumps({"login_id": valid_login, "pw": valid_pw}),
        content_type="application/json",
    )
    data = json.loads(response.data.decode("utf-8"))
    assert response.status_code == StatusCode.OK
    assert data["name"] == "이름"
    assert data["last_name"] == "last_name"
    assert data["email_check"] == False
    assert data["profile_check"] == False
    assert data["emoji_check"] == False
    assert data["oauth"] == 0

    # (로그인 후) 로그인 확인
    response = test_client.get(f"/api/user/login")
    data = json.loads(response.data.decode("utf-8"))
    assert response.status_code == StatusCode.OK
    assert data["email_check"] == False
    assert data["profile_check"] == False
    assert data["emoji_check"] == False

    # 메일 주소 가져오기
    response = test_client.get(f"/api/user/email")
    data = json.loads(response.data.decode("utf-8"))
    assert response.status_code == StatusCode.OK
    assert data["email"] == valid_email

    # 메일 주소 바꾸기
    response = test_client.patch(
        f"/api/user/email",
        data=json.dumps({"email": valid_email}),
        content_type="application/json",
    )
    data = json.loads(response.data.decode("utf-8"))
    assert response.status_code == StatusCode.BAD_REQUEST

    response = test_client.patch(
        f"/api/user/email",
        data=json.dumps({"email": duplicated_email}),
        content_type="application/json",
    )
    assert response.status_code == StatusCode.BAD_REQUEST

    response = test_client.patch(
        f"/api/user/email",
        data=json.dumps({"email": invalid_email}),
        content_type="application/json",
    )
    assert response.status_code == StatusCode.BAD_REQUEST

    response = test_client.patch(
        f"/api/user/email",
        data=json.dumps({"email": valid_email_2}),
        content_type="application/json",
    )
    data = json.loads(response.data.decode("utf-8"))
    assert response.status_code == StatusCode.OK
    assert data["email_check"] == False
    assert data["key"]
    key = data["key"]

    # 이메일 인증 키 다시 보내기
    response = test_client.get(f"/api/user/send-email")
    data = json.loads(response.data.decode("utf-8"))
    assert response.status_code == StatusCode.OK
    assert data["key"] == key

    # 이메일 인증
    response = test_client.get(f"/api/user/verify-email?key={key + '00'}")
    assert response.status_code == StatusCode.BAD_REQUEST

    response = test_client.get(f"/api/user/verify-email?key={key}")
    assert response.status_code == StatusCode.OK

    # 프로필 설정 확인 (email_check)
    response = test_client.get(f"/api/user/login")
    data = json.loads(response.data.decode("utf-8"))
    assert response.status_code == StatusCode.OK
    assert data["email_check"] == True
    assert data["profile_check"] == False
    assert data["emoji_check"] == False

    # 프로필 설정 (실패값)
    response = test_client.patch(
        "/api/user/profile",
        content_type="application/json",
    )
    data = json.loads(response.data.decode("utf-8"))
    assert response.status_code == StatusCode.BAD_REQUEST

    response = test_client.patch(
        "/api/user/profile",
        data=json.dumps({"age": "temp"}),
        content_type="application/json",
    )
    data = json.loads(response.data.decode("utf-8"))
    assert response.status_code == StatusCode.BAD_REQUEST

    response = test_client.patch(
        "/api/user/profile",
        data=json.dumps({"gender": 7}),
        content_type="application/json",
    )
    data = json.loads(response.data.decode("utf-8"))
    assert response.status_code == StatusCode.BAD_REQUEST

    response = test_client.patch(
        "/api/user/profile",
        data=json.dumps({"taste": 1}),
        content_type="application/json",
    )
    data = json.loads(response.data.decode("utf-8"))
    assert response.status_code == StatusCode.BAD_REQUEST

    response = test_client.patch(
        "/api/user/profile",
        data=json.dumps({"name": "", "last_name": "", "tags": [], "emoji": []}),
        content_type="application/json",
    )
    data = json.loads(response.data.decode("utf-8"))
    assert response.status_code == StatusCode.BAD_REQUEST

    response = test_client.patch(
        "/api/user/profile",
        data=json.dumps({"similar": "True"}),
        content_type="application/json",
    )
    data = json.loads(response.data.decode("utf-8"))
    assert response.status_code == StatusCode.BAD_REQUEST

    # 프로필 설정 (age, gender, taste)
    response = test_client.patch(
        "/api/user/profile",
        data=json.dumps(
            {
                "age": 20,
                "gender": 2,
                "taste": 7,
            }
        ),
        content_type="application/json",
    )
    data = json.loads(response.data.decode("utf-8"))
    assert response.status_code == StatusCode.OK
    assert data["email_check"] == True

    # 프로필 설정 확인 (profile_check)
    response = test_client.get(f"/api/user/login")
    data = json.loads(response.data.decode("utf-8"))
    assert response.status_code == StatusCode.OK
    assert data["email_check"] == True
    assert data["profile_check"] == True
    assert data["emoji_check"] == False

    # 프로필 설정 (Tags, hate_tags)
    response = test_client.patch(
        "/api/user/profile",
        data=json.dumps(
            {
                "tags": [1, 2, 3],
                "hate_tags": [7, 8, 9],
            }
        ),
        content_type="application/json",
    )
    data = json.loads(response.data.decode("utf-8"))
    assert response.status_code == StatusCode.OK
    assert data["email_check"] == True

    # 프로필 설정 (emoji, hate_emoji)
    response = test_client.patch(
        "/api/user/profile",
        data=json.dumps(
            {
                "emoji": [1, 2, 14],
                "hate_emoji": [15],
                "similar": False,
            }
        ),
        content_type="application/json",
    )
    data = json.loads(response.data.decode("utf-8"))
    print(data)
    assert response.status_code == StatusCode.OK
    assert data["email_check"] == True

    # 프로필 설정 확인 (emoji_check)
    response = test_client.get(f"/api/user/login")
    data = json.loads(response.data.decode("utf-8"))
    assert response.status_code == StatusCode.OK
    assert data["email_check"] == True
    assert data["profile_check"] == True
    assert data["emoji_check"] == True

    # 프로필 설정 (pw)
    response = test_client.patch(
        "/api/user/profile",
        data=json.dumps(
            {
                "pw": short_pw,
            }
        ),
        content_type="application/json",
    )
    assert response.status_code == StatusCode.BAD_REQUEST

    response = test_client.patch(
        "/api/user/profile",
        data=json.dumps(
            {
                "pw": not_valid_pw_1,
            }
        ),
        content_type="application/json",
    )
    assert response.status_code == StatusCode.BAD_REQUEST

    response = test_client.patch(
        "/api/user/profile",
        data=json.dumps(
            {
                "pw": valid_pw,
            }
        ),
        content_type="application/json",
    )
    data = json.loads(response.data.decode("utf-8"))
    assert response.status_code == StatusCode.OK
    assert data["email_check"] == True
    assert data["profile_check"] == True
    assert data["emoji_check"] == True

    # 로그아웃
    response = test_client.post(f"/api/user/logout")
    assert response.status_code == StatusCode.OK


# (이메일 인증 후) 이메일 변경
def test_change_email(test_client):
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
    assert data["name"] == "dummy1"
    assert data["last_name"] == "1"
    assert data["age"] == 20
    assert data["email_check"] == True
    assert data["profile_check"] == True
    assert data["emoji_check"] == True
    assert data["oauth"] == 0

    # 이메일 변경
    response = test_client.patch(
        "/api/user/profile",
        data=json.dumps(
            {
                "email": valid_email_2,
                "gender": 1,
                "taste": 2,
                "emoji": [1, 2, 3],
                "last_name": "dumdum",
                "age": 40,
            }
        ),
        content_type="application/json",
    )
    data = json.loads(response.data.decode("utf-8"))
    assert response.status_code == StatusCode.OK
    assert data["email_check"] == False

    # 이메일 변경 시 로그아웃 확인
    response = test_client.get(f"/api/user/login")
    data = json.loads(response.data.decode("utf-8"))
    assert response.status_code == StatusCode.UNAUTHORIZED

    # 재로그인, email_check 및 변경 사항 확인
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
    assert data["name"] == "dummy1"
    assert data["last_name"] == "dumdum"
    assert data["age"] == 40
    assert data["email_check"] == False
    assert data["profile_check"] == True
    assert data["emoji_check"] == True
    assert data["oauth"] == 0

    # 로그아웃
    response = test_client.post(f"/api/user/logout")
    assert response.status_code == StatusCode.OK


# 유저 테스트 (이메일 인증 후) _ 초기 프로필 설정, 이메일 인증으로 막힌 API 확인
def test_after_authorize_email(test_client):
    # 로그인 시도 (실패)
    response = test_client.post(
        f"/api/user/login",
        data=json.dumps(
            {
                "login_id": not_registered_login,
                "pw": valid_pw,
            }
        ),
        content_type="application/json",
    )
    assert response.status_code == StatusCode.BAD_REQUEST

    response = test_client.post(
        f"/api/user/login",
        data=json.dumps(
            {
                "login_id": duplicated_login,
                "pw": short_pw,
            }
        ),
        content_type="application/json",
    )
    assert response.status_code == StatusCode.BAD_REQUEST

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
    assert data["name"] == "dummy1"
    assert data["last_name"] == "1"
    assert data["age"] == 20
    assert data["email_check"] == True
    assert data["profile_check"] == True
    assert data["emoji_check"] == True
    assert data["oauth"] == 0

    # (로그인 후) 로그인 확인
    response = test_client.get(f"/api/user/login")
    data = json.loads(response.data.decode("utf-8"))
    assert response.status_code == StatusCode.OK
    assert data["email_check"] == True
    assert data["profile_check"] == True
    assert data["emoji_check"] == True

    # 메일 주소 가져오기
    response = test_client.get(f"/api/user/email")
    data = json.loads(response.data.decode("utf-8"))
    assert response.status_code == StatusCode.FORBIDDEN

    # 메일 주소 바꾸기
    response = test_client.patch(
        f"/api/user/email",
        data=json.dumps({"email": valid_email_2}),
        content_type="application/json",
    )
    data = json.loads(response.data.decode("utf-8"))
    assert response.status_code == StatusCode.FORBIDDEN

    # 이메일 인증 키 다시 보내기
    response = test_client.get(f"/api/user/send-email")
    data = json.loads(response.data.decode("utf-8"))
    assert response.status_code == StatusCode.FORBIDDEN

    # (자기 자신) 프로필 확인
    response = test_client.get(f"/api/user/profile")
    data = json.loads(response.data.decode("utf-8"))
    assert response.status_code == StatusCode.OK
    assert data["login_id"] == "dummy1"
    assert data["name"] == "dummy1"
    assert data["last_name"] == "1"
    assert data["age"] == 20
    assert data["gender"] == 2
    assert data["taste"] == 7
    assert data["bio"] == "1"
    assert data["tags"] == [4, 11, 12]
    assert data["hate_tags"] == [13]
    assert data["emoji"] == [12, 13, 16]
    assert data["hate_emoji"] == [15]
    assert data["similar"] == True
    assert data["pictures"]

    # 프로필 설정 (Tags, hate_tags)
    response = test_client.patch(
        "/api/user/profile",
        data=json.dumps(
            {
                "tags": [1, 2, 3],
                "hate_tags": [7, 8, 9],
            }
        ),
        content_type="application/json",
    )
    data = json.loads(response.data.decode("utf-8"))
    assert response.status_code == StatusCode.OK
    assert data["email_check"] == True

    # 프로필 설정 (emoji, hate_emoji)
    response = test_client.patch(
        "/api/user/profile",
        data=json.dumps(
            {
                "emoji": [1, 2, 14],
                "hate_emoji": [15],
                "similar": False,
            }
        ),
        content_type="application/json",
    )
    data = json.loads(response.data.decode("utf-8"))
    assert response.status_code == StatusCode.OK
    assert data["email_check"] == True

    # 프로필 설정 확인 (emoji_check)
    response = test_client.get(f"/api/user/login")
    data = json.loads(response.data.decode("utf-8"))
    assert response.status_code == StatusCode.OK
    assert data["email_check"] == True
    assert data["profile_check"] == True
    assert data["emoji_check"] == True

    # 로그아웃
    response = test_client.post(f"/api/user/logout")
    assert response.status_code == StatusCode.OK


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
    target = data["profile_list"][0]
    assert len(data["profile_list"]) == 1
    assert target["name"] == "dummy2"
    assert target["last_name"] == "2"
    assert target["distance"]
    assert target["fancy"] == 0
    assert target["age"] == 18
    assert target["picture"]
    assert target["time"] is None

    # 프로필 세부사항 확인 (성공)
    target_id = target["id"]
    response = test_client.get(f"/api/user/profile-detail?id={target_id}")
    data = json.loads(response.data.decode("utf-8"))
    assert response.status_code == StatusCode.OK
    assert data["login_id"] == "dummy2"
    assert data["status"] == 0
    assert data["last_online"]
    assert data["fame"] == 0
    assert data["gender"] == 4
    assert data["taste"] == 2
    assert data["bio"] == "2"
    assert data["tags"] == [4, 11, 12]
    assert data["hate_tags"] == [13]
    assert data["emoji"] == [16]
    assert data["hate_emoji"] == []
    assert data["similar"] == True
    assert data["pictures"]

    # 프로필 세부사항 확인 (실패)
    response = test_client.get(f"/api/user/profile-detail?id={"asdf"}")
    assert response.status_code == StatusCode.BAD_REQUEST

    response = test_client.get(f"/api/user/profile-detail?id={target_id + 100}")
    assert response.status_code == StatusCode.BAD_REQUEST

    # 유저 리포트 (실패)
    response = test_client.post(
        f"/api/user/report",
        data=json.dumps(
            {"target_id": target_id-1, "reason": 1}
        ),
        content_type="application/json",
    )
    assert response.status_code == StatusCode.BAD_REQUEST

    response = test_client.post(
        f"/api/user/report",
        data=json.dumps(
            {"target_id": target_id + 100, "reason": 1}
        ),
        content_type="application/json",
    )
    assert response.status_code == StatusCode.BAD_REQUEST

    response = test_client.post(
        f"/api/user/report",
        data=json.dumps(
            {"target_id": "asdf", "reason": 1}
        ),
        content_type="application/json",
    )
    assert response.status_code == StatusCode.BAD_REQUEST

    response = test_client.post(
        f"/api/user/report",
        data=json.dumps(
            {"target_id": target_id, "reason": 10}
        ),
        content_type="application/json",
    )
    assert response.status_code == StatusCode.BAD_REQUEST

    response = test_client.post(
        f"/api/user/report",
        data=json.dumps(
            {"target_id": target_id, "reason": 9}
        ),
        content_type="application/json",
    )
    assert response.status_code == StatusCode.BAD_REQUEST

    # 신고 (성공)
    response = test_client.post(
        f"/api/user/report",
        data=json.dumps(
            {"target_id": target_id, "reason": 1}
        ),
        content_type="application/json",
    )
    assert response.status_code == StatusCode.OK

    # 같은 유저 또 신고
    response = test_client.post(
        f"/api/user/report",
        data=json.dumps(
            {"target_id": target_id, "reason": 1}
        ),
        content_type="application/json",
    )
    assert response.status_code == StatusCode.BAD_REQUEST

    # 블록 전 유저 검색
    response = test_client.post(
        f"/api/user/search",
        data=json.dumps(
            {
                "min_age": 10,
                "max_age": 40,
                "distance": 100,
                "fame": 0,
                "tags": [],
            }
        ),
        content_type="application/json",
    )
    data = json.loads(response.data.decode("utf-8"))
    assert response.status_code == StatusCode.OK
    assert len(data["profile_list"]) == 3

    # 유저 블록 (실패)
    response = test_client.post(
        f"/api/user/block",
        data=json.dumps(
            {"target_id": target_id-1}
        ),
        content_type="application/json",
    )
    assert response.status_code == StatusCode.BAD_REQUEST

    response = test_client.post(
        f"/api/user/block",
        data=json.dumps(
            {"target_id": target_id + 100}
        ),
        content_type="application/json",
    )
    assert response.status_code == StatusCode.BAD_REQUEST

    response = test_client.post(
        f"/api/user/block",
        data=json.dumps(
            {"target_id": "asdf"}
        ),
        content_type="application/json",
    )
    assert response.status_code == StatusCode.BAD_REQUEST

    # report한 유저 또 block
    response = test_client.post(
        f"/api/user/block",
        data=json.dumps(
            {"target_id": target_id}
        ),
        content_type="application/json",
    )
    assert response.status_code == StatusCode.BAD_REQUEST

    # 블록 (성공)
    response = test_client.post(
        f"/api/user/block",
        data=json.dumps(
            {"target_id": target_id + 1}
        ),
        content_type="application/json",
    )
    assert response.status_code == StatusCode.OK

    # 같은 유저 또 block
    response = test_client.post(
        f"/api/user/block",
        data=json.dumps(
            {"target_id": target_id + 1}
        ),
        content_type="application/json",
    )
    assert response.status_code == StatusCode.BAD_REQUEST

    # 블록 후 유저 검색 시 나오지 않음
    response = test_client.post(
        f"/api/user/search",
        data=json.dumps(
            {
                "min_age": 10,
                "max_age": 40,
                "distance": 100,
                "fame": 0,
                "tags": [],
            }
        ),
        content_type="application/json",
    )
    data = json.loads(response.data.decode("utf-8"))
    assert response.status_code == StatusCode.OK
    assert len(data["profile_list"]) == 2

    # 신고 (실패)
    response = test_client.post(
        f"/api/user/report",
        data=json.dumps(
            {"target_id": target_id+2, "reason": 9, "reason_opt": "밍"}
        ),
        content_type="application/json",
    )
    assert response.status_code == StatusCode.BAD_REQUEST

    # 신고 (성공)
    response = test_client.post(
        f"/api/user/report",
        data=json.dumps(
            {"target_id": target_id+2, "reason": 9, "reason_opt": "그냥 싫어요"}
        ),
        content_type="application/json",
    )
    assert response.status_code == StatusCode.OK

    # 로그아웃
    response = test_client.post(f"/api/user/logout")
    assert response.status_code == StatusCode.OK


# 유저 티 추천
def test_tea_suggest_api(test_client):
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

    # tea 추천
    response = test_client.get(f"/api/user/tea")
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
        data=json.dumps({"target_id": target["id"], "reason": 1}),
        content_type="application/json",
    )
    data = json.loads(response.data.decode("utf-8"))
    assert response.status_code == StatusCode.OK

    # (신고, 블록 후) tea 추천
    response = test_client.get(f"/api/user/tea")
    data = json.loads(response.data.decode("utf-8"))
    assert response.status_code == StatusCode.OK
    assert len(data["profile_list"]) == 2
    assert data["profile_list"][0]["name"] == "dummy4"
    assert data["profile_list"][1]["name"] == "dummy3"

    # 로그아웃
    response = test_client.post(f"/api/user/logout")
    assert response.status_code == StatusCode.OK


# 로그아웃
def test_logout(test_client):

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
    assert response.status_code == StatusCode.OK

    # (로그인 후) 로그인 확인
    response = test_client.get(f"/api/user/login")
    data = json.loads(response.data.decode("utf-8"))
    assert response.status_code == StatusCode.OK
    assert data["email_check"] == True
    assert data["profile_check"] == True
    assert data["emoji_check"] == True

    # refresh token 재발급
    response = test_client.patch(f"/api/user/reset-token")
    assert response.status_code == StatusCode.OK

    # (로그인 후) 로그인 확인
    response = test_client.get(f"/api/user/login")
    data = json.loads(response.data.decode("utf-8"))
    assert response.status_code == StatusCode.OK
    assert data["email_check"] == True
    assert data["profile_check"] == True
    assert data["emoji_check"] == True

    # 로그아웃
    response = test_client.post(f"/api/user/logout")
    assert response.status_code == StatusCode.OK

    # (로그인 후) 로그인 확인
    response = test_client.get(f"/api/user/login")
    assert response.status_code == StatusCode.UNAUTHORIZED

    # refresh token 재발급
    response = test_client.patch(f"/api/user/reset-token")
    assert response.status_code == StatusCode.UNAUTHORIZED


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
        # print(e)
        # 롤백 및 예외 처리
        conn.rollback()
        # raise e

    finally:
        # 커서와 연결 닫기
        cursor.close()
        PostgreSQLFactory.close_connection()
