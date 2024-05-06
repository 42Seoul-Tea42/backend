from flask_restx import Namespace, Resource, fields
from . import teaService as serv

# from ..wrapper.location import check_location
from flask_jwt_extended import jwt_required, get_jwt_identity

ns = Namespace(name="tea", description="추천 관련 API", path="/tea")


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

    field_get_tea = ns.model(
        "tea 추천 응답 데이터",
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


@ns.route("/")
class Suggest(Resource):
    # @jwt_required()
    @ns.response(200, "api요청 성공", _ResponseSchema.field_get_tea)
    @ns.response(400, "Bad Request", _ResponseSchema.field_failed)
    @ns.response(403, "Forbidden(권한없음)", _ResponseSchema.field_failed)
    def get(self):
        """get tea suggestions for you!"""
        # id = get_jwt_identity()
        # [JWT] delete below
        id = 1
        return serv.suggest(id)
