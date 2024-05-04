import smtplib
import os
from email.mime.multipart import (
    MIMEMultipart,
)  # 메일의 Data 영역의 메시지를 만드는 모듈
from email.mime.text import MIMEText  # 메일의 본문 내용을 만드는 모듈
from .const import Key

# smpt 서버와 연결
email_smtp = os.environ.get("EMAIL_SMTP")
email_port = os.environ.get("EMAIL_PORT")
smtp = smtplib.SMTP(email_smtp, email_port)

# 로그인
email_account = os.environ.get("EMAIL_ACCOUNT")
email_password = os.environ.get("EMAIL_PASSWORD")
smtp.ehlo()
smtp.starttls()
smtp.login(email_account, email_password)


def send_smtp_email(addr_to, key, opt) -> str:
    msg = MIMEMultipart()
    msg["From"] = email_account
    msg["To"] = addr_to

    domain = os.environ.get("DOMAIN")

    if opt == Key.EMAIL:
        msg["Subject"] = f"[Tea For Two] 이메일 인증 요청"  # 메일 제목
        content = f"""안녕하세요.\n\n
                    Tea For Two를 이용해주셔서 감사합니다.\n
                    아래 링크를 통해 인증을 완료해주세요.\n
                    {domain}{os.environ.get("EMAIL_CALLBACK_LINK")}?page={opt}&key={key}\n\n
                    만일 본 이메일이 의도치 않게 수신되었거나 인증을 요청하지 않았다면, 이 이메일을 무시해주시기 바랍니다.\n\n
                    감사합니다.\n"""
        msg.attach(MIMEText(content, "plain"))

    elif opt == Key.PASSWORD:
        msg["Subject"] = f"[Tea For Two] 비밀번호 재 설정 안내"  # 메일 제목
        content = f"""안녕하세요.\n\n
                    Tea For Two를 이용해주셔서 감사합니다.\n
                    비밀번호를 재설정하실 수 있도록 안내드립니다.\n
                    아래 링크를 클릭하시면 비밀번호 재설정 페이지로 이동하실 수 있습니다.\n
                    {domain}{os.environ.get("EMAIL_CALLBACK_LINK")}?page={opt}&key={key}\n\n
                    비밀번호를 안전하게 유지하기 위해 주기적으로 변경하시는 것이 좋습니다.\n
                    만일 본 이메일이 의도치 않게 수신되었다면, 이 이메일을 무시해주시기 바랍니다.\n\n
                    감사합니다.\n"""
        msg.attach(MIMEText(content, "plain"))

    smtp.sendmail(email_account, addr_to, msg.as_string())


# # smtp 서버 연결 해제
# smtp.quit()
