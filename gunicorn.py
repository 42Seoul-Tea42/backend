# 프로젝트 위치
chdir = "/usr/app/srcs"

# 워커 프로세스 수
# workers = 4
workers = 1

# 소켓 접근 권한
bind = ["0.0.0.0:5000", "0.0.0.0:5001", "0.0.0.0:5002"]

# 접속 대기 큐 사이즈
backlog = 2048

# 접속 대기 큐 사이즈 default 30초
# timeout = 60

# 로깅 설정
accesslog = None

# 에러 로그
errorlog = "-"

# 프로세스 파일 위치
pidfile = "/var/run/gunicorn.pid"

# 종료시 프로세스 정리
reload = True

# 워커 자동 재시작
max_requests = 1000
max_requests_jitter = 100
