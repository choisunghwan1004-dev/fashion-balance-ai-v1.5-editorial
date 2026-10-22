"""Email link authentication. Only hashes are retained; link consumption is transactional."""
import hashlib
import os
import re
import secrets
import smtplib
import ssl
from email.message import EmailMessage
from urllib.parse import urlsplit
from fastapi import HTTPException, Request
import db


def fail(code, message):
    raise HTTPException(code, message)


def digest(value):
    return hashlib.sha256(value.encode()).hexdigest()


def origin():
    parts = urlsplit(os.getenv('APP_BASE_URL','http://localhost:3000'))
    if parts.scheme not in ('http','https') or not parts.netloc or parts.username or parts.password:
        raise ValueError('APP_BASE_URL must be an HTTP(S) origin')
    if os.getenv('NODE_ENV')=='production' and parts.scheme!='https':
        raise ValueError('Production requires HTTPS')
    return parts.scheme+'://'+parts.netloc


def identify(request: Request):
    token = request.cookies.get('fashion_session','')
    if re.fullmatch('[a-f0-9]{64}',token):
        rows = db.query('''SELECT u.id,u.email,u.nickname FROM auth_sessions s JOIN users u ON u.id=s.user_id
            WHERE s.token_hash=%s AND s.expires_at>UTC_TIMESTAMP() AND u.verified_at IS NOT NULL''',(digest(token),))
        if rows:
            return rows[0]
    return None


def required(request: Request):
    user = identify(request)
    if user is None:
        fail(401,'로그인이 필요합니다.')
    return user


def admin(request: Request):
    user = required(request)
    if user['email'].lower() not in {x.strip().lower() for x in os.getenv('ADMIN_EMAILS','').split(',') if x.strip()}:
        fail(403,'관리자 권한이 필요합니다.')
    return user


def set_session(response, token, max_age=30*86400):
    response.set_cookie('fashion_session',token,max_age=max_age,httponly=True,secure=origin().startswith('https:'),samesite='lax',path='/')


def limit(key, max_hits):
    with db.transaction() as conn:
        bucket = digest(key)
        db.query('''INSERT INTO auth_limits(bucket,hits,expires_at) VALUES(%s,1,DATE_ADD(UTC_TIMESTAMP(),INTERVAL 1 HOUR))
            ON DUPLICATE KEY UPDATE hits=IF(expires_at<=UTC_TIMESTAMP(),1,hits+1),
            expires_at=IF(expires_at<=UTC_TIMESTAMP(),DATE_ADD(UTC_TIMESTAMP(),INTERVAL 1 HOUR),expires_at)''',(bucket,),conn)
        rows = db.query('SELECT hits FROM auth_limits WHERE bucket=%s',(bucket,),conn)
        if rows[0]['hits']>max_hits:
            fail(429,'요청이 많습니다. 1시간 후 다시 시도하세요.')


def send_link(email, token):
    if not os.getenv('SMTP_HOST') or not os.getenv('MAIL_FROM'):
        fail(503,'관리자가 이메일 발송 설정을 완료해야 합니다.')
    message = EmailMessage()
    message['From'] = os.environ['MAIL_FROM']
    message['To'] = email
    message['Subject'] = 'Fashion Balance AI 로그인'
    message.set_content('15분 안에 아래 링크를 여세요. 로그인 완료 버튼을 누르면 인증됩니다.\n'+origin()+'/login.html#token='+token)
    context = ssl.create_default_context()
    secure = os.getenv('SMTP_SECURE','false').lower()=='true'
    host,port = os.environ['SMTP_HOST'],int(os.getenv('SMTP_PORT','465' if secure else '587'))
    if secure:
        connection = smtplib.SMTP_SSL(host,port,timeout=15,context=context)
    else:
        connection = smtplib.SMTP(host,port,timeout=15)
    with connection as smtp:
        if not secure:
            smtp.starttls(context=context)
        if os.getenv('SMTP_USER'):
            smtp.login(os.environ['SMTP_USER'],os.getenv('SMTP_PASSWORD',''))
        smtp.send_message(message)


def request_link(data, ip):
    email = str(data.get('email','')).strip().lower()
    nickname = str(data.get('nickname','')).strip()
    if not re.fullmatch(r'[a-z0-9._%+\-]+@[a-z0-9.\-]+\.[a-z]{2,63}',email) or len(email)>254 or not 1<=len(nickname)<=60:
        fail(400,'닉네임과 이메일을 확인하세요.')
    limit('ip:'+ip,20)
    limit('email:'+email,5)
    if not os.getenv('SMTP_HOST') or not os.getenv('MAIL_FROM'):
        fail(503,'관리자가 이메일 발송 설정을 완료해야 합니다.')
    token = secrets.token_hex(32)
    db.query('INSERT INTO auth_links(token_hash,email,nickname,expires_at) VALUES(%s,%s,%s,DATE_ADD(UTC_TIMESTAMP(),INTERVAL 15 MINUTE))',(digest(token),email,nickname))
    try:
        send_link(email,token)
    except Exception:
        db.query('DELETE FROM auth_links WHERE token_hash=%s',(digest(token),))
        fail(503,'인증 메일 발송에 실패했습니다. 잠시 후 다시 시도하세요.')
    return {'ok':True,'message':'이메일의 인증 링크를 열어 주세요. 링크는 15분 동안 한 번만 사용할 수 있습니다.'}


def verify_link(token, ip):
    limit('verify:'+ip,60)
    if not isinstance(token,str) or not re.fullmatch('[a-f0-9]{64}',token):
        fail(400,'인증 링크가 올바르지 않습니다.')
    with db.transaction() as conn:
        rows = db.query('SELECT email,nickname FROM auth_links WHERE token_hash=%s AND expires_at>UTC_TIMESTAMP() FOR UPDATE',(digest(token),),conn)
        if not rows:
            fail(400,'이미 사용했거나 만료된 링크입니다. 다시 요청하세요.')
        link = rows[0]
        users = db.query('SELECT id,verified_at FROM users WHERE email=%s FOR UPDATE',(link['email'],),conn)
        if users:
            if not users[0]['verified_at']:
                fail(409,'기존 데모 계정 이메일입니다. 다른 이메일을 사용하세요.')
            user_id = users[0]['id']
        else:
            result = db.query('INSERT INTO users(email,password_hash,nickname,verified_at) VALUES(%s,%s,%s,UTC_TIMESTAMP())',(link['email'],'!magic-link-only:'+secrets.token_hex(32),link['nickname']),conn)
            user_id = result['insert_id']
        db.query('DELETE FROM auth_links WHERE token_hash=%s',(digest(token),),conn)
        session = secrets.token_hex(32)
        db.query('INSERT INTO auth_sessions(token_hash,user_id,expires_at) VALUES(%s,%s,DATE_ADD(UTC_TIMESTAMP(),INTERVAL 30 DAY))',(digest(session),user_id),conn)
        return session
