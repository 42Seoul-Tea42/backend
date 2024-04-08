from flask import request, redirect, jsonify
import requests, os

# from app.db import conn
from flask_restx import Namespace, Resource, fields, reqparse
from ..user import userService as userServ, userUtils

# from . import userService as serv
# from .userUtils import update_location

ns = Namespace(name='kakao', description='카카오 회원가입/로그인 관련 API', path='/kakao')

domain = os.environ.get('DOMAIN')
client_id = os.environ.get('KAKAO_API_KEY')
redirect_uri = domain + '/kakao/redirect'
kauth_host = "https://kauth.kakao.com"
kapi_host = "https://kapi.kakao.com"
client_secret = os.environ.get('KAKAO_API_SECRET')

##### login
@ns.route('/authorize')
# @ns.header('content-type', 'application/json')
class authorize(Resource):
    def get(self):
        return redirect(
            f"{kauth_host}/oauth/authorize?response_type=code&client_id={client_id}&redirect_uri={redirect_uri}")
        

@ns.route('/redirect')
# @ns.header('content-type', 'application/json')
class redirect_page(Resource):
    def get(self):

        if request.args.get("error"):
            #TODO 카카오 로그인 실패시 처리
            pass

        headers = {'Content-Type': 'application/x-www-form-urlencoded;charset=utf-8'}

        data = {'grant_type': 'authorization_code',
                'client_id': client_id,
                'redirect_uri': redirect_uri,
                'client_secret': client_secret,
                'code': request.args.get("code")}

        resp = requests.post(kauth_host + "/oauth/token", data=data, headers=headers)

        #response
        # HTTP/1.1 200 OK
        # Content-Type: application/json;charset=UTF-8
        # {
        #     "token_type":"bearer",
        #     "access_token":"${ACCESS_TOKEN}",
        #     "expires_in":43199,
        #     "refresh_token":"${REFRESH_TOKEN}",
        #     "refresh_token_expires_in":5184000,
        #     "scope":"account_email profile"
        # }

        headers = {'Content-Type': 'application/x-www-form-urlencoded;charset=utf-8',
                   'Authorization': f'Bearer {resp.json()['access_token']}'}

        resp = requests.post(kauth_host + f"/v2/user/me", headers=headers)

        data = {'login_id': 'kakao' + resp.json()['id'],
                'email': resp.json()['kakao_account']['email'],
                'name': resp.json()['kakao_account']['name']}

        #유저 정보 없으면 회원가입
        try:
            if not userUtils.get_user_by_login_id(data['login_id']):
                userServ.register_kakao(data)
        except Exception:
            #DB 처리 실패 -> email 중복 처리
            return {
                'message': 'fail: cannot register with duplicated email',
                'Location': domain,
            }, 302

        #로그인 후 리 다이렉트
        #TODO [TEST] 리다이렉션 및 데이터 전송
        login_data = jsonify(userServ.login_kakao(data['login_id']))
        return {
            'message': 'succeed',
            'Location': domain,
            'data': login_data
        }, 302