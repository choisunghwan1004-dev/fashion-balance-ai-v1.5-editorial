# Fashion Balance AI V1.2 — 계절별 2가지 코디 미리보기

기존 V1.1의 개인 옷장 우선 / 쇼핑 보완 추천을 유지하고, 계절 선택 시 MySQL `seasonal_looks`에 저장된 두 개의 샘플 코디 이미지를 표시합니다.

## 기존 V1.1 업그레이드
1. 프로젝트 폴더를 별도로 백업합니다.
2. 새 V1.2 파일을 사용하고 `.env`에 DB 연결값을 입력합니다.
3. MySQL Workbench에서 `database/upgrade_v1_2.sql`을 **한 번** 실행합니다. 기존 테이블과 데이터는 삭제하지 않습니다.
4. `npm install` 후 `npm start` 실행, `http://localhost:3000` 접속.

## 신규 설치
`database/schema.sql`을 실행하고 `database/seed.sql`을 한 번 실행합니다. `upgrade_v1_2.sql`은 신규 설치에서는 실행하지 않습니다.

## 확인할 사항
- 메인 화면에서 계절을 바꾸면 DB의 샘플 코디 사진 2개가 즉시 변경됩니다.
- `POST /api/outfits/recommend`는 기존과 같이 옷장 상품의 추가 구매비용을 0원으로 계산합니다.
- `GET /api/seasonal-looks?season=봄`으로 샘플 사진 메타데이터를 확인할 수 있습니다.
- 사진은 AI 생성 UI 시안에서 발췌한 **스타일 참고용**입니다. DB 상품의 실제 사진이 아닙니다.
- 여름/겨울 이미지는 임시 참고 사진이므로 해당 계절의 실제 착장 사진으로 교체해야 합니다.
- 로그인 인증 없이 테스트 사용자 1번을 사용하므로 인터넷에 공개하지 마세요.
