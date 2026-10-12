# Fashion Balance AI V1.4 — 사계절 통합 테스트

## 실행
1. 기존 V1.3 MySQL DB 백업. 신규 설치라면 `database/schema.sql` → `database/seed.sql` 순서 실행.
2. 기존 V1.3 DB가 있다면 신규 schema/seed는 실행하지 않아도 됩니다.
3. MySQL Workbench에서 `database/seed_v1_4_demo.sql` 실행 (기존 데이터 삭제 없음).
4. `.env.example`을 `.env`로 복사하고 DB_PASSWORD 설정.
5. `npm install` → `npm start` → http://localhost:3000

## 테스트
- 계절 4개 × 스타일 4개, 바지 또는 겉옷 색상을 선택 → 추천 버튼 클릭
- 결과 위에 실제 적용 조건 확인
- LOOK 1/2의 `이 코디 채택하기` 버튼을 누르면 선택 테두리와 완료 메시지 표시 (DB 저장 아님)
- 내 옷장: http://localhost:3000/wardrobe.html
- 내 옷은 추가 구매비용 0원, 미보유는 샘플 가격으로 계산
- 쇼핑 링크는 29CM의 **검색 결과** 페이지이며 특정 실물 상품, 가격, 재고를 보증하지 않습니다.

## 데이터
- `seed_v1_4_demo.sql`: 4계절 × 4스타일 × 12개 = **192개 가상 상품**
- 가상 내 옷장: 32개 핵심 의류 + 액세서리 샘플
- 기존 seasonal_looks 사진 8장은 이전 V1.3에서 유지. 사진은 샘플 스타일 이미지로 상품과 1:1 매칭 아님.
- 공개 쇼핑몰 웹페이지를 확인해 검색 링크만 연결. 판매처의 사진·상품 설명을 무단 복제하지 않음.
- 운영용: 로그인/권한, 상품 API 계약, 가격 갱신, 이미지 이용권 확보 필요.
