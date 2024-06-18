from flask import request
import requests, os
from flask_restx import Namespace, Resource
from ..user import userService as userServ, userUtils
from ..utils.const import StatusCode, Oauth
from werkzeug.exceptions import BadRequest

ns = Namespace(name='kakao', description='카카오 회원가입/로그인 관련 API', path='/api/kakao')

domain = os.getenv('NEXT_PUBLIC_DOMAIN')
# KaKao
kakao = {
    "token_uri" : "https://kauth.kakao.com/oauth/token",
    "data_uri" : "https://kapi.kakao.com/v2/user/me",
    "redirect_uri" : domain + os.getenv('NEXT_PUBLIC_KAKAO_REDIRECT_URI'),
    "client_id" : os.getenv('KAKAO_API_KEY'),
    "client_secret" :  os.getenv('KAKAO_API_SECRET')
}

##### login
@ns.route('/login')
class authorize(Resource):
    @ns.doc(
        params={"code": "kakao 발급 code", "state": "FE 발급 state"}
    )
    def get(self):
        code = request.args.get("code")
        state = request.args.get("state")
        if not code or not state:
            raise BadRequest("code 또는 state 값이 필요합니다.")
        
        # 카카오 token 요청
        headers = {'Content-Type': 'application/x-www-form-urlencoded;charset=utf-8'}
        data = {
            'grant_type': 'authorization_code',
            'client_id': kakao["client_id"],
            'redirect_uri': kakao["redirect_uri"],
            'client_secret': kakao["client_secret"],
            'code': code,
            'state': state
        }

        resp = requests.post(kakao['token_uri'], data=data, headers=headers)
        if resp.status_code != StatusCode.OK:
            raise BadRequest("카카오 로그인 도중 에러가 발생했습니다.")

        # 카카오 user data 요청
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded;charset=utf-8',
            'Authorization': f'Bearer {resp.json()['access_token']}'
        }

        resp = requests.post(kakao['data_uri'], headers=headers)
        if resp.status_code != StatusCode.OK:
            raise BadRequest("카카오 로그인 도중 에러가 발생했습니다.")

        kakao_data = resp.json()
        data = {
            'login_id': f'kakao{kakao_data['id']}',
            'email': kakao_data['kakao_account']['email'],
            'name': kakao_data['kakao_account']['profile']['nickname']
        }

        #유저 정보 없으면 회원가입
        if userUtils.get_user_by_login_id(data['login_id']) is None:
            userServ.register_oauth(data, Oauth.KAKAO)

        #로그인 후 리 다이렉트
        #TODO [TEST] 리다이렉션 및 데이터 전송
        return userServ.login_kakao(data['login_id'])


# @ns.route('/redirect')
# class redirect_page(Resource):
#     def get(self):

#         #TODO error 맞는지 확인 (request.json)
#         if request.args.get("error"):
#             raise BadRequest("카카오 로그인 도중 에러가 발생했습니다.")

#         headers = {'Content-Type': 'application/x-www-form-urlencoded;charset=utf-8'}

#         data = {'grant_type': 'authorization_code',
#                 'client_id': client_id,
#                 'redirect_uri': Kakao.REDIRECT_URI,
#                 'client_secret': client_secret,
#                 'code': request.args.get("code")}

#         resp = requests.post(Kakao.TOKEN_URI, data=data, headers=headers)
#         if resp.status_code != StatusCode.OK:
#             raise BadRequest("카카오 로그인 도중 에러가 발생했습니다.")

#         headers = {'Content-Type': 'application/x-www-form-urlencoded;charset=utf-8',
#                    'Authorization': f'Bearer {resp.json()['access_token']}'}

#         resp = requests.post(Kakao.DATA_URI, headers=headers)
#         if resp.status_code != StatusCode.OK:
#             raise BadRequest("카카오 로그인 도중 에러가 발생했습니다.")

#         kakao_data = resp.json()
#         data = {'login_id': f'kakao{kakao_data['id']}',
#                 'email': kakao_data['kakao_account']['email'],
#                 'name': kakao_data['kakao_account']['profile']['nickname']}

#         #유저 정보 없으면 회원가입
#         if userUtils.get_user_by_login_id(data['login_id']) is None:
#             userServ.register_kakao(data)

#         #로그인 후 리 다이렉트
#         #TODO [TEST] 리다이렉션 및 데이터 전송
#         return userServ.login_kakao(data['login_id'])