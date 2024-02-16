from app.db import conn
from flask import request
from flask_restx import Namespace, Resource, fields
from . import userService as serv


ns = Namespace(name='user', description='유저 정보 관련 API', path='/user')

class _Schema():             
    field_login = ns.model('로그인 시 필요 데이터', {
        'login_id': fields.String(description='유저 아이디'),
        'pw': fields.String(description='유저 비밀번호'),
        'longitude': fields.Float(description='경도'),
        'latitude': fields.Float(description='위도')
    })

    field_checkEmail = ns.model('checkEmail 필요 데이터', {
        'email': fields.String(description='중복 확인 이메일'),
    })

    field_checkId = ns.model('checkId 필요 데이터', {
        'login_id': fields.String(description='중복 확인 아이디')
    })

    field_register = ns.model('register 필요 데이터', {
        "email": fields.String(description='이메일'),
        'login_id': fields.String(description='아이디'),
        "pw": fields.String(description='패스워드'),
        "last_name": fields.String(description='성'),
        "name": fields.String(description='이름'),
        "birthday": fields.DateTime(description='생일'),
        'longitude': fields.Float(description='경도'),
        'latitude': fields.Float(description='위도')
    })

    field_changeEmail = ns.model('changeEmail 필요 데이터', {
        "email": fields.String(description='신규 이메일')
    })

    field_setProfile = ns.model('setProfile 필요 데이터', {
        "gender": fields.Integer(description='유저 성별'),
        "taste": fields.Integer(description='유저 취향'),
        "bio": fields.String(description='자기소개'),
        "tags": fields.List(fields.Integer, description='취미 태그'),
        "hate_tags": fields.List(fields.Integer, description='싫어하는 취미 태그'),
    })

    field_setPicture = ns.model('setPicture 필요 데이터', {
        "pictures": fields.List(fields.String, description='취미 태그'),        
    })

    field_setLocation = ns.model('setLocation 필요 데이터', {
        'longitude': fields.Float(description='경도'),
        'latitude': fields.Float(description='위도')
    })

    field_emoji = ns.model('emoji 필요 데이터', {
        "emoji": fields.List(fields.Integer, description='유저 취향 이모지'),
        "hate_emoji": fields.List(fields.Integer, description='싫어하는 이모지'),
        "similar": fields.Boolean(description='비슷한 사람 좋아요%s'),
    })

    field_search = ns.model('search 필요 데이터', {
        "min_age": fields.Integer(description='최소 나이'),
        "max_age": fields.Integer(description='최대 나이'),
        "distance": fields.Float(description='거리'),
        "tags": fields.List(fields.Integer, description='찾고싶은 태그'),
        "fame": fields.Float(description='fame 지수 최소치'),
    })

    field_setting = ns.model('setting 필요 데이터', {
        "email": fields.String(description='이메일'),
        "pw": fields.String(description='패스워드'),
        "last_name": fields.String(description='성'),
        "name": fields.String(description='이름'),
        "birthday": fields.DateTime(description='생일'),
        "gender": fields.String(description='유저 성별'),
        "taste": fields.String(description='유저 취향'),
        "bio": fields.String(description='자기소개'),
        "tags": fields.List(fields.Integer, description='취미 태그'),
        "hate_tags": fields.List(fields.Integer, description='싫어하는 취미 태그'),
        "like_emoji": fields.List(fields.Integer, description='유저 취향 이모지'),
        "hate_emoji": fields.List(fields.Integer, description='싫어하는 이모지'),
        "similar": fields.Boolean(description='비슷한 사람 좋아요%s'),
    })

    # field_profile = ns.model('profile 필요 데이터', {
    #     'target_id': fields.Integer(description='보고 싶은 유저'),
    # })

    field_profileDetail = ns.model('profileDetail 필요 데이터', {
        'target_id': fields.Integer(description='보고 싶은 유저'),
    })

    field_report = ns.model('report 필요 데이터', {
        'target_id': fields.Integer(description='신고 대상 유저'),
    })

    field_block = ns.model('block 필요 데이터', {
        'target_id': fields.Integer(description='블록 대상 유저'),
    })

    field_requestReset = ns.model('requestReset 필요 데이터', {
        'login_id': fields.String(description='유저 로그인 아이디'),
    })

    field_resetPw = ns.model('resetPw 필요 데이터', {
        'pw': fields.String(description='변경할 비밀번호')
    })

    response_fields = ns.model('응답 내용', {
        'message': fields.String(description='응답 별 참고 메시지'),
        'data': fields.Raw(description='API별 필요한 응답 내용')
    })



##### login
@ns.route('/login')
@ns.header('content-type', 'application/json')
class Login(Resource):
    @ns.expect(_Schema.field_login)
    @ns.response(200, 'api요청 성공', _Schema.response_fields)
    @ns.response(400, 'api요청 실패', _Schema.response_fields)
    def post(self):
        """login"""
        try:
            return serv.login(request.json)
        except Exception as e:
            conn.rollback()
            print(f'BE error: {self} {e}')
            return { 'message': 'failed' }, 400

# @ns.route('/kakao')
# def login_kakao():
#     return 'user: kakao'

# @ns.route('/google')
# def login_google():
#     return 'user: google'


# ##### identify
        
@ns.route('/checkId')
@ns.header('content-type', 'application/json')
class CheckId(Resource):
    @ns.expect(_Schema.field_checkId)
    @ns.response(200, 'api요청 성공', _Schema.response_fields)
    @ns.response(400, 'api요청 실패', _Schema.response_fields)
    def post(self):
        """check ID duplication"""
        try:
            return serv.checkId(request.json)
        except Exception as e:
            conn.rollback()
            print(f'BE error: {self} {e}')
            return { 'message': 'failed' }, 400
        

# @ns.route('/profile')
# @ns.header('content-type', 'application/json')
# class Profile(Resource):
#     # @jwt_required()
#     @ns.expect(_Schema.field_profile)
#     @ns.response(200, 'api요청 성공', _Schema.response_fields)
#     @ns.response(400, 'api요청 실패', _Schema.response_fields)
#     def post(self):
#         """프로필 확인"""
#         try:
#             return serv.profile(request.json)
#         except Exception as e:
#             conn.rollback()
#             print(f'BE error: {self} {e}')
#             return { 'message': 'failed' }, 400


@ns.route('/profileDetail')
@ns.header('content-type', 'application/json')
class ProfileDetail(Resource):
    # @jwt_required()
    @ns.expect(_Schema.field_profileDetail)
    @ns.response(200, 'api요청 성공', _Schema.response_fields)
    @ns.response(400, 'api요청 실패', _Schema.response_fields)
    def post(self):
        """상세 프로필 확인"""
        try:
            return serv.profileDetail(request.json)
        except Exception as e:
            conn.rollback()
            print(f'BE error: {self} {e}')
            return { 'message': 'failed' }, 400


@ns.route('/logout')
class Logout(Resource):
    # @jwt_required()
    @ns.response(200, 'api요청 성공', _Schema.response_fields)
    @ns.response(400, 'api요청 실패', _Schema.response_fields)
    def get(self):
        """logout"""
        try:
            return serv.logout()
        except Exception as e:
            conn.rollback()
            print(f'BE error: {self} {e}')
            return { 'message': 'failed' }, 400


# ##### email
@ns.route('/checkEmail')
@ns.header('content-type', 'application/json')
class CheckEmail(Resource):
    @ns.expect(_Schema.field_checkEmail)
    @ns.response(200, 'api요청 성공', _Schema.response_fields)
    @ns.response(400, 'api요청 실패', _Schema.response_fields)
    def post(self):
        """email 중복 확인"""
        try:
            return serv.checkEmail(request.json)
        except Exception as e:
            conn.rollback()
            print(f'BE error: {self} {e}')
            return { 'message': 'failed' }, 400


@ns.route('/emailStatus')
class EmailStatus(Resource):
    # @jwt_required()
    @ns.response(200, 'api요청 성공', _Schema.response_fields)
    @ns.response(400, 'api요청 실패', _Schema.response_fields)
    def get(self):
        """이메일 인증 여부 확인"""
        try:
            return serv.emailStatus()
        except Exception as e:
            conn.rollback()
            print(f'BE error: {self} {e}')
            return { 'message': 'failed' }, 400


@ns.route('/getEmail')
class GetEmail(Resource):
    # @jwt_required()
    @ns.response(200, 'api요청 성공', _Schema.response_fields)
    @ns.response(400, 'api요청 실패', _Schema.response_fields)
    def get(self):
        """이메일 주소 확인"""
        try:
            return serv.getEmail()
        except Exception as e:
            conn.rollback()
            print(f'BE error: {self} {e}')
            return { 'message': 'error' }, 400
        

@ns.route('/sendEmail')
class SendEmail(Resource):
    # @jwt_required()
    @ns.response(200, 'api요청 성공', _Schema.response_fields)
    @ns.response(400, 'api요청 실패', _Schema.response_fields)
    def get(self):
        """인증 메일 다시 보내기"""
        try:
            return serv.sendEmail()
        except Exception as e:
            conn.rollback()
            print(f'BE error: {self} {e}')
            return { 'message': 'failed' }, 400
        

@ns.route('/changeEmail')
@ns.header('content-type', 'application/json')
class ChangeEmail(Resource):
    # @jwt_required()
    @ns.expect(_Schema.field_changeEmail)
    @ns.response(200, 'api요청 성공', _Schema.response_fields)
    @ns.response(400, 'api요청 실패', _Schema.response_fields)
    def post(self):
        """(기존 메일 인증 전) 신규 이메일 등록"""
        try:
            return serv.changeEmail(request.json)
        except Exception as e:
            conn.rollback()
            print(f'BE error: {self} {e}')
            return { 'message': 'failed' }, 400


@ns.route('/registerEmail/<string:key>')
@ns.doc(params={'key': '이메일 인증 링크 중 키'})
class RegisterEmail(Resource):
    @ns.response(200, 'api요청 성공', _Schema.response_fields)
    @ns.response(400, 'api요청 실패', _Schema.response_fields)
    def get(self, key):
        """이메일 인증 진행"""
        try:
            return serv.registerEmail(key)
        except Exception as e:
            conn.rollback()
            print(f'BE error: {self} {e}')
            return { 'message': 'failed' }, 400


# ##### register && setting
@ns.route('/setting')
@ns.header('content-type', 'application/json')
class Setting(Resource):
    # @jwt_required()
    @ns.expect(_Schema.field_setting)
    @ns.response(200, 'api요청 성공', _Schema.response_fields)
    @ns.response(400, 'api요청 실패', _Schema.response_fields)
    def post(self):
        """설정 업데이트 (프로필 사진은 별도로 진행)"""
        try:
            return serv.setting(request.json)
        except Exception as e:
            conn.rollback()
            print(f'BE error: {self} {e}')
            return { 'message': 'failed' }, 400


@ns.route('/register')
@ns.header('content-type', 'application/json')
class Register(Resource):
    @ns.expect(_Schema.field_register)
    @ns.response(200, 'api요청 성공', _Schema.response_fields)
    @ns.response(400, 'api요청 실패', _Schema.response_fields)
    def post(self):
        """회원 정보 등록"""
        try:
            return serv.register(request.json)
        except Exception as e:
            conn.rollback()
            print(f'BE error: {self} {e}')
            return { 'message': 'failed' }, 400


@ns.route('/setProfile')
@ns.header('content-type', 'application/json')
class SetProfile(Resource):
    # @jwt_required()
    @ns.expect(_Schema.field_setProfile)
    @ns.response(200, 'api요청 성공', _Schema.response_fields)
    @ns.response(400, 'api요청 실패', _Schema.response_fields)
    def post(self):
        """(최초 1회) 프로필 설정"""
        try:
            return serv.setProfile(request.json)
        except Exception as e:
            conn.rollback()
            print(f'BE error: {self} {e}')
            return { 'message': 'failed' }, 400


@ns.route('/setPicture')
@ns.header('content-type', 'application/json')
class SetPicture(Resource):
    # @jwt_required()
    @ns.expect(_Schema.field_setPicture)
    @ns.response(200, 'api요청 성공', _Schema.response_fields)
    @ns.response(400, 'api요청 실패', _Schema.response_fields)
    def post(self):
        """(최초 1회 및 설정페이지) 프로필 사진 설정"""
        try:
            return serv.setPicture(request.json)
        except Exception as e:
            conn.rollback()
            print(f'BE error: {self} {e}')
            return { 'message': 'failed' }, 400


@ns.route('/setLocation')
@ns.header('content-type', 'application/json')
class SetLocation(Resource):
    # @jwt_required()
    @ns.expect(_Schema.field_setLocation)
    @ns.response(200, 'api요청 성공', _Schema.response_fields)
    @ns.response(400, 'api요청 실패', _Schema.response_fields)
    def post(self):
        """유저 위치 설정"""
        try:
            return serv.setLocation(request.json)
        except Exception as e:
            conn.rollback()
            print(f'BE error: {self} {e}')
            return { 'message': 'failed' }, 400



@ns.route('/resetPw/<string:key>')
@ns.header('content-type', 'application/json')
@ns.doc(params={'key': '(비밀번호 재설정은 로그인 상태가 아니므로) 아이디 확인용 인증 key'})
class ResetPw(Resource):
    @ns.expect(_Schema.field_resetPw)
    @ns.response(200, 'api요청 성공', _Schema.response_fields)
    @ns.response(400, 'api요청 실패', _Schema.response_fields)
    def post(self, key):
        """비밀번호 재 설정"""
        try:
            return serv.resetPw(request.json, key)
        except Exception as e:
            conn.rollback()
            print(f'BE error: {self} {e}')
            return { 'message': 'failed' }, 400


@ns.route('/requestReset')
@ns.header('content-type', 'application/json')
class RequestReset(Resource):
    @ns.expect(_Schema.field_requestReset)
    @ns.response(200, 'api요청 성공', _Schema.response_fields)
    @ns.response(400, 'api요청 실패', _Schema.response_fields)
    def post(self):
        """비밀번호 재설정 링크 요청 (이메일)"""
        try:
            return serv.requestReset(request.json)
        except Exception as e:
            conn.rollback()
            print(f'BE error: {self} {e}')
            return { 'message': 'failed' }, 400

@ns.route('/unregister')
class Unregister(Resource):
    # @jwt_required()
    @ns.response(200, 'api요청 성공', _Schema.response_fields)
    @ns.response(400, 'api요청 실패', _Schema.response_fields)
    def get(self):
        """회원 탈퇴"""
        try:
            return serv.unregister()
        except Exception as e:
            conn.rollback()
            print(f'BE error: {self} {e}')
            return { 'message': 'failed' }, 400


# ##### taste
@ns.route('/emoji')
@ns.header('content-type', 'application/json')
class Emoji(Resource):
    # @jwt_required()
    @ns.expect(_Schema.field_emoji)
    @ns.response(200, 'api요청 성공', _Schema.response_fields)
    @ns.response(400, 'api요청 실패', _Schema.response_fields)
    def post(self):
        """이모지 취향 설정"""
        try:
            return serv.emoji(request.json)
        except Exception as e:
            conn.rollback()
            print(f'BE error: {self} {e}')
            return { 'message': 'failed' }, 400


# ##### search
@ns.route('/search')
@ns.header('content-type', 'application/json')
class Search(Resource):
    # @jwt_required()
    @ns.expect(_Schema.field_search)
    @ns.response(200, 'api요청 성공', _Schema.response_fields)
    @ns.response(400, 'api요청 실패', _Schema.response_fields)
    def post(self):
        """유저 검색 기능"""
        try:
            return serv.search(request.json)
        except Exception as e:
            conn.rollback()
            print(f'BE error: {self} {e}')
            return { 'message': 'failed' }, 400


# ##### report && block
@ns.route('/report')
@ns.header('content-type', 'application/json')
class Report(Resource):
    # @jwt_required()
    @ns.expect(_Schema.field_report)
    @ns.response(200, 'api요청 성공', _Schema.response_fields)
    @ns.response(400, 'api요청 실패', _Schema.response_fields)
    def post(self):
        """리포트 하기"""
        try:
            return serv.report(request.json)
        except Exception as e:
            conn.rollback()
            print(f'BE error: {self} {e}')
            return { 'message': 'failed' }, 400


@ns.route('/block')
@ns.header('content-type', 'application/json')
class Block(Resource):
    # @jwt_required()
    @ns.expect(_Schema.field_block)
    @ns.response(200, 'api요청 성공', _Schema.response_fields)
    @ns.response(400, 'api요청 실패', _Schema.response_fields)
    def post(self):
        """블록하기"""
        try:
            return serv.block(request.json)
        except Exception as e:
            conn.rollback()
            print(f'BE error: {self} {e}')
            return { 'message': 'failed' }, 400