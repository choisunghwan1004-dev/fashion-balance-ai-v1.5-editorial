"""Fashion Balance AI: Python/FastAPI server serving the built React application."""
from contextlib import asynccontextmanager
from io import BytesIO
from pathlib import Path
import json
import logging
import os
import re
import uuid
from dotenv import load_dotenv
from fastapi import FastAPI, Depends, HTTPException, Request, Response
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.exceptions import RequestValidationError
import qrcode
import qrcode.image.svg

ROOT = Path(__file__).resolve().parent
load_dotenv(ROOT/'.env')
import auth
import db
import recommend
import vision

SEASONS = ['봄','여름','가을','겨울']
STYLES = ['스마트 캐주얼','미니멀','클래식','스트리트']
PROFILE = {'face_shape':['미선택','둥근형','타원형','각진형','긴형','하트형'],
 'body_shape':['미선택','직선형','상체강조형','하체강조형','허리강조형','균형형','슬림형','보통형','통통형'],
 'undertone':['미선택','웜','쿨','뉴트럴'],'preferred_fit':['편안한핏','슬림핏','루즈핏']}
PRIVATE = ROOT/'private/uploads'
DIST = ROOT/'frontend/dist'


@asynccontextmanager
async def lifespan(app):
    auth.origin()
    # Never expose legacy uploaded photos through a static directory.
    if (ROOT/'public/uploads').exists() or (ROOT/'frontend/public/uploads').exists():
        raise RuntimeError('Run python migrate_photos.py before starting')
    PRIVATE.mkdir(parents=True,exist_ok=True)
    yield


app = FastAPI(title='Fashion Balance AI V2.1 — Python + React',lifespan=lifespan)


@app.middleware('http')
async def security(request: Request, call_next):
    if request.method not in ('GET','HEAD','OPTIONS') and request.headers.get('origin')!=auth.origin():
        return JSONResponse({'error':'요청 출처를 확인하세요.'},403)
    # Bound JSON photo requests before parsing, even for chunked requests.
    if request.method not in ('GET','HEAD','OPTIONS'):
        length = request.headers.get('content-length','0')
        if not length.isdigit() or int(length)>4_500_000:
            return JSONResponse({'error':'요청은 4.5MB 이하로 보내세요.'},413)
        body = bytearray()
        async for chunk in request.stream():
            body.extend(chunk)
            if len(body)>4_500_000:
                return JSONResponse({'error':'요청은 4.5MB 이하로 보내세요.'},413)
        request._body = bytes(body)
    response = await call_next(request)
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['Referrer-Policy'] = 'no-referrer'
    if request.url.path.startswith(('/api/','/uploads/')):
        response.headers['Cache-Control'] = 'no-store'
    return response


@app.exception_handler(HTTPException)
async def http_error(request, exc):
    return JSONResponse({'error':exc.detail},exc.status_code)


@app.exception_handler(RequestValidationError)
async def validation_error(request, exc):
    return JSONResponse({'error':'입력값을 확인하세요.'},400)


@app.exception_handler(Exception)
async def server_error(request, exc):
    logging.error('Request failed: %s',type(exc).__name__)
    return JSONResponse({'error':'서버 또는 DB 오류가 발생했습니다. DB 설정과 SQL 적용 여부를 확인하세요.'},500)


def ip(request):
    return request.client.host if request.client else 'unknown'


@app.get('/api/health')
def health():
    return {'ok':True,'backend':'Python / FastAPI','frontend':'React','database_checked':False}


@app.get('/api/mobile/config')
def mobile_config():
    from urllib.parse import urlsplit
    base = auth.origin()
    return {'base_url':base,'secure':base.startswith('https:'),'loopback':urlsplit(base).hostname in ('localhost','127.0.0.1','::1')}


@app.get('/api/auth/me')
def me(request: Request):
    return {'user':auth.identify(request)}


@app.get('/api/auth/qr')
def qr():
    image = qrcode.make(auth.origin()+'/login.html',image_factory=qrcode.image.svg.SvgPathImage)
    buffer = BytesIO()
    image.save(buffer)
    return Response(buffer.getvalue(),media_type='image/svg+xml')


@app.post('/api/auth/request')
def request_link(request: Request, data: dict):
    return auth.request_link(data,ip(request))


@app.post('/api/auth/verify')
def verify(request: Request, response: Response, data: dict):
    token = auth.verify_link(data.get('token'),ip(request))
    auth.set_session(response,token)
    return {'ok':True}


@app.post('/api/auth/logout')
def logout(request: Request, response: Response):
    token = request.cookies.get('fashion_session','')
    if token:
        db.query('DELETE FROM auth_sessions WHERE token_hash=%s',(auth.digest(token),))
    auth.set_session(response,'',0)
    return {'ok':True}


@app.get('/api/profile')
def profile(user=Depends(auth.required)):
    rows = db.query('SELECT face_shape,body_shape,undertone,preferred_fit FROM style_profiles WHERE user_id=%s',(user['id'],))
    return rows[0] if rows else {key:values[0] for key,values in PROFILE.items()}


@app.put('/api/profile')
def update_profile(data: dict, user=Depends(auth.required)):
    if any(data.get(key) not in values for key,values in PROFILE.items()):
        auth.fail(400,'체형·얼굴형·톤·핏 선택값을 확인하세요.')
    db.query('''INSERT INTO style_profiles(user_id,face_shape,body_shape,undertone,preferred_fit) VALUES(%s,%s,%s,%s,%s)
        ON DUPLICATE KEY UPDATE face_shape=VALUES(face_shape),body_shape=VALUES(body_shape),undertone=VALUES(undertone),preferred_fit=VALUES(preferred_fit)''',
        (user['id'],*(data[k] for k in PROFILE)))
    return {'saved':True,'profile':{k:data[k] for k in PROFILE}}


@app.get('/api/items')
def items():
    return db.query('''SELECT i.*,c.name category_name,co.name color_name,s.name style_name FROM fashion_items i
        JOIN categories c ON c.id=i.category_id JOIN colors co ON co.id=i.color_id JOIN styles s ON s.id=i.style_id
        WHERE i.active=1 AND i.owner_user_id IS NULL ORDER BY i.id DESC LIMIT 500''')


def number(value, minimum=0, maximum=2_147_483_647):
    try:
        n = int(value)
        if str(n)!=str(value) and not (isinstance(value,float) and value==n):
            raise ValueError()
        if isinstance(value,bool) or not minimum<=n<=maximum:
            raise ValueError()
        return n
    except (TypeError,ValueError,OverflowError):
        auth.fail(400,'숫자 입력값을 확인하세요.')


def garment(data):
    name = data.get('name')
    if not isinstance(name,str) or not 1<=len(name.strip())<=120 or data.get('season') not in SEASONS+['사계절']:
        auth.fail(400,'옷 이름·계절을 확인하세요.')
    return (name.strip(),number(data.get('category_id'),1,10),number(data.get('color_id'),1,6),number(data.get('style_id'),1,4),data['season'])


def url(value):
    if value and (not isinstance(value,str) or len(value)>500 or not re.match(r'^https?://',value,re.I)):
        auth.fail(400,'사진·쇼핑 URL을 확인하세요.')
    return value or None


@app.post('/api/items',status_code=201)
def add_item(data: dict, user=Depends(auth.admin)):
    fields = garment(data)
    result = db.query('INSERT INTO fashion_items(name,category_id,color_id,style_id,season,price,image_url,shop_url) VALUES(%s,%s,%s,%s,%s,%s,%s,%s)',
                      (*fields,number(data.get('price')),url(data.get('image_url')),url(data.get('shop_url'))))
    return {'id':result['insert_id']}


@app.get('/api/wardrobe')
def wardrobe(user=Depends(auth.required)):
    return db.query('''SELECT w.item_id,i.name,i.price,i.owner_user_id,i.image_url,c.name category_name,co.name color_name
        FROM wardrobe_items w JOIN fashion_items i ON i.id=w.item_id JOIN categories c ON c.id=i.category_id
        JOIN colors co ON co.id=i.color_id WHERE w.user_id=%s AND i.active=1
        AND (i.owner_user_id IS NULL OR i.owner_user_id=%s) ORDER BY w.id DESC''',(user['id'],user['id']))


@app.post('/api/wardrobe',status_code=201)
def add_wardrobe(data: dict, user=Depends(auth.required)):
    item_id = number(data.get('item_id'),1)
    if not db.query('SELECT id FROM fashion_items WHERE id=%s AND active=1 AND (owner_user_id IS NULL OR owner_user_id=%s)',(item_id,user['id'])):
        auth.fail(404,'상품 없음')
    db.query('INSERT IGNORE INTO wardrobe_items(user_id,item_id) VALUES(%s,%s)',(user['id'],item_id))
    return {'item_id':item_id}


@app.post('/api/wardrobe/custom',status_code=201)
def custom(data: dict, user=Depends(auth.required)):
    fields = garment(data)
    image_url = data.get('image_url') or None
    if image_url:
        if not isinstance(image_url,str) or not re.fullmatch(r'/uploads/[a-f0-9-]+\.(jpg|png|webp)',image_url):
            auth.fail(400,'사진 URL 오류')
        if not db.query('SELECT filename FROM private_photos WHERE filename=%s AND user_id=%s',(image_url.rsplit('/',1)[1],user['id'])):
            auth.fail(403,'본인 사진만 등록할 수 있습니다.')
    with db.transaction() as conn:
        result = db.query('INSERT INTO fashion_items(name,category_id,color_id,style_id,season,price,owner_user_id,image_url) VALUES(%s,%s,%s,%s,%s,0,%s,%s)',(*fields,user['id'],image_url),conn)
        db.query('INSERT INTO wardrobe_items(user_id,item_id) VALUES(%s,%s)',(user['id'],result['insert_id']),conn)
    return {'item_id':result['insert_id']}


@app.delete('/api/wardrobe/{item_id}')
def remove_wardrobe(item_id: int, user=Depends(auth.required)):
    number(item_id,1)
    with db.transaction() as conn:
        db.query('DELETE FROM wardrobe_items WHERE user_id=%s AND item_id=%s',(user['id'],item_id),conn)
        db.query('UPDATE fashion_items SET active=0 WHERE id=%s AND owner_user_id=%s',(item_id,user['id']),conn)
    return {'ok':True}


@app.post('/api/uploads',status_code=201)
def upload(data: dict, user=Depends(auth.required)):
    raw,extension = vision.decode_image(data.get('data'))
    name = str(uuid.uuid4())+'.'+extension
    PRIVATE.mkdir(parents=True,exist_ok=True)
    target = PRIVATE/name
    try:
        with target.open('xb') as file:
            file.write(raw)
        db.query('INSERT INTO private_photos(filename,user_id) VALUES(%s,%s)',(name,user['id']))
    except Exception:
        target.unlink(missing_ok=True)
        raise
    return {'image_url':'/uploads/'+name,'recognition':False}


@app.get('/uploads/{filename:path}')
def photo(filename: str, user=Depends(auth.required)):
    if not re.fullmatch(r'[a-f0-9-]+\.(jpg|png|webp)',filename):
        auth.fail(404,'사진 없음')
    if not db.query('SELECT filename FROM private_photos WHERE filename=%s AND user_id=%s',(filename,user['id'])) or not (PRIVATE/filename).is_file():
        auth.fail(404,'사진 없음')
    return FileResponse(PRIVATE/filename)


@app.get('/api/vision/status')
def vision_status(user=Depends(auth.required)):
    return {'ai_enabled':bool(os.getenv('OPENAI_API_KEY')),'model':os.getenv('OPENAI_VISION_MODEL','gpt-4.1-mini')}


@app.post('/api/vision/analyze')
def analyze(data: dict, user=Depends(auth.required)):
    return vision.analyze(data)


@app.get('/api/outfits/anchor-colors')
def anchor_colors(category: str, user=Depends(auth.required)):
    if category not in ['하의','아우터']:
        auth.fail(400,'카테고리 오류')
    rows = db.query('''SELECT DISTINCT co.name color FROM fashion_items i JOIN categories c ON c.id=i.category_id
        JOIN colors co ON co.id=i.color_id WHERE c.name=%s AND i.active=1
        AND (i.owner_user_id IS NULL OR i.owner_user_id=%s) ORDER BY co.name''',(category,user['id']))
    return [r['color'] for r in rows]


@app.post('/api/outfits/recommend')
def recommend_outfits(data: dict, user=Depends(auth.required)):
    category,color = data.get('anchorCategory'),data.get('anchorColor')
    if category not in [None,'하의','아우터'] or (color is not None and (not isinstance(color,str) or len(color)>40)) or bool(category)!=bool(color):
        auth.fail(400,'기준 아이템과 색상을 확인하세요.')
    if data.get('season') not in SEASONS or data.get('style') not in STYLES or data.get('source','mixed') not in ['mixed','wardrobe','shop']:
        auth.fail(400,'계절·스타일·추천 범위를 확인하세요.')
    result = recommend.recommend(user['id'],data['season'],data['style'],number(data.get('budget')),data.get('source','mixed'),category,color,profile(user))
    db.query('INSERT INTO recommendation_history(user_id,payload) VALUES(%s,%s)',(user['id'],json.dumps(result,ensure_ascii=False)))
    return result


@app.get('/api/outfits/history')
def history(user=Depends(auth.required)):
    return db.query('SELECT id,payload,created_at FROM recommendation_history WHERE user_id=%s ORDER BY id DESC LIMIT 30',(user['id'],))


@app.get('/api/seasonal-looks')
def seasonal(season: str='가을'):
    if season not in SEASONS:
        auth.fail(400,'계절 오류')
    return db.query('SELECT id,season,look_no,title,description,image_url,style_name,sample_only FROM seasonal_looks WHERE season=%s ORDER BY look_no LIMIT 2',(season,))


@app.get('/api/trends')
def trends():
    return db.query('SELECT t.*,s.name style_name FROM trends t JOIN styles s ON s.id=t.style_id ORDER BY t.year DESC,t.id DESC LIMIT 50')


# Private files, .env and source are never mounted. Only built React assets and reference images.
app.mount('/assets',StaticFiles(directory=DIST/'assets',check_dir=False),name='assets')
app.mount('/images',StaticFiles(directory=ROOT/'public/images'),name='images')
app.mount('/app-icons',StaticFiles(directory=DIST/'app-icons',check_dir=False),name='app-icons')


@app.get('/manifest.webmanifest')
def manifest():
    return FileResponse(DIST/'manifest.webmanifest',media_type='application/manifest+json')


@app.get('/sw.js')
def service_worker():
    return FileResponse(DIST/'sw.js',media_type='application/javascript',headers={'Cache-Control':'no-cache','Service-Worker-Allowed':'/'})


@app.get('/{page:path}')
def frontend(page: str):
    if page not in ['','index.html','wardrobe.html','profile.html','trends.html','admin.html','login.html','history.html','mobile.html']:
        auth.fail(404,'페이지 없음')
    if not (DIST/'index.html').is_file():
        return JSONResponse({'error':'React 빌드가 필요합니다. frontend 폴더에서 npm install 후 npm run build를 실행하세요.'},503)
    return FileResponse(DIST/'index.html')
