from app.db import conn
from flask import request
from flask_restx import Namespace, Resource, fields
from . import chatService as serv

ns = Namespace(name='chat', description='채팅창 관련 API', path='/chat')

class _Schema():             
    field_msg = ns.model('기존 채팅방 채팅 요청 시 필요 데이터', {
        'target_id': fields.Integer(description='채팅 대상 아이디'),
        'msg_id': fields.Integer(description='무한로딩용 기준 점(초기값 -1: 오버플로우임ㅋㅋ)'),
    })

    # field_send = ns.model('(추후 소켓으로 대체 가능성 유)메시지 보낼 때 필요 데이터', {
    #     'target_id': fields.Integer(description='채팅 대상 아이디'),
    #     'msg': fields.String(description='보내는 메시지 내용')
    # })

    response_fields = ns.model('응답 내용', {
        'message': fields.String(description='응답 별 참고 메시지'),
        'data': fields.Raw(description='API별 필요한 응답 내용')
    })


@ns.route('/list')
@ns.header('content-type', 'application/json')
class ChatList(Resource):
    # @jwt_required()
    @ns.response(200, 'api요청 성공', _Schema.response_fields)
    @ns.response(400, 'api요청 실패', _Schema.response_fields)
    def get(self):
        """채팅리스트를 드립니다!"""
        try:
            return serv.chatList()
        except Exception as e:
            conn.rollback()
            return { 'message': 'failed' }, 400


@ns.route('/msg')
@ns.header('content-type', 'application/json')
class GetMsg(Resource):
    # @jwt_required()
    @ns.expect(_Schema.field_msg)
    @ns.response(200, 'api요청 성공', _Schema.response_fields)
    @ns.response(400, 'api요청 실패', _Schema.response_fields)
    def post(self):
        """채팅 했던 내용 보내드립니다!!"""
        try:
            return serv.getMsg(request.json)
        except Exception as e:
            conn.rollback()
            return { 'message': 'failed' }, 400


# 웹소켓으로 처리
# @ns.route('/send')
# @ns.header('content-type', 'application/json')
# class SendChat(Resource):
#     # @jwt_required()
#     @ns.expect(_Schema.field_send) #안필요할듯!
#     @ns.response(200, 'api요청 성공', _Schema.response_fields)
#     @ns.response(400, 'api요청 실패', _Schema.response_fields)
#     def post(self):
#         """저쪽 신사/숙녀분께 메시지 보내드리겠습니다"""
#         try:
#             return serv.sendChat(request.json)
#         except Exception as e:
            # conn.rollback()
#             return { 'message': 'failed' }, 400