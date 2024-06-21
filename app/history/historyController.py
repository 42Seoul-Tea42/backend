from flask import request
from flask_restx import Namespace, Resource, fields
from . import historyService as serv
from ..utils.const import ProfileList
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..utils.validator import Validator

# from ..wrapper.location import check_location

ns = Namespace(
    name="history", description="fancy 및 히스토리 관련 API", path="/api/history"
)


class _RequestSchema:
    field_patch_fancy = ns.model(
        "fancy / unfancy 시 필요 데이터",
        {
            "target_id": fields.Integer(
                required=True, description="팬시/un팬시할 target id"
            ),
        },
    )


class _ResponseSchema:
    field_get_target_profile = ns.model(
        "profile 확인 응답 데이터",
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

    field_get_profile_list = ns.model(
        "search 응답 데이터",
        {
            "profile_list": fields.List(
                fields.Nested(field_get_target_profile), description="profile JSON list"
            ),
        },
    )

    field_failed = ns.model(
        "API 요청 실패",
        {
            "message": fields.String(description="실패 이유"),
        },
    )


@ns.route("/fancy-list")
class FancyList(Resource):

    @jwt_required()
    @ns.response(200, "api요청 성공", _ResponseSchema.field_get_profile_list)
    @ns.response(400, "Bad Request", _ResponseSchema.field_failed)
    @ns.response(
        401, "Unauthorized: JWT, CSRF token 없음", _ResponseSchema.field_failed
    )
    @ns.response(
        403, "Forbidden: email 인증 혹은 프로필 세팅 안됨", _ResponseSchema.field_failed
    )
    @ns.doc(params={"time": "무한스크롤 시점 확인용 time"})
    def get(self):
        """나를 팬시한 사람 그 누구냐!"""
        id = get_jwt_identity()
        data = Validator.validate(
            {
                "time": request.args.get("time"),
            }
        )

        return serv.view_history(id, data["time"], ProfileList.FANCY)


@ns.route("/fancy")
class Fancy(Resource):

    @jwt_required()
    @ns.expect(_RequestSchema.field_patch_fancy, validate=True)
    @ns.response(400, "Bad Request", _ResponseSchema.field_failed)
    @ns.response(
        401, "Unauthorized: JWT, CSRF token 없음", _ResponseSchema.field_failed
    )
    @ns.response(
        403, "Forbidden: email 인증 혹은 프로필 세팅 안됨", _ResponseSchema.field_failed
    )
    @ns.header("content-type", "application/json")
    def patch(self):
        """타겟을 fancy 합니다"""
        id = get_jwt_identity()
        data = Validator.validate({"target_id": request.json.get("target_id")})

        return serv.fancy(id, data["target_id"])


@ns.route("/unfancy")
class Unfancy(Resource):

    @jwt_required()
    @ns.expect(_RequestSchema.field_patch_fancy, validate=True)
    @ns.response(400, "Bad Request", _ResponseSchema.field_failed)
    @ns.response(
        401, "Unauthorized: JWT, CSRF token 없음", _ResponseSchema.field_failed
    )
    @ns.response(
        403, "Forbidden: email 인증 혹은 프로필 세팅 안됨", _ResponseSchema.field_failed
    )
    @ns.header("content-type", "application/json")
    def patch(self):
        """타겟을 unfancy 합니다"""
        id = get_jwt_identity()
        data = Validator.validate({"target_id": request.json.get("target_id")})

        return serv.unfancy(id, data["target_id"])


@ns.route("/history-list")
class HistoryList(Resource):

    @jwt_required()
    @ns.response(200, "api요청 성공", _ResponseSchema.field_get_profile_list)
    @ns.response(400, "Bad Request", _ResponseSchema.field_failed)
    @ns.response(
        401, "Unauthorized: JWT, CSRF token 없음", _ResponseSchema.field_failed
    )
    @ns.response(
        403, "Forbidden: email 인증 혹은 프로필 세팅 안됨", _ResponseSchema.field_failed
    )
    @ns.doc(params={"time": "무한스크롤 시점 확인용 time"})
    def get(self):
        """내가 본 사람들"""
        id = get_jwt_identity()
        data = Validator.validate(
            {
                "time": request.args.get("time"),
            }
        )
        return serv.view_history(id, data["time"], ProfileList.HISTORY)


@ns.route("/visitor-list")
class VisitorList(Resource):

    @jwt_required()
    @ns.response(200, "api요청 성공", _ResponseSchema.field_get_profile_list)
    @ns.response(400, "Bad Request", _ResponseSchema.field_failed)
    @ns.response(
        401, "Unauthorized: JWT, CSRF token 없음", _ResponseSchema.field_failed
    )
    @ns.response(
        403, "Forbidden: email 인증 혹은 프로필 세팅 안됨", _ResponseSchema.field_failed
    )
    @ns.doc(params={"time": "무한스크롤 시점 확인용 time"})
    def get(self):
        """내가 본 사람들"""
        id = get_jwt_identity()
        data = Validator.validate(
            {
                "time": request.args.get("time"),
            }
        )
        return serv.view_history(id, data["time"], ProfileList.VISITOR)
