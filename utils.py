from django.conf import settings
from django.core.mail import EmailMultiAlternatives

def send_confirm_email(email, token, referer='/'):
    subject = '注册确定邮件'
    text_content = '''
        感谢注册,但你的邮箱服务器不支持html链接功能,请联系管理员!
    '''
    html_content = '''
        <p>感谢注册<a href="http://%s/confirm?token=%s&from=%s">个人博客</a></p>
        <p>请点击链接完成注册!</p>
        <p>该链接的有效期为%s天</p>
    '''%('127.0.0.1:8000', token, referer, settings.CONFIRM_DAYS)

    msg = EmailMultiAlternatives(subject, text_content, settings.EMAIL_HOST_USER, [email])
    msg.attach_alternative(html_content, 'text/html')
    msg.send()

def hash_token(s, salt='mysite'):
    import hashlib
    h = hashlib.md5()
    s += salt
    h.update(s.encode('utf-8'))
    return h.hexdigest()

def make_confirm_string(str):
    from datetime import datetime
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    token = hash_token(str, now)
    return token

# 发送验证码邮件
def send_email_code(email, token):
    subject = '重置密码'
    text_content = '''
        你的邮箱服务器不支持html链接功能,请联系管理员!
    '''
    html_content = '您的验证码是%s, 有效期为10分钟，请及时填写!'%token
    msg = EmailMultiAlternatives(subject, text_content, settings.EMAIL_HOST_USER, [email])
    msg.attach_alternative(html_content, 'text/html')
    # 邮件发送异常不报错
    msg.send(True)
