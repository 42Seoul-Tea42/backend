from flask import request, Blueprint
from . import userService as serv
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.exceptions import BadRequest, InternalServerError
from ..utils.validator import Validator
from ..wrapper.location import check_location

bp_user = Blueprint("user", __name__, url_prefix="/api/user")


##### login
@bp_user.route("/login", methods=["GET"])
@jwt_required()
def check_user_login():
    """login 확인"""
    id = get_jwt_identity()
    return serv.login_check(id)


@bp_user.route("/login", methods=["POST"])
def login_user():
    """login"""
    data = Validator.validate(
        {
            "login_id": request.json.get("login_id"),
            "pw": request.json.get("pw"),
        }
    )
    return serv.login(data)


##### id 중복검사
@bp_user.route("/check-id", methods=["GET"])
def check_available_id():
    """check ID duplication"""
    data = Validator.validate({"login_id": request.args.get("login_id")})
    return serv.check_id(data["login_id"])


##### email 중복검사
@bp_user.route("/check-email", methods=["GET"])
def check_available_email():
    """email 중복 확인"""
    data = Validator.validate({"email": request.args.get("email")})
    return serv.check_email(data["email"])


##### email 확인
@bp_user.route("/email", methods=["GET"])
@jwt_required()
def get_user_email():
    """이메일 주소 확인"""
    id = get_jwt_identity()
    return serv.get_email(id)


@bp_user.route("/email", methods=["PATCH"])
@jwt_required()
def change_user_email():
    """(기존 메일 인증 전) 신규 이메일 등록"""
    id = get_jwt_identity()
    data = Validator.validate({"email": request.json.get("email")})
    return serv.change_email(id, data["email"])


##### (인증용) email 다시 보내기
@bp_user.route("/send-email", methods=["GET"])
@jwt_required()
def resend_check_email():
    """인증 메일 다시 보내기"""
    id = get_jwt_identity()
    return serv.resend_email(id)


##### email 인증
@bp_user.route("/verify-email", methods=["GET"])
def verify_email():
    """이메일 인증 진행"""
    data = Validator.validate({"key": request.args.get("key")})
    return serv.verify_email(data["key"])


##### 회원가입
@bp_user.route("/profile", methods=["POST"])
def register_user():
    """회원 가입"""
    data = Validator.validate(
        {
            "email": request.json.get("email"),
            "login_id": request.json.get("login_id"),
            "pw": request.json.get("pw"),
            "last_name": request.json.get("last_name"),
            "name": request.json.get("name"),
        }
    )
    return serv.register(data)


##### 회원 정보 수정
@bp_user.route("/profile", methods=["PATCH"])
@jwt_required()
def update_user_profile():
    """회원 정보 업데이트"""
    id = get_jwt_identity()
    if not request.json:
        raise BadRequest("바꿀 정보가 없습니다.")

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

    data = Validator.validate_setting(request.json)
    return serv.setting(id, data, images)


##### (자기자신) 프로필 확인
@bp_user.route("/profile", methods=["GET"])
@jwt_required()
def get_user_profile():
    """프로필 확인"""
    id = get_jwt_identity()
    return serv.get_profile(id)


##### (타인) 프로필 세부정보 확인
@bp_user.route("/profile-detail", methods=["GET"])
@jwt_required()
def get_user_profile_detail():
    """상세 프로필 확인"""
    id = get_jwt_identity()
    data = Validator.validate({"target_id": request.args.get("id")})
    return serv.profile_detail(id, data["target_id"])


##### 로그아웃
@bp_user.route("/logout", methods=["POST"])
@jwt_required()
@check_location
def logout():
    """logout"""
    id = get_jwt_identity()
    return serv.logout(id)


##### ID 찾기
@bp_user.route("/login-id", methods=["GET"])
def find_login_id():
    """유저 email로 ID 찾기"""
    data = Validator.validate({"email": request.args.get("email")})
    return serv.find_login_id(data["email"])


##### 비밀번호 재설정 메일 요청
@bp_user.route("/reset-pw", methods=["GET"])
def request_reset_pw():
    """비밀번호 재설정 링크 요청 (이메일)"""
    data = Validator.validate({"login_id": request.args.get("login_id")})
    return serv.request_reset(data["login_id"])


##### 비밀번호 재설정
@bp_user.route("/reset-pw", methods=["POST"])
def reset_pw():
    """비밀번호 재설정"""
    data = Validator.validate(
        {
            "pw": request.json.get("pw"),
            "key": request.args.get("key"),
        }
    )
    return serv.reset_pw(data["pw"], data["key"])


# soft delete 없을때까지는 사용 안하는걸로 하자
# ##### 회원 탈퇴
# @bp_user.route("/unregister", methods=["DELETE"])
# @jwt_required()
# def unregister():
#     """회원 탈퇴"""
#     id = get_jwt_identity()
#     return serv.unregister(id)


##### search
@bp_user.route("/search", methods=["POST"])
@jwt_required()
def search():
    """유저 검색 기능"""
    id = get_jwt_identity()
    data = Validator.validate(
        {
            "min_age": request.json.get("min_age"),
            "max_age": request.json.get("max_age"),
            "distance": request.json.get("distance"),
            "tags": request.json.get("tags"),
            "fame": request.json.get("fame"),
        }
    )
    return serv.search(id, data)


##### tea suggest
@bp_user.route("/tea", methods=["GET"])
@jwt_required()
def suggest():
    """get tea suggestions for you!"""
    id = get_jwt_identity()
    return serv.suggest(id)


##### report && block
@bp_user.route("/report", methods=["POST"])
@jwt_required()
def report_user():
    """리포트 하기"""
    id = get_jwt_identity()
    data = Validator.validate(
        {
            "target_id": request.json.get("target_id"),
            "reason": request.json.get("reason"),
            "reason_opt": request.json.get("reason_opt"),
        }
    )
    return serv.report(id, data)


@bp_user.route("/block", methods=["POST"])
@jwt_required()
def block_user():
    """블록하기"""
    id = get_jwt_identity()
    data = Validator.validate({"target_id": request.json.get("target_id")})
    return serv.block(id, data["target_id"])


##### access token 재발행
@bp_user.route("/reset-token", methods=["PATCH"])
@jwt_required(refresh=True)
def reset_token():
    """토큰 재발급"""
    id = get_jwt_identity()
    return serv.reset_token(id)
