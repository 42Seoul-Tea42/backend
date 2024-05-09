from flask import request
from flask_restx import Namespace, Resource, fields
from . import historyService as serv
from ..utils.const import History
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.exceptions import BadRequest
from datetime import datetime

# from ..wrapper.location import check_location

ns = Namespace(
    name="history", description="fancy 및 히스토리 관련 API", path="/history"
)


class _RequestSchema:
    field_patch_fancy = ns.model(
        "fancy / unfancy 시 필요 데이터",
        {
            "target_id": fields.Integer(description="팬시/un팬시할 target id"),
        },
    )


class _ResponseSchema:
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

    field_get_profile_list = ns.model(
        "profile 리스트",
        {
            "profiles": fields.List(
                fields.Nested(field_get_profile), description="profile JSON list"
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
    # @jwt_required()
    @ns.response(200, "api요청 성공", _ResponseSchema.field_get_profile_list)
    @ns.response(400, "Bad Request", _ResponseSchema.field_failed)
    @ns.response(403, "Forbidden(권한없음)", _ResponseSchema.field_failed)
    @ns.doc(params={"time": "무한스크롤 시점 확인용 time"})
    def get(self):
        """나를 팬시한 사람 그 누구냐!"""
        # id = get_jwt_identity()
        # [JWT] delete below
        id = 1
        time_str = request.args.get("time")
        if time_str is None:
            raise BadRequest("검색 기준 일시가 필요합니다.")

        try:
            time = datetime.strptime(time_str, "%Y-%m-%d %H:%M:%S.%f%z")
        except ValueError:
            raise BadRequest("유저 id와 기준 시간의 타입을 확인해주세요.")

        return serv.view_history(id, time, History.FANCY)


@ns.route("/fancy")
class Fancy(Resource):
    # @jwt_required()
    @ns.expect(_RequestSchema.field_patch_fancy, validate=True)
    @ns.response(400, "Bad Request", _ResponseSchema.field_failed)
    @ns.response(403, "Forbidden(권한없음)", _ResponseSchema.field_failed)
    @ns.header("content-type", "application/json")
    def patch(self):
        """fancy/unfancy 했음!"""
        # id = get_jwt_identity()
        # [JWT] delete below
        id = 1
        return serv.fancy(request.json, id)


@ns.route("/history-list")
class ViewHistory(Resource):
    # @jwt_required()
    @ns.response(200, "api요청 성공", _ResponseSchema.field_get_profile_list)
    @ns.response(400, "Bad Request", _ResponseSchema.field_failed)
    @ns.response(403, "Forbidden(권한없음)", _ResponseSchema.field_failed)
    @ns.doc(params={"time": "무한스크롤 시점 확인용 time"})
    def get(self):
        """내가 본 사람들"""
        # id = get_jwt_identity()
        # [JWT] delete below
        id = 1
        time_str = request.args.get("time")
        if time_str is None:
            raise BadRequest("검색 기준 일시가 필요합니다.")

        try:
            time = datetime.strptime(time_str, "%Y-%m-%d %H:%M:%S.%f%z")
        except ValueError:
            raise BadRequest("유저 id와 기준 시간의 타입을 확인해주세요.")

        return serv.view_history(id, time, History.HISTORY)
