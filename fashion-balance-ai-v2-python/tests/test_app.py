"""HTTP behavior and authorization tests with an explicit fake database (not a MySQL test)."""
from contextlib import contextmanager
import copy
import json
import threading
from datetime import datetime
import pytest
from fastapi.testclient import TestClient
import app
import auth
import db
import recommend


@pytest.fixture
def store(monkeypatch,tmp_path):
    state={'links':{},'sessions':{},'users':{},'photos':{},'profiles':{},'calls':[],'items':{},'wardrobe':[], 'history':[]}
    lock=threading.RLock()
    @contextmanager
    def transaction():
        with lock:
            backup=copy.deepcopy(state)
            try:yield object()
            except Exception:
                state.clear();state.update(backup);raise
    def query(sql,v=(),connection=None):
        state['calls'].append((sql,v))
        if sql.startswith('SELECT u.id'):
            uid=state['sessions'].get(v[0]);return [state['users'][uid]] if uid else []
        if sql.startswith('INSERT INTO auth_links'):
            state['links'][v[0]]={'email':v[1],'nickname':v[2]};return {'insert_id':0}
        if sql.startswith('SELECT email,nickname FROM auth_links'):
            return [state['links'][v[0]]] if v[0] in state['links'] else []
        if sql.startswith('SELECT id,verified_at FROM users'):
            return [u for u in state['users'].values() if u['email']==v[0]]
        if sql.startswith('INSERT INTO users'):
            uid=len(state['users'])+2;state['users'][uid]={'id':uid,'email':v[0],'nickname':v[2],'verified_at':True};return {'insert_id':uid}
        if sql.startswith('DELETE FROM auth_links'):
            state['links'].pop(v[0],None);return {}
        if sql.startswith('INSERT INTO auth_sessions'):
            state['sessions'][v[0]]=v[1];return {}
        if sql.startswith('DELETE FROM auth_sessions'):
            state['sessions'].pop(v[0],None);return {}
        if sql.startswith('SELECT face_shape'):
            return [state['profiles'][v[0]]] if v[0] in state['profiles'] else []
        if sql.startswith('INSERT INTO style_profiles'):
            state['profiles'][v[0]]=dict(zip(app.PROFILE,v[1:]));return {}
        if sql.startswith('INSERT INTO private_photos'):
            state['photos'][v[0]]=v[1];return {}
        if sql.startswith('SELECT filename'):
            return [{'filename':v[0]}] if state['photos'].get(v[0])==v[1] else []
        if sql.startswith('SELECT id FROM fashion_items'):
            row=state['items'].get(v[0]);return [row] if row and row.get('owner_user_id') in (None,v[1]) else []
        if sql.startswith('SELECT id,payload'):
            return [h for h in state['history'] if h['user_id']==v[0]]
        if sql.startswith('SELECT w.item_id'):
            return []
        if sql.startswith('INSERT IGNORE INTO wardrobe_items'):
            state['wardrobe'].append(v);return {}
        raise AssertionError('Unexpected SQL: '+sql)
    monkeypatch.setattr(db,'query',query);monkeypatch.setattr(db,'transaction',transaction)
    monkeypatch.setattr(auth,'limit',lambda *args:None)
    monkeypatch.setattr(app,'PRIVATE',tmp_path/'uploads');app.PRIVATE.mkdir()
    monkeypatch.setenv('APP_BASE_URL','http://localhost:3000');monkeypatch.setenv('SMTP_HOST','smtp.example.test');monkeypatch.setenv('MAIL_FROM','test@example.test')
    monkeypatch.setenv('ADMIN_EMAILS','admin@example.test')
    state['users']={2:{'id':2,'email':'a@example.test','nickname':'회원 A','verified_at':True},3:{'id':3,'email':'b@example.test','nickname':'회원 B','verified_at':True}}
    state['sessions']={auth.digest('a'*64):2,auth.digest('b'*64):3}
    return state


@pytest.fixture
def client(store):
    with TestClient(app.app,base_url='http://localhost:3000') as c:
        yield c


def headers(who='a'):
    return {'Origin':'http://localhost:3000','Cookie':'fashion_session='+who*64}


@pytest.mark.parametrize('path',['/api/profile','/api/wardrobe','/api/outfits/history','/api/vision/status','/uploads/test.png'])
def test_guests_denied(client,path):
    assert client.get(path).status_code==401


def test_real_react_build_and_qr(client):
    assert client.get('/').status_code==200
    assert 'id="root"' in client.get('/').text
    assert '<svg' in client.get('/api/auth/qr').text
    assert client.get('/.env').status_code==404
    assert client.get('/app.py').status_code==404
    assert client.get('/V1.9_ORIGINAL_BACKUP.zip').status_code==404


def test_profile_separation(client):
    a={'face_shape':'둥근형','body_shape':'통통형','undertone':'웜','preferred_fit':'루즈핏'}
    assert client.put('/api/profile',json=a,headers=headers()).status_code==200
    assert client.get('/api/profile',headers=headers()).json()==a
    assert client.get('/api/profile',headers=headers('b')).json()['body_shape']=='미선택'


def test_picture_ownership_and_logout(client,store):
    import base64
    raw=b'\x89PNG\r\n\x1a\n'+b'0'*20
    payload='data:image/png;base64,'+base64.b64encode(raw).decode()
    response=client.post('/api/uploads',json={'data':payload},headers=headers())
    assert response.status_code==201
    path=response.json()['image_url']
    assert client.get(path,headers=headers()).content==raw
    assert client.get(path,headers=headers('b')).status_code==404
    assert client.get(path).status_code==401
    assert client.get(path,headers=headers()).headers['cache-control']=='no-store'
    assert client.post('/api/auth/logout',headers=headers()).status_code==200
    assert client.get(path,headers=headers()).status_code==401


def test_private_photo_cannot_be_reused_by_b(client,store):
    store['photos']['abc.png']=2
    body={'name':'내 옷','category_id':4,'color_id':5,'style_id':1,'season':'가을','image_url':'/uploads/abc.png'}
    assert client.post('/api/wardrobe/custom',json=body,headers=headers('b')).status_code==403


def test_other_users_item_cannot_be_added(client,store):
    store['items'][42]={'id':42,'owner_user_id':2}
    assert client.post('/api/wardrobe',json={'item_id':42},headers=headers('b')).status_code==404
    assert not store['wardrobe']


def test_origin_and_admin(client):
    assert client.post('/api/auth/logout',headers={'Origin':'https://other.test'}).status_code==403
    assert client.post('/api/items',json={},headers=headers()).status_code==403


def test_link_is_single_use_cookie_and_existing_data_preserved(client,store,monkeypatch):
    captured=[];monkeypatch.setattr(auth,'send_link',lambda email,token:captured.append((email,token)))
    assert client.post('/api/auth/request',headers=headers(),json={'email':'new@example.test','nickname':'새 회원'}).status_code==200
    assert len(captured)==1
    token=captured[0][1];assert token not in store['links']
    first=client.post('/api/auth/verify',headers=headers(),json={'token':token})
    assert first.status_code==200
    cookie=first.headers['set-cookie'].lower();assert 'httponly' in cookie and 'samesite=lax' in cookie
    second=client.post('/api/auth/verify',headers=headers(),json={'token':token})
    assert second.status_code==400
    assert store['users'][2]['email']=='a@example.test'


def test_invalid_inputs_and_unconsented_ai(client):
    assert client.put('/api/profile',headers=headers(),json={'body_shape':'anything'}).status_code==400
    assert client.post('/api/vision/analyze',headers=headers(),json={'kind':'face','consent':False}).status_code==400
    assert client.post('/api/uploads',headers=headers(),json={'data':'data:image/png;base64,aGVsbG8='}).status_code==400
    assert client.post('/api/outfits/recommend',headers=headers(),json={'season':'가을','style':'미니멀','budget':-1}).status_code==400


def test_history_sql_scoped_to_current_user(client,store):
    store['history']=[{'id':1,'user_id':2,'payload':'[]','created_at':'2026-10-22T10:00:00'},{'id':2,'user_id':3,'payload':'[]','created_at':'2026-10-22T10:00:00'}]
    assert [r['id'] for r in client.get('/api/outfits/history',headers=headers('b')).json()]==[2]


def test_recommendation_owned_zero_budget_accessories_and_user_scope(monkeypatch):
    calls=[]
    rows=[{'id':i+1,'name':name,'price':50000,'is_owned':1,'category_name':name,'color_name':'블랙'} for i,name in enumerate(recommend.CORE+recommend.OPTIONAL)]
    def query(sql,values=(),connection=None):
        calls.append((sql,values));return rows if len(calls)==1 else [{'score':50}]
    monkeypatch.setattr(db,'query',query)
    result=recommend.recommend(22,'가을','미니멀',0,profile={'face_shape':'둥근형','body_shape':'통통형','undertone':'쿨','preferred_fit':'루즈핏'})
    assert result[0]['purchase_total']==0 and result[0]['owned_count']==10
    assert calls[0][1]==(22,22,'가을','미니멀')
    assert calls[1][1]==('가을','미니멀')
    assert any('편안한 핏' in reason for reason in result[0]['personalization'])


def test_mobile_manifest_icons_and_private_cache_exclusion(client):
    config=client.get('/api/mobile/config').json()
    assert config=={'base_url':'http://localhost:3000','secure':False,'loopback':True}
    manifest=client.get('/manifest.webmanifest')
    assert manifest.status_code==200
    assert manifest.json()['display']=='standalone'
    for icon in manifest.json()['icons']:
        assert client.get(icon['src']).status_code==200
    sw=client.get('/sw.js')
    assert sw.status_code==200 and sw.headers['cache-control']=='no-cache'
    assert "url.pathname.startsWith('/api/')" in sw.text
    assert "url.pathname.startsWith('/uploads/')" in sw.text
    assert client.get('/mobile.html').status_code==200


def test_mobile_url_setup_preserves_secrets(monkeypatch,tmp_path):
    import mobile_setup
    monkeypatch.setattr(mobile_setup,'ROOT',tmp_path)
    env=tmp_path/'.env';env.write_text('DB_PASSWORD=keep_this_value\nAPP_BASE_URL=http://localhost:3000\nSMTP_PASSWORD=keep_this_too\n')
    mobile_setup.configure('http://192.168.0.10:3000')
    text=env.read_text()
    assert 'DB_PASSWORD=keep_this_value' in text and 'SMTP_PASSWORD=keep_this_too' in text
    assert "APP_BASE_URL='http://192.168.0.10:3000'" in text
    with pytest.raises(ValueError):mobile_setup.configure('http://localhost:3000')
