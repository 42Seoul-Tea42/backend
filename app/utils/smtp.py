import smtplib
import os
from email.mime.multipart import MIMEMultipart # 메일의 Data 영역 메시지 만드는 모듈
from email.mime.text import MIMEText  # 메일의 본문 내용을 만드는 모듈
from .const import Key

# 필요 환경변수
email_smtp = os.getenv("EMAIL_SMTP")
email_port = os.getenv("EMAIL_PORT")
email_account = os.getenv("EMAIL_ACCOUNT")
email_password = os.getenv("EMAIL_PASSWORD")

# 전역 변수로 SMTP 객체와 연결 상태를 유지
smtp = None


def get_smtp_connection():
    global smtp

    if smtp is None or not smtp.sock:
        try:
            # smtp 서버와 연결
            smtp = smtplib.SMTP(email_smtp, email_port, timeout=10)

            # 로그인
            smtp.ehlo()
            smtp.starttls()
            smtp.ehlo()
            smtp.login(email_account, email_password)

        except smtplib.SMTPException as e:
            smtp = None
            raise e



def send_smtp_email(addr_to, key, opt, retry_count=0) -> str:
    global smtp

    if retry_count > 2:
        print("[SMTP ERROR] Failed to send email after multiple attempts")
        return

    try:
        get_smtp_connection()

        msg = MIMEMultipart()
        msg["From"] = email_account
        msg["To"] = addr_to

        domain = os.getenv("NEXT_PUBLIC_DOMAIN")

        if opt == Key.EMAIL:
            msg["Subject"] = f"[Tea For Two] 이메일 인증 요청"  # 메일 제목
            content = f"""안녕하세요.\n\n
                        Tea For Two를 이용해주셔서 감사합니다.\n
                        아래 링크를 통해 인증을 완료해주세요.\n
                        {domain}{os.getenv("EMAIL_CALLBACK_LINK")}?key={key}\n\n
                        만일 본 이메일이 의도치 않게 수신되었거나 인증을 요청하지 않았다면, 이 이메일을 무시해주시기 바랍니다.\n\n
                        감사합니다.\n"""
            msg.attach(MIMEText(content, "plain"))

        elif opt == Key.PASSWORD:
            msg["Subject"] = f"[Tea For Two] 비밀번호 재 설정 안내"  # 메일 제목
            content = f"""안녕하세요.\n\n
                        Tea For Two를 이용해주셔서 감사합니다.\n
                        비밀번호를 재설정하실 수 있도록 안내드립니다.\n
                        아래 링크를 클릭하시면 비밀번호 재설정 페이지로 이동하실 수 있습니다.\n
                        {domain}{os.getenv("PASSWORD_CALLBACK_LINK")}?key={key}\n\n
                        비밀번호를 안전하게 유지하기 위해 주기적으로 변경하시는 것이 좋습니다.\n
                        만일 본 이메일이 의도치 않게 수신되었다면, 이 이메일을 무시해주시기 바랍니다.\n\n
                        감사합니다.\n"""
            msg.attach(MIMEText(content, "plain"))

        smtp.sendmail(email_account, addr_to, msg.as_string())

    except (smtplib.SMTPException, ssl.SSLError) as e:
        smtp = None
        send_smtp_email(addr_to, key, opt, retry_count+1)


# # smtp 서버 연결 해제
# smtp.quit()
