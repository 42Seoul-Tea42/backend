from flask import request, Blueprint
from . import chatService as serv
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..utils.validator import Validator


bp_chat = Blueprint("chat", __name__, url_prefix="/api/chat")


@bp_chat.route("/list", methods=["GET"])
@jwt_required()
def get_chat_list():
    """채팅리스트를 드립니다!"""
    id = get_jwt_identity()
    return serv.chat_list(id)


@bp_chat.route("/msg", methods=["GET"])
@jwt_required()
def get_chatroom_msg():
    """채팅 했던 내용 보내드립니다!!"""
    id = get_jwt_identity()
    data = Validator.validate(
        {
            "target_id": request.args.get("target_id"),
            "time": request.args.get("time"),
        }
    )
    return serv.get_msg(id, data)
