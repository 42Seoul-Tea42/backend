from flask import request
from flask_restx import Namespace, Resource, fields
from . import historyService as serv
from ..utils.const import History
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.exceptions import BadRequest
from datetime import datetime
from ..utils.const import KST, TIME_STR_TYPE

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
class CheckFancy(Resource):

    @jwt_required()
    @ns.response(200, "api요청 성공", _ResponseSchema.field_get_profile_list)
    @ns.response(400, "Bad Request: 잘못된 요청", _ResponseSchema.field_failed)
    @ns.response(
        401, "Unauthorized: JWT, CSRF token 없음", _ResponseSchema.field_failed
    )
    @ns.response(403, "Forbidden: (token 외) 권한 없음", _ResponseSchema.field_failed)
    @ns.doc(params={"time": "무한스크롤 시점 확인용 time"})
    def get(self):
        """나를 팬시한 사람 그 누구냐!"""
        id = get_jwt_identity()
        # [JWT] delete below
        # id = 1

        try:
            time_str = request.args.get("time")
            if time_str is None:
                time = datetime.now(KST)
            else:
                time = datetime.strptime(time_str, TIME_STR_TYPE)
        except ValueError:
            raise BadRequest("기준 시간이 유효하지 않습니다.")

        return serv.view_history(id, time, History.FANCY)


@ns.route("/fancy")
class Fancy(Resource):

    @jwt_required()
    @ns.expect(_RequestSchema.field_patch_fancy, validate=True)
    @ns.response(400, "Bad Request: 잘못된 요청", _ResponseSchema.field_failed)
    @ns.response(
        401, "Unauthorized: JWT, CSRF token 없음", _ResponseSchema.field_failed
    )
    @ns.response(403, "Forbidden: (token 외) 권한 없음", _ResponseSchema.field_failed)
    @ns.header("content-type", "application/json")
    def patch(self):
        """타겟을 fancy 합니다"""
        id = get_jwt_identity()
        # [JWT] delete below
        # id = 1
        return serv.fancy(request.json, id)


@ns.route("/unfancy")
class Unfancy(Resource):

    @jwt_required()
    @ns.expect(_RequestSchema.field_patch_fancy, validate=True)
    @ns.response(400, "Bad Request: 잘못된 요청", _ResponseSchema.field_failed)
    @ns.response(
        401, "Unauthorized: JWT, CSRF token 없음", _ResponseSchema.field_failed
    )
    @ns.response(403, "Forbidden: (token 외) 권한 없음", _ResponseSchema.field_failed)
    @ns.header("content-type", "application/json")
    def patch(self):
        """타겟을 unfancy 합니다"""
        id = get_jwt_identity()
        # [JWT] delete below
        # id = 1
        return serv.unfancy(request.json, id)


@ns.route("/history-list")
class ViewHistory(Resource):

    @jwt_required()
    @ns.response(200, "api요청 성공", _ResponseSchema.field_get_profile_list)
    @ns.response(400, "Bad Request: 잘못된 요청", _ResponseSchema.field_failed)
    @ns.response(
        401, "Unauthorized: JWT, CSRF token 없음", _ResponseSchema.field_failed
    )
    @ns.response(403, "Forbidden: (token 외) 권한 없음", _ResponseSchema.field_failed)
    @ns.doc(params={"time": "무한스크롤 시점 확인용 time"})
    def get(self):
        """내가 본 사람들"""
        id = get_jwt_identity()
        # [JWT] delete below
        # id = 1

        try:
            time_str = request.args.get("time")
            if time_str is None:
                time = datetime.now(KST)
            else:
                time = datetime.strptime(time_str, TIME_STR_TYPE)
        except ValueError:
            raise BadRequest("기준 시간이 유효하지 않습니다.")

        return serv.view_history(id, time, History.HISTORY)
