from flask import request, Blueprint
from . import historyService as serv
from ..utils.const import ProfileList
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..utils.validator import Validator


bp_history = Blueprint("history", __name__, url_prefix="/api/history")


@bp_history.route("/fancy-list", methods=["GET"])
@jwt_required()
def get_fancy_list():
    """나를 팬시한 사람 그 누구냐!"""
    id = get_jwt_identity()
    data = Validator.validate(
        {
            "time": request.args.get("time"),
        }
    )

    return serv.view_history(id, data["time"], ProfileList.FANCY)


@bp_history.route("/history-list", methods=["GET"])
@jwt_required()
def get_history_list():
    """내가 본 사람들"""
    id = get_jwt_identity()
    data = Validator.validate(
        {
            "time": request.args.get("time"),
        }
    )
    return serv.view_history(id, data["time"], ProfileList.HISTORY)


@bp_history.route("/visitor-list", methods=["GET"])
@jwt_required()
def get_visitor_list():
    """내가 본 사람들"""
    id = get_jwt_identity()
    data = Validator.validate(
        {
            "time": request.args.get("time"),
        }
    )
    return serv.view_history(id, data["time"], ProfileList.VISITOR)


@bp_history.route("/fancy", methods=["PATCH"])
@jwt_required()
def fancy():
    """타겟을 fancy 합니다"""
    id = get_jwt_identity()
    data = Validator.validate({"target_id": request.json.get("target_id")})

    return serv.fancy(id, data["target_id"])


@bp_history.route("/unfancy", methods=["PATCH"])
@jwt_required()
def unfancy():
    """타겟을 unfancy 합니다"""
    id = get_jwt_identity()
    data = Validator.validate({"target_id": request.json.get("target_id")})

    return serv.unfancy(id, data["target_id"])
