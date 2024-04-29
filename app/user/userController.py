from flask import request
from flask_restx import Namespace, Resource, fields
from . import userService as serv
from ..wrapper.location import update_location
from ..wrapper.token import custom_jwt_required
from ..const import StatusCode

ns = Namespace(name="user", description="유저 정보 관련 API", path="/user")


class _RequestSchema:
    field_post_login = ns.model(
        "로그인 시 필요 데이터",
        {
            "login_id": fields.String(description="유저 아이디"),
            "pw": fields.String(description="유저 비밀번호"),
        },
    )

    field_post_profile = ns.model(
        "회원가입 필요 데이터",
        {
            "email": fields.String(description="이메일"),
            "login_id": fields.String(description="아이디"),
            "pw": fields.String(description="패스워드"),
            "last_name": fields.String(description="성"),
            "name": fields.String(description="이름"),
        },
    )

    field_patch_email = ns.model(
        "(인증 전) 이메일 변경 시 필요 데이터",
        {
            "email": fields.String(description="이메일"),
        },
    )

    field_patch_profile = ns.model(
        "(최초 1회) 프로필 설정 필요 데이터",
        {
            "age": fields.Integer(description="유저 나이"),
            "gender": fields.Integer(description="유저 성별"),
            "taste": fields.Integer(description="유저 성적 취향"),
            "bio": fields.String(description="자기소개"),
            "tags": fields.List(fields.Integer, description="취미 태그"),
            "hate_tags": fields.List(fields.Integer, description="싫어하는 취미 태그"),
            "pictures": fields.List(fields.String, description="프로필 이미지 파일"),
        },
    )

    field_patch_emoji = ns.model(
        "emoji 필요 데이터",
        {
            "prefer_emoji": fields.List(fields.Integer, description="유저 취향 이모지"),
            "hate_emoji": fields.List(fields.Integer, description="싫어하는 이모지"),
            "similar": fields.Boolean(description="비슷한 사람 좋아요"),
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
            "prefer_emoji": fields.List(fields.Integer, description="유저 취향 이모지"),
            "hate_emoji": fields.List(fields.Integer, description="싫어하는 이모지"),
            "similar": fields.Boolean(description="비슷한 사람 좋아요"),
        },
    )

    field_post_report = ns.model(
        "report 필요 데이터",
        {
            "target_id": fields.Integer(description="신고 대상 유저"),
            "reason": fields.Integer(description="신고 이유"),
            "reason_opt": fields.String(description="신고 이유 디테일"),
        },
    )

    field_post_block = ns.model(
        "block 필요 데이터",
        {
            "target_id": fields.Integer(description="블록 대상 유저"),
        },
    )

    field_post_resetPw = ns.model(
        "resetPw 필요 데이터", {"pw": fields.String(description="변경할 비밀번호")}
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
        "setting 필요 데이터",
        {
            "email_check": fields.Boolean(description="이메일 인증 여부"),
        },
    )

    field_get_profile = ns.model(
        "profile 확인 응답 데이터",
        {
            "id": fields.Integer(description="유저 id"),
            "name": fields.String(description="유저 이름"),
            "last_name": fields.String(description="유저 성"),
            "distance": fields.Float(description="거리"),
            "fancy": fields.Integer(description="유저와의 fancy 관계"),
            "age": fields.Integer(description="유저 나이"),
            "fame": fields.Float(description="fame 지수"),
            "tags": fields.List(fields.Integer, description="설정한 관심사 태그"),
            "gender": fields.Integer(description="유저 성별"),
            "picture": fields.List(
                fields.String, description="유저 프로필 사진 데이터"
            ),
        },
    )

    field_post_search = ns.model(
        "search 응답 데이터",
        {
            "profiles": fields.List(
                fields.Nested(field_get_profile), description="profile JSON list"
            ),
        },
    )

    field_get_profileDetail = ns.model(
        "profileDetail 확인 응답 데이터",
        {
            "login_id": fields.String(description="로그인 아이디"),
            "status": fields.Integer(description="접속 상태"),
            "last_online": fields.DateTime(description="마지막 접속 일시"),
            "taste": fields.Integer(description="유저 성적 취향"),
            "bio": fields.String(description="자기소개"),
        },
    )

    field_failed = ns.model(
        "API 요청 실패",
        {
            "message": fields.String(description="실패 이유"),
        },
    )


##### login
@ns.route("/login")
class Login(Resource):
    # @custom_jwt_required()
    @ns.response(200, "api요청 성공", _ResponseSchema.field_get_login)
    @ns.response(400, "Bad Request", _ResponseSchema.field_failed)
    @ns.response(403, "Forbidden(권한없음)", _ResponseSchema.field_failed)
    # @update_location()()
    def get(self, id=1):
        """login 확인"""
        # [JWT] delete below
        id = 1
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
            return {
                "message": "중복 검사할 id를 제공해야 합니다."
            }, StatusCode.BAD_REQUEST
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
            return {"message": "이메일을 제공해야 합니다."}, StatusCode.BAD_REQUEST
        return serv.check_email(email)


@ns.route("/email-status")
class EmailStatus(Resource):
    # @custom_jwt_required()
    @ns.response(200, "api요청 성공", _ResponseSchema.field_get_emailStatus)
    @ns.response(400, "Bad Request", _ResponseSchema.field_failed)
    @ns.response(403, "Forbidden(권한없음)", _ResponseSchema.field_failed)
    # @update_location()()
    def get(self, id=1):
        """이메일 인증 여부 확인"""
        # [JWT] delete below
        id = 1
        return serv.email_status(id)


@ns.route("/email")
class GetEmail(Resource):
    # @custom_jwt_required()
    @ns.response(200, "api요청 성공", _ResponseSchema.field_get_email)
    @ns.response(400, "Bad Request", _ResponseSchema.field_failed)
    @ns.response(403, "Forbidden(권한없음)", _ResponseSchema.field_failed)
    # @update_location()()
    def get(self, id=1):
        """이메일 주소 확인"""
        # [JWT] delete below
        id = 1
        return serv.get_email(id)

    # @custom_jwt_required()
    @ns.expect(_RequestSchema.field_patch_email, validate=True)
    @ns.response(200, "api요청 성공", _ResponseSchema.field_patch_email)
    @ns.response(400, "Bad Request", _ResponseSchema.field_failed)
    @ns.response(403, "Forbidden(권한없음)", _ResponseSchema.field_failed)
    # @update_location()()
    def patch(self, id=1):
        """(기존 메일 인증 전) 신규 이메일 등록"""
        # [JWT] delete below
        id = 1
        return serv.change_email(request.json, id)


@ns.route("/send-email")
class SendEmail(Resource):
    # @custom_jwt_required()
    @ns.response(200, "api요청 성공", _ResponseSchema.field_get_sendEmail)
    @ns.response(400, "Bad Request", _ResponseSchema.field_failed)
    @ns.response(403, "Forbidden(권한없음)", _ResponseSchema.field_failed)
    # @update_location()()
    def get(self, id=1):
        """인증 메일 다시 보내기"""
        # [JWT] delete below
        id = 1
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
            return {"message": "인증할 키를 제공해야 합니다."}, StatusCode.BAD_REQUEST
        return serv.verify_email(key)


# ##### register && setting
@ns.route("/setting")
class Setting(Resource):
    # @custom_jwt_required()
    @ns.expect(_RequestSchema.field_patch_setting)
    @ns.response(200, "api요청 성공", _ResponseSchema.field_patch_setting)
    @ns.response(400, "Bad Request", _ResponseSchema.field_failed)
    @ns.response(403, "Forbidden(권한없음)", _ResponseSchema.field_failed)
    @ns.header("content-type", "multipart/form-data")
    # @update_location()()
    def patch(self, id=1):
        """설정 업데이트"""
        # [JWT] delete below
        id = 1
        try:
            images = serv.save_pictures(request.files)
        except Exception as e:
            print(e)
            return {"message": "사진 저장 실패"}, StatusCode.INTERNAL_ERROR

        return serv.setting(request.json, id, images)


@ns.route("/profile")
class Profile(Resource):
    @ns.expect(_RequestSchema.field_post_profile, validate=True)
    @ns.response(400, "Bad Request", _ResponseSchema.field_failed)
    @ns.response(403, "Forbidden(권한없음)", _ResponseSchema.field_failed)
    @ns.header("content-type", "application/json")
    def post(self):
        """회원 가입"""
        return serv.register(request.json)

    # 프로필 하나 요청하는 상황은 없음 ################################
    # # @custom_jwt_required()
    # @ns.response(200, "api요청 성공", _ResponseSchema.field_get_profile)
    # @ns.response(400, "Bad Request", _ResponseSchema.field_failed)
    # @ns.response(403, "Forbidden(권한없음)", _ResponseSchema.field_failed)
    # @ns.doc(params={"id": "프로필 확인할 id"})
    # # @update_location()()
    # def get(self, id=1):
    #     """프로필 확인"""
    #     target_id = request.args.get("id")
    #     if not target_id:
    #         return {"message": "검색할 프로필 id를 제공해야 합니다."}, StatusCode.BAD_REQUEST
    #     return serv.get_profile(id, target_id), 200
    ############################################################

    # @custom_jwt_required()
    @ns.expect(_RequestSchema.field_patch_profile, validate=True)
    @ns.response(200, "api요청 성공", _ResponseSchema.field_patch_setting)
    @ns.response(400, "Bad Request", _ResponseSchema.field_failed)
    @ns.response(403, "Forbidden(권한없음)", _ResponseSchema.field_failed)
    @ns.header("content-type", "multipart/form-data")
    # @update_location()()
    def patch(self, id=1):
        """(최초 1회) 프로필 설정"""
        # [JWT] delete below
        id = 1
        try:
            images = serv.save_pictures(request.files)
            if not images:
                raise Exception("사진 저장 실패")
        except Exception as e:
            print(e)
            return {"message": "사진 저장 실패"}, StatusCode.INTERNAL_ERROR

        return serv.set_profile(request.json, id, images)


@ns.route("/profile-detail")
class ProfileDetail(Resource):
    # @custom_jwt_required()
    @ns.response(200, "api요청 성공", _ResponseSchema.field_get_profileDetail)
    @ns.response(400, "Bad Request", _ResponseSchema.field_failed)
    @ns.response(403, "Forbidden(권한없음)", _ResponseSchema.field_failed)
    @ns.doc(params={"id": "프로필 확인할 id"})
    # @update_location()()
    def get(self, id=1):
        """상세 프로필 확인"""
        target_id = request.args.get("id")
        if not target_id:
            return {
                "message": "프로필을 확인할 유저의 id를 제공해야 합니다."
            }, StatusCode.BAD_REQUEST
        return serv.profile_detail(id, target_id)


@ns.route("/logout")
class Logout(Resource):
    # @custom_jwt_required()
    @ns.response(400, "Bad Request", _ResponseSchema.field_failed)
    @ns.response(403, "Forbidden(권한없음)", _ResponseSchema.field_failed)
    # @update_location()()
    def post(self, id=1):
        """logout"""
        # [JWT] delete below
        id = 1
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
            return {
                "message": "확인할 이메일을 제공해야 합니다."
            }, StatusCode.BAD_REQUEST
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
            return {"message": "로그인 id를 입력해주세요."}, StatusCode.BAD_REQUEST
        return serv.request_reset(login_id)

    @ns.response(400, "Bad Request", _ResponseSchema.field_failed)
    @ns.response(403, "Forbidden(권한없음)", _ResponseSchema.field_failed)
    @ns.doc(params={"key": "(비밀번호 재설정용) 확인 키"})
    @ns.header("content-type", "application/json")
    def post(self):
        """비밀번호 재 설정"""
        key = request.args.get("key")
        if not key:
            return {"message": "인증용 key를 입력해주세요."}, StatusCode.BAD_REQUEST
        return serv.reset_pw(request.json, key)


# soft delete 없을때까지는 사용 안하는걸로 하자
# @ns.route("/unregister")
# class Unregister(Resource):
#     # @custom_jwt_required()
#     @ns.response(400, "Bad Request", _ResponseSchema.field_failed)
#     @ns.response(403, "Forbidden(권한없음)", _ResponseSchema.field_failed)
#     # @update_location()()
#     def delete(self, id=1):
#         """회원 탈퇴"""
#         # [JWT] delete below
#         id = 1
#         return serv.unregister(id)


# ##### taste
@ns.route("/emoji")
class Emoji(Resource):
    # @custom_jwt_required()
    @ns.expect(_RequestSchema.field_patch_emoji, validate=True)
    @ns.response(400, "Bad Request", _ResponseSchema.field_failed)
    @ns.response(403, "Forbidden(권한없음)", _ResponseSchema.field_failed)
    @ns.header("content-type", "application/json")
    # @update_location()()
    def patch(self, id=1):
        """이모지 취향 설정"""
        # [JWT] delete below
        id = 1
        return serv.set_emoji(request.json, id)


# ##### search
@ns.route("/search")
class Search(Resource):
    # @custom_jwt_required()
    @ns.expect(_RequestSchema.field_post_search)
    @ns.response(200, "api요청 성공", _ResponseSchema.field_post_search)
    @ns.response(400, "Bad Request", _ResponseSchema.field_failed)
    @ns.response(403, "Forbidden(권한없음)", _ResponseSchema.field_failed)
    @ns.header("content-type", "application/json")
    # @update_location()()
    def post(self, id=1):
        """유저 검색 기능"""
        # [JWT] delete below
        id = 1
        return serv.search(request.json, id)


# ##### report && block
@ns.route("/report")
class Report(Resource):
    # @custom_jwt_required()
    @ns.expect(_RequestSchema.field_post_report)
    @ns.response(400, "Bad Request", _ResponseSchema.field_failed)
    @ns.response(403, "Forbidden(권한없음)", _ResponseSchema.field_failed)
    @ns.header("content-type", "application/json")
    # @update_location()()
    def post(self, id=1):
        """리포트 하기"""
        # [JWT] delete below
        id = 1
        return serv.report(request.json, id)


@ns.route("/block")
class Block(Resource):
    # @custom_jwt_required()
    @ns.expect(_RequestSchema.field_post_block, validate=True)
    @ns.response(400, "Bad Request", _ResponseSchema.field_failed)
    @ns.response(403, "Forbidden(권한없음)", _ResponseSchema.field_failed)
    @ns.header("content-type", "application/json")
    # @update_location()()
    def post(self, id=1):
        """블록하기"""
        # [JWT] delete below
        id = 1
        return serv.block(request.json, id)
