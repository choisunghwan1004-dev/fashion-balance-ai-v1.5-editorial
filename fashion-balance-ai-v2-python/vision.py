"""Optional consent-based photo analysis; uploaded analysis photos are not retained."""
import base64
import json
import os
import re
import httpx
from auth import fail

OPTIONS = {
 'category':['모자','스카프','아우터','상의','하의','신발','가방','벨트','시계','주얼리','알 수 없음'],
 'color':['베이지','화이트','네이비','브라운','블랙','그레이','알 수 없음'],
 'pattern':['무지','스트라이프','체크','도트','프린트','기타','알 수 없음'],
 'season':['봄','여름','가을','겨울','사계절','알 수 없음'],
 'face_shape':['둥근형','타원형','각진형','긴형','하트형','미선택'],
 'body_shape':['직선형','상체강조형','하체강조형','허리강조형','균형형','미선택'],
}
FIELDS = {'garment':['category','color','pattern','season','name','confidence'],'face':['face_shape','confidence'],'body':['body_shape','confidence']}


def decode_image(data):
    if not isinstance(data,str) or len(data)>4300000:
        fail(400,'사진은 최대 3MB까지 가능합니다.')
    match = re.fullmatch(r'data:image/(jpeg|png|webp);base64,([A-Za-z0-9+/=]+)',data)
    if not match:
        fail(400,'JPG, PNG, WEBP 사진만 가능합니다.')
    try:
        raw = base64.b64decode(match[2],validate=True)
    except ValueError:
        fail(400,'사진 인코딩이 올바르지 않습니다.')
    if not 16<=len(raw)<=3*1024*1024:
        fail(400,'사진 용량을 확인하세요.')
    mime = match[1]
    valid = raw.startswith(b'\xff\xd8\xff') if mime=='jpeg' else raw.startswith(b'\x89PNG\r\n\x1a\n') if mime=='png' else raw[:4]==b'RIFF' and raw[8:12]==b'WEBP'
    if not valid:
        fail(400,'사진 파일 형식이 올바르지 않습니다.')
    return raw,'jpg' if mime=='jpeg' else mime


def analyze(data):
    kind = data.get('kind')
    if not isinstance(kind,str) or kind not in FIELDS or data.get('consent') is not True:
        fail(400,'분석 유형과 사진 전송 동의를 확인하세요.')
    decode_image(data.get('data'))
    if not os.getenv('OPENAI_API_KEY'):
        fail(503,'AI 사진 분석 API 키가 없습니다. 직접 선택과 기기 내 색상 추정은 이용할 수 있습니다.')
    fields = {k:OPTIONS[k] for k in FIELDS[kind] if k in OPTIONS}
    instruction = '패션 참고 분석이다. JSON 객체만 반환하라. 각 필드는 다음 선택지만 사용한다: '+json.dumps(fields,ensure_ascii=False)+'. confidence는 0~1. garment는 의류 종류/색상/계절/패턴과 한국어 name. face는 명확한 얼굴 윤곽만, body는 명확한 전신 의복의 시각적 실루엣만 분석한다. 불명확하면 미선택/알 수 없음. 나이·인종·건강·체중·신체 치수·미모는 추론하지 않는다.'
    try:
        response = httpx.post('https://api.openai.com/v1/responses',headers={'Authorization':'Bearer '+os.environ['OPENAI_API_KEY']},timeout=20,json={
            'model':os.getenv('OPENAI_VISION_MODEL','gpt-4.1-mini'),'store':False,'max_output_tokens':250,
            'input':[{'role':'user','content':[{'type':'input_text','text':instruction},{'type':'input_image','image_url':data['data']}]}]})
        if not response.is_success:
            fail(502,'AI 서비스 요청 실패. API 설정·사용 한도를 확인하세요.')
        text = ''.join(c.get('text','') for o in response.json().get('output',[]) for c in o.get('content',[]) if c.get('type')=='output_text')
        parsed = json.loads(re.sub(r'^```(?:json)?\s*|\s*```$','',text.strip()))
        result = {}
        for field in FIELDS[kind]:
            value = parsed.get(field)
            if field=='confidence':
                result[field] = min(1,max(0,float(value or 0)))
            elif field=='name':
                result[field] = str(value or '내 옷')[:80]
            else:
                result[field] = value if value in OPTIONS[field] else OPTIONS[field][-1]
        return {'result':result,'requires_confirmation':True,'stored':False}
    except (httpx.HTTPError,ValueError,TypeError,KeyError,AttributeError):
        fail(502,'AI 응답을 처리하지 못했습니다. 직접 선택해 주세요.')
