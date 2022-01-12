import smtplib
from email.mime.text import MIMEText


def read_file(url):
    with open(url, 'r') as f:
        str = ''
        for line in f:
            str += line
    return str


def send_mail(to='389053452@qq.com', content='None', title='系统文件'):
    # 设置服务信息
    config = {
        'mail_host': 'smtp.163.com',
        # 163用户名
        'mail_user': '13159170392',
        # 密码(部分邮箱为授权码)
        'mail_pass': 'LWJIBCMUMPLIMKVK',
        # 邮件发送方邮箱地址
        'sender': '13159170392@163.com'
    }

    receivers = to

    # 设置email信息
    # 邮件内容设置
    message = MIMEText(content, 'plain', 'utf-8')
    # 邮件主题
    message['Subject'] = title
    # 发送方信息
    message['From'] = config['sender']

    # 接受方信息
    accepters = ''
    if isinstance(to, list):
        accepters = ", ".join(to)
    else:
        accepters = to
    message['To'] = accepters

    # 登录并发送邮件
    try:
        smtpObj = smtplib.SMTP()
        # 连接到服务器
        smtpObj.connect(config['mail_host'], 25)
        # 登录到服务器
        smtpObj.login(config['mail_user'], config['mail_pass'])
        # 发送
        smtpObj.sendmail(config['sender'], receivers, message.as_string())
        print('success')
    except smtplib.SMTPException as e:
        print('error', e)  # 打印错误
    finally:
        smtpObj.quit()


if __name__ == '__main__':
    content = read_file('test.txt')
    accepters = [
        '389053452@qq.com', '13159170392@163.com', 'lyk9406@gmail.com'
    ]
    send_mail(to=accepters, content=content)
