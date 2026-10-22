"""V1.8/V1.9 recommendation rules ported to Python, including accessories and owned cost=0."""
import itertools
import math
import db

CORE = ['아우터', '상의', '하의', '신발']
OPTIONAL = ['모자', '스카프', '가방', '벨트', '시계', '주얼리']
NEUTRALS = set(['베이지', '화이트', '네이비', '브라운', '블랙', '그레이'])
WARM = set(['베이지', '브라운', '크림', '카키', '아이보리', '오렌지'])
COOL = set(['네이비', '그레이', '블루', '블랙', '화이트', '퍼플'])
FACE = {'둥근형':'각이 있는 모자·세로 라인 스카프를 시도해 보세요','타원형':'다양한 모자와 스카프를 시도해 보세요','각진형':'부드러운 소재의 모자·스카프를 시도해 보세요','긴형':'폭이 있는 스카프·챙이 있는 모자를 시도해 보세요','하트형':'부드러운 라인의 액세서리를 시도해 보세요'}
BODY = {'직선형':'레이어드로 실루엣에 변화를 줄 수 있어요','상체강조형':'하의에 포인트를 주는 스타일도 어울릴 수 있어요','하체강조형':'상의에 포인트를 주는 스타일도 어울릴 수 있어요','허리강조형':'허리선이 보이는 코디를 시도해 보세요','균형형':'원하는 실루엣을 자유롭게 선택해 보세요','슬림형':'레이어드나 볼륨감 있는 소재를 선택할 수 있어요','보통형':'다양한 핏을 비교하며 편한 스타일을 선택해 보세요','통통형':'편안한 핏과 원하는 실루엣을 우선해 보세요'}


def cost(item):
    return 0 if item['is_owned'] else int(item['price'])


def build(items, trend, profile):
    colors = {i['color_name'] for i in items}
    color_score = max(8, 25 - max(0, len(colors)-3)*5 - (0 if colors <= NEUTRALS else 4))
    owned = sum(bool(i['is_owned']) for i in items)
    score = min(100, color_score+20+20+math.floor(trend*.15+.5)+10+10+min(5, owned))
    reasons, bonus = [], 0
    if not profile:
        reasons.append('기본 색상·계절 규칙 적용')
    else:
        tone = profile['undertone']
        if tone != '미선택':
            palette = WARM if tone == '웜' else COOL if tone == '쿨' else WARM | COOL
            hits = sum(i['color_name'] in palette for i in items)
            bonus = min(6, hits*2)
            reasons.append(f'{tone} 톤 선호 팔레트 {hits}개 반영')
        if profile['face_shape'] in FACE:
            reasons.append(FACE[profile['face_shape']])
        if profile['body_shape'] in BODY:
            reasons.append(BODY[profile['body_shape']])
        reasons.append('선호 핏: '+profile['preferred_fit'])
    total = sum(cost(i) for i in items)
    return dict(personalization=reasons, items=[dict(i, purchase_price=cost(i), source='wardrobe' if i['is_owned'] else 'shop') for i in items],
                purchase_total=total, total_price=total, owned_count=owned, shopping_count=len(items)-owned,
                shopping_items=[i['id'] for i in items if not i['is_owned']], balance_score=min(100,score+bonus), trend_score=trend)


def recommend(user_id, season, style, budget, source='mixed', anchorCategory=None, anchorColor=None, profile=None):
    rows = db.query('''SELECT i.id,i.name,i.price,i.image_url,i.shop_url,i.owner_user_id,
        c.name category_name,co.name color_name,CASE WHEN w.item_id IS NOT NULL THEN 1 ELSE 0 END is_owned
        FROM fashion_items i JOIN categories c ON c.id=i.category_id JOIN colors co ON co.id=i.color_id
        JOIN styles s ON s.id=i.style_id LEFT JOIN wardrobe_items w ON w.item_id=i.id AND w.user_id=%s
        WHERE i.active=1 AND (i.owner_user_id IS NULL OR i.owner_user_id=%s)
        AND (i.season=%s OR i.season='사계절') AND s.name=%s
        ORDER BY is_owned DESC,i.price ASC,i.id ASC LIMIT 500''', (user_id,user_id,season,style))
    rows = [i for i in rows if (source=='mixed' or (source=='wardrobe' and i['is_owned']) or (source=='shop' and not i['is_owned']))]
    groups = {c: [i for i in rows if i['category_name']==c] for c in CORE+OPTIONAL}
    if any(not groups[c] for c in CORE):
        return []
    if anchorCategory:
        groups[anchorCategory] = [i for i in groups[anchorCategory] if i['color_name']==anchorColor]
        if not groups[anchorCategory]:
            return []
    trends = db.query('SELECT t.score FROM trends t JOIN styles s ON s.id=t.style_id WHERE t.season=%s AND s.name=%s ORDER BY t.year DESC,t.id DESC LIMIT 1',(season,style))
    trend = int(trends[0]['score']) if trends else 50
    sort = lambda i: (-int(bool(i['is_owned'])),cost(i))
    candidates = []
    for combination in itertools.product(*(sorted(groups[c],key=sort)[:4] for c in CORE)):
        items = list(combination)
        total = sum(cost(i) for i in items)
        if total > budget:
            continue
        for category in OPTIONAL:
            extra = next((i for i in sorted(groups[category],key=sort) if i['is_owned'] or (category=='가방' and total+cost(i)<=budget)),None)
            if extra:
                items.append(extra)
                total += cost(extra)
        candidates.append(build(items,trend,profile))
    candidates.sort(key=lambda o:(-o['owned_count'],-o['balance_score'],o['purchase_total']))
    selected, seen = [], set()
    for outfit in candidates:
        signature = tuple(i['id'] for i in outfit['items'] if i['category_name'] in CORE)
        if signature not in seen:
            selected.append(outfit)
            seen.add(signature)
        if len(selected)==2:
            break
    return selected
