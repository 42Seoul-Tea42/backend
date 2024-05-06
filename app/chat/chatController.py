from flask import request
from flask_restx import Namespace, Resource, fields
from . import chatService as serv
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.exceptions import BadRequest

# from ..wrapper.location import check_location

ns = Namespace(name="chat", description="채팅창 관련 API", path="/chat")


class _ResponseSchema:
    field_json_chat = ns.model(
        "채팅 대상 응답 데이터",
        {
            "id": fields.Integer(description="유저 id"),
            "name": fields.String(description="유저 이름"),
            "last_name": fields.String(description="유저 성"),
            "status": fields.Integer(description="유저 온라인 여부"),
            "distance": fields.Float(description="거리"),
            "fancy": fields.Integer(description="유저와의 fancy 관계"),
            "new": fields.Boolean(description="새 메시지 여부"),
            "picture": fields.String(description="유저 프로필 사진 데이터"),
        },
    )

    field_get_list = ns.model(
        "채팅 목록 데이터",
        {
            "chat_list": fields.List(
                fields.Nested(field_json_chat), description="채팅 목록"
            ),
        },
    )

    field_json_msg = ns.model(
        "채팅 하나에 대한 정보",
        {
            "msg_id": fields.Integer(description="메시지 id"),
            "sender": fields.Integer(description="메시지 보낸 사람 id"),
            "msg": fields.String(description="메시지 내용"),
            "msg_time": fields.DateTime(description="메시지 보낸 시간"),
            "checked": fields.Boolean(description="상대방이 확인했는지 여부"),
        },
    )

    field_get_msg = ns.model(
        "채팅 히스토리",
        {
            "msg_list": fields.List(
                fields.Nested(field_json_msg), description="메시지 히스토리"
            ),
        },
    )

    field_failed = ns.model(
        "API 요청 실패",
        {
            "message": fields.String(description="실패 이유"),
        },
    )


@ns.route("/list")
class ChatList(Resource):
    # @jwt_required()
    @ns.response(200, "api요청 성공", _ResponseSchema.field_get_list)
    @ns.response(400, "Bad Request", _ResponseSchema.field_failed)
    @ns.response(403, "Forbidden(권한없음)", _ResponseSchema.field_failed)
    def get(self):
        """채팅리스트를 드립니다!"""
        # id = get_jwt_identity()
        # [JWT] delete below
        id = 1
        return serv.chat_list(id)


@ns.route("/msg")
class GetMsg(Resource):
    # @jwt_required()
    @ns.response(200, "api요청 성공", _ResponseSchema.field_get_msg)
    @ns.response(400, "Bad Request", _ResponseSchema.field_failed)
    @ns.response(403, "Forbidden(권한없음)", _ResponseSchema.field_failed)
    @ns.doc(
        params={"target_id": "메시지 상대 id", "msg_id": "확인할 메시지 기준 msg_id"}
    )
    def get(self):
        """채팅 했던 내용 보내드립니다!!"""
        # id = get_jwt_identity()
        # [JWT] delete below
        id = 1
        target_id = request.args.get("target_id")
        if target_id is None:
            raise BadRequest("메시지를 확인할 유저 id를 제공해야 합니다.")

        msg_id = request.args.get("msg_id")
        if msg_id is None:
            raise BadRequest("로딩 기준 메시지 id를 제공해야 합니다.")

        try:
            target_id = int(target_id)
            msg_id = int(msg_id)
        except ValueError:
            raise BadRequest("id는 숫자로 제공되어야 합니다.")

        return serv.get_msg(id, target_id, msg_id)
