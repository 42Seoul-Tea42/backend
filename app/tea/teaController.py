from app.db import conn
from flask_restx import Namespace, Resource, fields
from . import teaService as serv
from flask import jsonify

ns = Namespace(name='tea', description='추천 관련 API', path='/tea')

class _Schema():
    response_fields = ns.model('응답 내용', {
        'message': fields.String(description='응답 별 참고 메시지'),
        'data': fields.Raw(description='API별 필요한 응답 내용')
    })


@ns.route('/')
@ns.header('content-type', 'application/json')
class Suggest(Resource):
    # @jwt_required()
    @ns.response(200, 'api요청 성공', _Schema.response_fields)
    @ns.response(400, 'api요청 실패', _Schema.response_fields)
    def get(self):
        """get tea suggestions for you!"""
        try:
            return serv.suggest()
        except Exception as e:
            conn.rollback()
            print(f'BE error: {self} {e}')
            return { 'message': 'failed' }, 400
