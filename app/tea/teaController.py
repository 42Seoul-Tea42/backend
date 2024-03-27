from app.db import conn
from flask_restx import Namespace, Resource, fields
from . import teaService as serv
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..user.userUtils import update_location

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
    # @update_location
    def get(self):
        """get tea suggestions for you!"""
        try:
            id = 1
            # id = get_jwt_identity()['id']
            return serv.suggest(id)
        except Exception as e:
            conn.rollback()
            print(f'BE error: {self} {e}')
            return { 'message': 'failed' }, 400
