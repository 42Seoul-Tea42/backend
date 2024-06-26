from flask import request, Blueprint
import requests, os
from ..user import userService as userServ, userUtils
from ..utils.const import StatusCode, Oauth
from werkzeug.exceptions import BadRequest

bp_kakao = Blueprint('kakao', __name__, url_prefix='/api/kakao')

domain = os.getenv('NEXT_PUBLIC_DOMAIN')

# KaKao
kakao = {
    "token_uri" : "https://kauth.kakao.com/oauth/token",
    "data_uri" : "https://kapi.kakao.com/v2/user/me",
    "redirect_uri" : domain + os.getenv('NEXT_PUBLIC_KAKAO_REDIRECT_URI'),
    "client_id" : os.getenv('KAKAO_API_KEY'),
    "client_secret" :  os.getenv('KAKAO_API_SECRET')
}

@bp_kakao.route('/login', methods=['GET'])
def login_kakao():
    code = request.args.get("code")
    state = request.args.get("state")
    if code is None or state is None:
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
        'name': kakao_data['kakao_account']['profile']['nickname'],
        'last_name': kakao_data['kakao_account']['profile']['nickname'][0],
    }

    #유저 정보 없으면 회원가입
    if userUtils.get_user_by_login_id(data['login_id']) is None:
        userServ.register_oauth(data, Oauth.KAKAO)

    #로그인 후 리 다이렉트
    #TODO [TEST] 리다이렉션 및 데이터 전송
    return userServ.login_oauth(data['login_id'])
