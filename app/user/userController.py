from flask import request
from flask_restx import Namespace, Resource, fields
from . import userService as serv

# from ..wrapper.location import check_location
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.exceptions import BadRequest, InternalServerError

ns = Namespace(name="user", description="유저 정보 관련 API", path="/api/user")


class _RequestSchema:
    field_post_login = ns.model(
        "로그인 시 필요 데이터",
        {
            "login_id": fields.String(required=True, description="유저 아이디"),
            "pw": fields.String(required=True, description="유저 비밀번호"),
        },
    )

    field_post_profile = ns.model(
        "회원가입 필요 데이터",
        {
            "email": fields.String(required=True, description="이메일"),
            "login_id": fields.String(required=True, description="아이디"),
            "pw": fields.String(required=True, description="패스워드"),
            "last_name": fields.String(required=True, description="성"),
            "name": fields.String(required=True, description="이름"),
        },
    )

    field_patch_email = ns.model(
        "(인증 전) 이메일 변경 시 필요 데이터",
        {
            "email": fields.String(required=True, description="이메일"),
        },
    )

    field_post_search = ns.model(
        "search 필요 데이터",
        {
            "min_age": fields.Integer(description="최소 나이"),
            "max_age": fields.Integer(description="최대 나이"),
            "distance": fields.Float(description="거리"),
            "tags": fields.List(fields.Integer, description="찾고싶은 태그"),
            "fame": fields.Float(description="fame 지수 최소치"),
        },
    )

    field_patch_setting = ns.model(
        "setting 필요 데이터",
        {
            "email": fields.String(description="이메일"),
            "pw": fields.String(description="패스워드"),
            "last_name": fields.String(description="성"),
            "name": fields.String(description="이름"),
            "age": fields.Integer(description="유저 나이"),
            "gender": fields.Integer(description="유저 성별"),
            "taste": fields.Integer(description="유저 성적 취향"),
            "bio": fields.String(description="자기소개"),
            "tags": fields.List(fields.Integer, description="취미 태그"),
            "hate_tags": fields.List(fields.Integer, description="싫어하는 취미 태그"),
            "emoji": fields.List(fields.Integer, description="유저 취향 이모지"),
            "hate_emoji": fields.List(fields.Integer, description="싫어하는 이모지"),
            "similar": fields.Boolean(description="비슷한 사람 좋아요"),
        },
    )

    field_post_report = ns.model(
        "report 필요 데이터",
        {
            "target_id": fields.Integer(required=True, description="신고 대상 유저"),
            "reason": fields.Integer(required=True, description="신고 이유"),
            "reason_opt": fields.String(description="신고 이유 디테일"),
        },
    )

    field_post_block = ns.model(
        "block 필요 데이터",
        {
            "target_id": fields.Integer(required=True, description="블록 대상 유저"),
        },
    )

    field_post_resetPw = ns.model(
        "resetPw 필요 데이터",
        {"pw": fields.String(required=True, description="변경할 비밀번호")},
    )


class _ResponseSchema:
    field_get_login = ns.model(
        "로그인 여부 응답 데이터",
        {
            "email_check": fields.Boolean(description="이메일 인증 여부"),
            "profile_check": fields.Boolean(description="(최초 1회) 프로필 설정 여부"),
            "emoji_check": fields.Boolean(description="(최초 1회) 이모지 설정 여부"),
        },
    )

    field_post_login = ns.model(
        "로그인 응답 데이터",
        {
            "id": fields.Integer(description="유저 id"),
            "name": fields.String(description="유저 이름"),
            "last_name": fields.String(description="유저 성"),
            "age": fields.Integer(description="유저 나이"),
            "email_check": fields.Boolean(description="이메일 인증 여부"),
            "profile_check": fields.Boolean(description="(최초 1회) 프로필 설정 여부"),
            "emoji_check": fields.Boolean(description="(최초 1회) 이모지 설정 여부"),
            "oauth": fields.Integer(description="oauth 여부"),
        },
    )

    field_get_checkEmail = ns.model(
        "이메일 중복 확인 응답 데이터",
        {
            "occupied": fields.Boolean(description="이메일 사용 여부"),
        },
    )

    field_get_checkId = ns.model(
        "Login Id 중복 확인 응답 데이터",
        {
            "occupied": fields.Boolean(description="login id 사용 여부"),
        },
    )

    field_get_emailStatus = ns.model(
        "이메일 인증 여부 확인 응답 데이터",
        {
            "email_check": fields.Boolean(description="이메일 인증 여부"),
            "profile_check": fields.Boolean(description="(최초 1회) 프로필 설정 여부"),
            "emoji_check": fields.Boolean(description="(최초 1회) 이모지 설정 여부"),
        },
    )

    field_get_email = ns.model(
        "유저 이메일 주소 확인 응답 데이터",
        {
            "email": fields.String(description="유저 이메일 주소"),
        },
    )

    field_patch_email = ns.model(
        "(인증 전) 이메일 변경 요청 응답 데이터",
        {
            "email_check": fields.Boolean(description="이메일 인증 여부"),
            "profile_check": fields.Boolean(description="(최초 1회) 프로필 설정 여부"),
            "emoji_check": fields.Boolean(description="(최초 1회) 이모지 설정 여부"),
        },
    )

    field_get_sendEmail = ns.model(
        "(인증 전) 인증메일 다시 보내기 요청 응답 데이터",
        {
            "email_check": fields.Boolean(description="이메일 인증 여부"),
            "profile_check": fields.Boolean(description="(최초 1회) 프로필 설정 여부"),
            "emoji_check": fields.Boolean(description="(최초 1회) 이모지 설정 여부"),
        },
    )

    field_patch_setting = ns.model(
        "setting 응답 데이터",
        {
            "email_check": fields.Boolean(description="이메일 인증 여부"),
        },
    )

    field_get_user_profile = ns.model(
        "자신의 profile 기존 설정 확인 응답 데이터",
        {
            "login_id": fields.String(description="유저 로그인 id"),
            "name": fields.String(description="유저 이름"),
            "last_name": fields.String(description="유저 성"),
            "email": fields.String(description="유저 이메일 주소"),
            "age": fields.Integer(description="유저 나이"),
            "gender": fields.Integer(description="유저 성별"),
            "taste": fields.Integer(description="유저 취향"),
            "bio": fields.String(description="유저 자기소개"),
            "tags": fields.List(fields.Integer, description="설정한 관심사 태그"),
            "hate_tags": fields.List(
                fields.Integer, description="설정한 싫어하는 관심사 태그"
            ),
            "emoji": fields.List(fields.Integer, description="설정한 이모티콘 태그"),
            "hate_emoji": fields.List(
                fields.Integer, description="설정한 싫어하는 이모티콘 태그"
            ),
            "similar": fields.Boolean(description="비슷한 사람과 만나고 싶어요"),
            "pictures": fields.List(
                fields.String, description="유저 프로필 사진 데이터"
            ),
        },
    )

    field_get_target_profile = ns.model(
        "target의 profile 응답 데이터",
        {
            "id": fields.Integer(description="유저 id"),
            "name": fields.String(description="유저 이름"),
            "last_name": fields.String(description="유저 성"),
            "distance": fields.Float(description="거리"),
            "fancy": fields.Integer(description="유저와의 fancy 관계"),
            "age": fields.Integer(description="유저 나이"),
            "tags": fields.List(fields.Integer, description="설정한 관심사 태그"),
            "fame": fields.Integer(description="유저 fame 지수"),
            "picture": fields.String(description="유저 프로필 사진 데이터"),
            "time": fields.String(description="무한로딩용 기준점"),
        },
    )

    field_post_search = ns.model(
        "search 응답 데이터",
        {
            "profile_list": fields.List(
                fields.Nested(field_get_target_profile), description="profile JSON list"
            ),
        },
    )

    field_get_tea = ns.model(
        "tea 추천 응답 데이터",
        {
            "profile_list": fields.List(
                fields.Nested(field_get_target_profile), description="profile JSON list"
            ),
        },
    )

    field_get_profileDetail = ns.model(
        "profileDetail 확인 응답 데이터",
        {
            "login_id": fields.String(description="로그인 아이디"),
            "status": fields.Integer(description="접속 상태"),
            "last_online": fields.DateTime(description="마지막 접속 일시"),
            "fame": fields.Float(description="fame 지수"),
            "gender": fields.Integer(description="유저 성별"),
            "taste": fields.Integer(description="유저 성적 취향"),
            "bio": fields.String(description="자기소개"),
            "tags": fields.List(fields.Integer, description="설정한 관심사 태그"),
            "hate_tags": fields.List(
                fields.Integer, description="설정한 싫어하는 관심사 태그"
            ),
            "emoji": fields.List(fields.Integer, description="설정한 이모티콘 태그"),
            "hate_emoji": fields.List(
                fields.Integer, description="설정한 싫어하는 이모티콘 태그"
            ),
            "similar": fields.Boolean(description="비슷한 사람과 만나고 싶어요"),
            "pictures": fields.List(fields.String, description="프로필 사진 데이터"),
        },
    )

    field_failed = ns.model(
        "API 요청 실패",
        {
            "message": fields.String(description="실패 이유"),
            "error": fields.Integer(description="(401 시) 만료 토큰 Enum"),
        },
    )


##### login
@ns.route("/login")
class Login(Resource):

    @jwt_required()
    @ns.response(200, "api요청 성공", _ResponseSchema.field_get_login)
    @ns.response(400, "Bad Request: 잘못된 요청", _ResponseSchema.field_failed)
    @ns.response(
        401, "Unauthorized: JWT, CSRF token 없음", _ResponseSchema.field_failed
    )
    @ns.response(403, "Forbidden: (token 외) 권한 없음", _ResponseSchema.field_failed)
    def get(self):
        """login 확인"""
        id = get_jwt_identity()
        # [JWT] delete below
        # id = 1
        return serv.login_check(id)

    @ns.expect(_RequestSchema.field_post_login, validate=True)
    @ns.response(200, "api요청 성공", _ResponseSchema.field_post_login)
    @ns.response(400, "Bad Request", _ResponseSchema.field_failed)
    @ns.response(403, "Forbidden(권한없음)", _ResponseSchema.field_failed)
    @ns.header("content-type", "application/json")
    def post(self):
        """login"""
        return serv.login(request.json)


@ns.route("/check-id")
class CheckId(Resource):
    @ns.response(200, "api요청 성공", _ResponseSchema.field_get_checkId)
    @ns.response(400, "Bad Request", _ResponseSchema.field_failed)
    @ns.response(403, "Forbidden(권한없음)", _ResponseSchema.field_failed)
    @ns.doc(params={"login_id": "중복 확인할 login id"})
    def get(self):
        """check ID duplication"""
        login_id = request.args.get("login_id")
        if not login_id:
            raise BadRequest("중복 검사할 id를 제공해야 합니다.")
        return serv.check_id(login_id)


# ##### email
@ns.route("/check-email")
class CheckEmail(Resource):
    @ns.response(200, "api요청 성공", _ResponseSchema.field_get_checkEmail)
    @ns.response(400, "Bad Request", _ResponseSchema.field_failed)
    @ns.response(403, "Forbidden(권한없음)", _ResponseSchema.field_failed)
    @ns.doc(params={"email": "중복 확인할 email"})
    def get(self):
        """email 중복 확인"""
        email = request.args.get("email")
        if not email:
            raise BadRequest("중복 검사할 이메일을 제공해야 합니다.")
        return serv.check_email(email)


@ns.route("/email")
class GetEmail(Resource):

    @jwt_required()
    @ns.response(200, "api요청 성공", _ResponseSchema.field_get_email)
    @ns.response(400, "Bad Request: 잘못된 요청", _ResponseSchema.field_failed)
    @ns.response(
        401, "Unauthorized: JWT, CSRF token 없음", _ResponseSchema.field_failed
    )
    @ns.response(403, "Forbidden: (token 외) 권한 없음", _ResponseSchema.field_failed)
    def get(self):
        """이메일 주소 확인"""
        id = get_jwt_identity()
        # [JWT] delete below
        # id = 1
        return serv.get_email(id)

    @jwt_required()
    @ns.expect(_RequestSchema.field_patch_email, validate=True)
    @ns.response(200, "api요청 성공", _ResponseSchema.field_patch_email)
    @ns.response(400, "Bad Request: 잘못된 요청", _ResponseSchema.field_failed)
    @ns.response(
        401, "Unauthorized: JWT, CSRF token 없음", _ResponseSchema.field_failed
    )
    @ns.response(403, "Forbidden: (token 외) 권한 없음", _ResponseSchema.field_failed)
    def patch(self):
        """(기존 메일 인증 전) 신규 이메일 등록"""
        id = get_jwt_identity()
        # [JWT] delete below
        # id = 1
        return serv.change_email(request.json, id)


@ns.route("/send-email")
class SendEmail(Resource):

    @jwt_required()
    @ns.response(200, "api요청 성공", _ResponseSchema.field_get_sendEmail)
    @ns.response(400, "Bad Request: 잘못된 요청", _ResponseSchema.field_failed)
    @ns.response(
        401, "Unauthorized: JWT, CSRF token 없음", _ResponseSchema.field_failed
    )
    @ns.response(403, "Forbidden: (token 외) 권한 없음", _ResponseSchema.field_failed)
    def get(self):
        """인증 메일 다시 보내기"""
        id = get_jwt_identity()
        # [JWT] delete below
        # id = 1
        return serv.resend_email(id)


@ns.route("/verify-email")
class VerifyEmail(Resource):
    @ns.response(400, "Bad Request", _ResponseSchema.field_failed)
    @ns.response(403, "Forbidden(권한없음)", _ResponseSchema.field_failed)
    @ns.doc(params={"key": "이메일 인증 링크 중 키"})
    def get(self):
        """이메일 인증 진행"""
        key = request.args.get("key")
        if not key:
            raise BadRequest("인증할 키를 제공해야 합니다.")
        return serv.verify_email(key)


@ns.route("/profile")
class Profile(Resource):
    @ns.expect(_RequestSchema.field_post_profile, validate=True)
    @ns.response(400, "Bad Request", _ResponseSchema.field_failed)
    @ns.response(403, "Forbidden(권한없음)", _ResponseSchema.field_failed)
    @ns.header("content-type", "application/json")
    def post(self):
        """회원 가입"""
        return serv.register(request.json)

    @jwt_required()
    @ns.expect(_RequestSchema.field_patch_setting, validate=True)
    @ns.response(200, "api요청 성공", _ResponseSchema.field_patch_setting)
    @ns.response(400, "Bad Request: 잘못된 요청", _ResponseSchema.field_failed)
    @ns.response(
        401, "Unauthorized: JWT, CSRF token 없음", _ResponseSchema.field_failed
    )
    @ns.response(403, "Forbidden: (token 외) 권한 없음", _ResponseSchema.field_failed)
    @ns.header("content-type", "application/json")
    def patch(self):
        """설정 업데이트"""
        id = get_jwt_identity()
        # [JWT] delete below
        # id = 1
        try:
            images = (
                serv.save_pictures(id, request.json["pictures"])
                if "pictures" in request.json
                and 0 < len(request.json["pictures"])
                and 1 < len(request.json["pictures"][0])
                else []
            )
        except ValueError:
            raise BadRequest("업로드 불가능한 사진입니다.")
        except Exception as e:
            raise InternalServerError("사진 저장 실패")

        return serv.setting(request.json, id, images)

    # 프로필 하나 요청하는 상황 == 자기 자신 정보 보기
    @jwt_required()
    @ns.response(200, "api요청 성공", _ResponseSchema.field_get_user_profile)
    @ns.response(400, "Bad Request: 잘못된 요청", _ResponseSchema.field_failed)
    @ns.response(
        401, "Unauthorized: JWT, CSRF token 없음", _ResponseSchema.field_failed
    )
    @ns.response(403, "Forbidden: (token 외) 권한 없음", _ResponseSchema.field_failed)
    def get(self):
        """프로필 확인"""
        id = get_jwt_identity()
        # [JWT] delete below
        # id = 1
        return serv.get_profile(id)


@ns.route("/profile-detail")
class ProfileDetail(Resource):

    @jwt_required()
    @ns.response(200, "api요청 성공", _ResponseSchema.field_get_profileDetail)
    @ns.response(400, "Bad Request: 잘못된 요청", _ResponseSchema.field_failed)
    @ns.response(
        401, "Unauthorized: JWT, CSRF token 없음", _ResponseSchema.field_failed
    )
    @ns.response(403, "Forbidden: (token 외) 권한 없음", _ResponseSchema.field_failed)
    @ns.doc(params={"id": "프로필 확인할 id"})
    def get(self):
        """상세 프로필 확인"""
        id = get_jwt_identity()
        # [JWT] delete below
        # id = 1
        target_id = request.args.get("id")
        if not target_id:
            raise BadRequest("프로필을 확인할 유저의 id를 제공해야 합니다.")

        try:
            target_id = int(target_id)
        except ValueError:
            raise BadRequest("id는 숫자로 제공되어야 합니다.")

        return serv.profile_detail(id, target_id)


@ns.route("/logout")
class Logout(Resource):

    @jwt_required()
    @ns.response(400, "Bad Request: 잘못된 요청", _ResponseSchema.field_failed)
    @ns.response(
        401, "Unauthorized: JWT, CSRF token 없음", _ResponseSchema.field_failed
    )
    @ns.response(403, "Forbidden: (token 외) 권한 없음", _ResponseSchema.field_failed)
    # @check_location()
    def post(self):
        """logout"""
        id = get_jwt_identity()
        # [JWT] delete below
        # id = 1
        return serv.logout(id)


@ns.route("/login-id")
class LoginId(Resource):
    @ns.response(400, "Bad Request", _ResponseSchema.field_failed)
    @ns.response(403, "Forbidden(권한없음)", _ResponseSchema.field_failed)
    @ns.doc(params={"email": "(로그인 id 확인할) 메일 주소"})
    def get(self):
        """유저 email로 ID 찾기"""
        email = request.args.get("email")
        if not email:
            raise BadRequest("확인할 이메일을 제공해야 합니다.")
        return serv.find_login_id(email)


@ns.route("/reset-pw")
class ResetPw(Resource):
    @ns.response(400, "Bad Request", _ResponseSchema.field_failed)
    @ns.response(403, "Forbidden(권한없음)", _ResponseSchema.field_failed)
    @ns.doc(params={"login_id": "(비밀번호 재설정 메일 요청) 로그인 아이디"})
    def get(self):
        """비밀번호 재설정 링크 요청 (이메일)"""
        login_id = request.args.get("login_id")
        if not login_id:
            raise BadRequest("로그인 id를 입력해주세요.")
        return serv.request_reset(login_id)

    @ns.response(400, "Bad Request", _ResponseSchema.field_failed)
    @ns.response(403, "Forbidden(권한없음)", _ResponseSchema.field_failed)
    @ns.doc(params={"key": "(비밀번호 재설정용) 확인 키"})
    @ns.header("content-type", "application/json")
    def post(self):
        """비밀번호 재 설정"""
        key = request.args.get("key")
        if not key:
            raise BadRequest("인증용 key를 입력해주세요.")
        return serv.reset_pw(request.json, key)


# soft delete 없을때까지는 사용 안하는걸로 하자
# @ns.route("/unregister")
# class Unregister(Resource):
#     @jwt_required()
#     @ns.response(400, "Bad Request: 잘못된 요청", _ResponseSchema.field_failed)
# @ns.response(
#     401, "Unauthorized: JWT, CSRF token 없음", _ResponseSchema.field_failed
# )
# @ns.response(403, "Forbidden: (token 외) 권한 없음", _ResponseSchema.field_failed)
#     def delete(self):
#         """회원 탈퇴"""
#         #id = get_jwt_identity()
# [JWT] delete below
#         # id = 1
#         return serv.unregister(id)


##### search
@ns.route("/search")
class Search(Resource):

    @jwt_required()
    @ns.expect(_RequestSchema.field_post_search, validate=True)
    @ns.response(200, "api요청 성공", _ResponseSchema.field_post_search)
    @ns.response(400, "Bad Request: 잘못된 요청", _ResponseSchema.field_failed)
    @ns.response(
        401, "Unauthorized: JWT, CSRF token 없음", _ResponseSchema.field_failed
    )
    @ns.response(403, "Forbidden: (token 외) 권한 없음", _ResponseSchema.field_failed)
    @ns.header("content-type", "application/json")
    def post(self):
        """유저 검색 기능"""
        id = get_jwt_identity()
        # [JWT] delete below
        # id = 1
        return serv.search(request.json, id)


##### tea suggest
@ns.route("/tea")
class Suggest(Resource):

    @jwt_required()
    @ns.response(200, "api요청 성공", _ResponseSchema.field_get_tea)
    @ns.response(400, "Bad Request: 잘못된 요청", _ResponseSchema.field_failed)
    @ns.response(
        401, "Unauthorized: JWT, CSRF token 없음", _ResponseSchema.field_failed
    )
    @ns.response(403, "Forbidden: (token 외) 권한 없음", _ResponseSchema.field_failed)
    def get(self):
        """get tea suggestions for you!"""
        id = get_jwt_identity()
        # [JWT] delete below
        # id = 1
        return serv.suggest(id)


# ##### report && block
@ns.route("/report")
class Report(Resource):

    @jwt_required()
    @ns.expect(_RequestSchema.field_post_report, validate=True)
    @ns.response(400, "Bad Request: 잘못된 요청", _ResponseSchema.field_failed)
    @ns.response(
        401, "Unauthorized: JWT, CSRF token 없음", _ResponseSchema.field_failed
    )
    @ns.response(403, "Forbidden: (token 외) 권한 없음", _ResponseSchema.field_failed)
    @ns.header("content-type", "application/json")
    def post(self):
        """리포트 하기"""
        id = get_jwt_identity()
        # [JWT] delete below
        # id = 1
        return serv.report(request.json, id)


@ns.route("/block")
class Block(Resource):

    @jwt_required()
    @ns.expect(_RequestSchema.field_post_block, validate=True)
    @ns.response(400, "Bad Request: 잘못된 요청", _ResponseSchema.field_failed)
    @ns.response(
        401, "Unauthorized: JWT, CSRF token 없음", _ResponseSchema.field_failed
    )
    @ns.response(403, "Forbidden: (token 외) 권한 없음", _ResponseSchema.field_failed)
    @ns.header("content-type", "application/json")
    def post(self):
        """블록하기"""
        id = get_jwt_identity()
        # [JWT] delete below
        # id = 1
        return serv.block(request.json, id)


@ns.route("/reset-token")
class resetToken(Resource):
    @jwt_required(refresh=True)
    @ns.response(401, "토큰 만료", _ResponseSchema.field_failed)
    # @check_location()
    def patch(self):
        """토큰 재발급"""
        id = get_jwt_identity()
        # [JWT] delete below
        # id = 1
        return serv.reset_token(id)
