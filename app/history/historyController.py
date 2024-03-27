from app.db import conn
from flask import request
from flask_restx import Namespace, Resource, fields
from . import historyService as serv
from app.const import History
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..user.userUtils import update_location

ns = Namespace(name='history', description='fancy 및 히스토리 관련 API', path='/history')

class _Schema():             
    field_history = ns.model('fancy, history 체크 시 필요 데이터', {
        'time': fields.String(description='무한 스크롤 기준점'),
    })

    field_fancy = ns.model('(추후 소켓으로 대체 가능성 유)메시지 보낼 때 필요 데이터', {
        'target_id': fields.Integer(description='채팅 대상 아이디'),
    })

    response_fields = ns.model('응답 내용', {
        'message': fields.String(description='응답 별 참고 메시지'),
        'data': fields.Raw(description='API별 필요한 응답 내용')
    })


@ns.route('/checkFancy')
@ns.header('content-type', 'application/json')
class CheckFancy(Resource):
    # @jwt_required()
    @ns.expect(_Schema.field_history)
    @ns.response(200, 'api요청 성공', _Schema.response_fields)
    @ns.response(400, 'api요청 실패', _Schema.response_fields)
    # @update_location
    def post(self):
        """나를 팬시한 사람 그 누구냐!"""
        try:
            id = 1
            # id = get_jwt_identity()['id']
            return serv.viewHistory(request.json, id, History.FANCY)
        except Exception as e:
            conn.rollback()
            return { 'message': 'failed' }, 400
        

@ns.route('/view')
@ns.header('content-type', 'application/json')
class ViewHistory(Resource):
    # @jwt_required()
    @ns.expect(_Schema.field_history)
    @ns.response(200, 'api요청 성공', _Schema.response_fields)
    @ns.response(400, 'api요청 실패', _Schema.response_fields)
    # @update_location
    def post(self):
        """내가 본 사람들"""
        try:
            id = 1
            # id = get_jwt_identity()['id']
            return serv.viewHistory(request.json, id, History.HISTORY)
        except Exception as e:
            conn.rollback()
            return { 'message': 'failed' }, 400
        

@ns.route('/fancy')
@ns.header('content-type', 'application/json')
class Fancy(Resource):
    # @jwt_required()
    @ns.expect(_Schema.field_fancy)
    @ns.response(200, 'api요청 성공', _Schema.response_fields)
    @ns.response(400, 'api요청 실패', _Schema.response_fields)
    # @update_location
    def post(self):
        """fancy/unfancy 했음!"""
        try:
            id = 1
            # id = get_jwt_identity()['id']
            return serv.fancy(request.json, id)
        except Exception as e:
            conn.rollback()
            return { 'message': 'failed' }, 400
        
