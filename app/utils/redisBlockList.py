from app import redis_jwt_blocklist
import os


def update_block_list(jti, refresh_jti):

    redis_jwt_blocklist.set(jti, "", ex=int(os.getenv("ACCESS_TIME")))
    redis_jwt_blocklist.set(refresh_jti, "", ex=int(os.getenv("REFRESH_TIME")))


# Redis JWT blocklist schema (db=1)
# 각 jti, refresh_jit가 키로 사용되며 값은 빈 문자열로 설정
# @jwt_required() 실행 시 해당 토큰이 블록리스트에 있는지 확인
# 만료 시간은 토큰 유형의 만료 시간과 동일하게 설정
# {
#     # access_token 고유 식별자
#     "jti": {"": "", "ex": "integer (seconds until expiration)"},
#     # refresh_token 고유 식별자
#     "refresh_jti": {"": "", "ex": "integer (seconds until expiration)"},
# }
