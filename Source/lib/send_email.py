import smtplib
import datetime
from email.mime.text import MIMEText
from email.utils import formataddr
from Source.lib.config import EMAIL_CONFIG


def send_mail(content_text, subject, to_list):
    msg = MIMEText(content_text, 'html', 'utf-8')
    msg['From'] = formataddr(["skipper", EMAIL_CONFIG['user']])
    msg['To'] = ','.join(to_list)
    msg['Subject'] = subject
    server = smtplib.SMTP()
    server.connect(EMAIL_CONFIG['mail_host'])
    server.login(EMAIL_CONFIG['user'], EMAIL_CONFIG['password'])
    server.sendmail(EMAIL_CONFIG['user'], to_list, msg.as_string())
    server.quit()


if __name__ == '__main__':
    subject = 'hello test email'
    subject += datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    content = 'something'
    to_list = ['firstbestma@126.com']
    send_mail(content, subject=subject, to_list=to_list)