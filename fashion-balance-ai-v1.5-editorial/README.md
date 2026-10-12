# Fashion Balance AI V1.1 — My Closet & Smart Shopping

## 핵심
- 내 옷장 상품은 추가 구매비용 **0원**. 쇼핑 카탈로그에서만 부족한 아이템을 선택하고 합계 계산.
- 모자·스카프·아우터·상의·하의·신발·가방·벨트·시계·주얼리 (10개 범주).
- 내 옷 직접 등록, 기존 카탈로그 상품을 내 옷장에 추가, 옷장 상품 제거.
- 추천 방식: `mixed`(내 옷 우선 + 쇼핑 보완), `wardrobe`(내 옷만), `shop`(쇼핑만).
- 코디별 내 옷 개수 / 구매할 상품 개수 / 추가 구매 총액 / 밸런스 점수 표시.
- 차분한 아이보리·베이지·세이지 그린 UI.

## DB 모델
- `fashion_items.owner_user_id IS NULL`: 쇼핑 카탈로그 상품 (상품 가격, URL 포함).
- `fashion_items.owner_user_id = 1`: 데모 사용자가 직접 등록한 개인 소장품. `price=0`.
- `wardrobe_items(user_id,item_id)`: 이미 보유한 상품 연결. 카탈로그 상품도 옷장에 넣으면 구매비용 0원.
- 다른 사용자에 대한 데이터 격리는 **미구현**. 데모 사용자 ID=1 고정.
- `trends`는 관리자가 넣은 샘플 점수이며 실시간 패션 트렌드 수집이 아님.

## 설치
1. Node.js 18+, MySQL 8.x 준비.
2. **신규 설치:** MySQL Workbench에서 `database/schema.sql` 실행 후 `database/seed.sql`을 한 번만 실행.
3. **이전 V1 통합형 업그레이드:** DB 백업 후 `database/upgrade_v1_1.sql`을 **한 번만** 실행. 기존 데이터를 유지하며 `owner_user_id` 컬럼을 추가합니다. 이미 컬럼이 있다면 재실행하지 마세요.
4. `.env.example`을 `.env`로 복사하여 MySQL 비밀번호 입력.
5. `npm install`, `npm start`.
6. http://localhost:3000 → 코디 추천, `/wardrobe.html` → 내 옷장, `/admin.html` → 쇼핑 카탈로그 상품 등록.

## API
- `GET /api/items`: 쇼핑 카탈로그 목록 (개인 소장품 제외)
- `POST /api/items`: 쇼핑 카탈로그 상품 등록 (인증 없는 데모 관리자)
- `GET /api/wardrobe`: 데모 사용자의 보유 의류 목록
- `POST /api/wardrobe` `{"item_id":1}`: 카탈로그 상품을 보유 의류로 등록
- `POST /api/wardrobe/custom` `{"name":"내 코트","category_id":3,"color_id":1,"style_id":1,"season":"가을"}`: 내 옷 직접 등록
- `DELETE /api/wardrobe/:itemId`: 보유 목록에서 제거 (개인 등록품은 비활성화)
- `POST /api/outfits/recommend` `{"season":"가을","style":"스마트 캐주얼","budget":150000,"source":"mixed"}`
- `GET /api/trends`: 관리자 입력 트렌드

## 계산 규칙
- `is_owned = wardrobe_items에 존재` → `purchase_price=0`.
- 쇼핑 상품 → `purchase_price=fashion_items.price`.
- `purchase_total = sum(purchase_price)`; 예산은 **추가 구매 금액**에만 적용.
- 필수 4개 범주(아우터·상의·하의·신발)가 충족되어야 결과 반환. 선택 범주는 예산 내에서 추가.
- 보유 의류 활용 수를 우선하여 최대 3개 추천. 색상/트렌드 점수는 V1.1 단순 휴리스틱이며 실제 AI 평가가 아님.

## 주의사항
- **로컬 학습용 데모입니다. 인터넷에 공개하지 마세요.** 사용자 로그인, 관리자 인증, 다중 사용자 격리, 사진 업로드, 실시간 상품 가격 검증, 실제 결제, 자동 패션 데이터 수집은 아직 없습니다.
- 가격 및 상품은 샘플이며 쇼핑 URL은 관리자가 등록한 주소만 표시됩니다.
- 직접 등록한 개인 옷의 구매 당시 가격이나 취득원가는 저장하지 않습니다. 추천에 필요한 추가 지출만 0원으로 계산합니다.
- 기존 `database/upgrade_from_v1.sql`은 구 V1 → V1 통합형 용도입니다. 이미 통합형인 경우에는 사용하지 마세요.
