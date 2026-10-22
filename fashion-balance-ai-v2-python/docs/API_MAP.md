# React ↔ Python ↔ MySQL 연결

React 화면은 브라우저에서 `/api/...`로 요청하고 Python이 권한을 확인한 후 MySQL을 조회·저장합니다. 빌드된 React와 API를 같은 Python 서버에서 제공하므로 일반 실행은 1개 서버입니다.

| 화면·기능 | API | 권한·자료 |
|---|---|---|
| 가입 QR·상태 | GET /api/auth/qr, /api/auth/me | 가입 주소/현재 세션 |
| 인증 요청 | POST /api/auth/request | 닉네임·이메일, 시간당 요청 제한 |
| 링크 확인 | POST /api/auth/verify | 만료·일회용 토큰, 트랜잭션으로 세션 생성 |
| 로그아웃 | POST /api/auth/logout | 해당 세션 삭제 |
| 체형·얼굴형·톤·핏 | GET/PUT /api/profile | 본인 style_profiles |
| 샘플·쇼핑 목록 | GET /api/items | owner_user_id NULL 상품 |
| 관리자 상품 | POST /api/items | 인증 사용자 + ADMIN_EMAILS |
| 내 옷 목록·추가 | GET/POST /api/wardrobe | 본인 wardrobe_items, 개인 상품은 본인 소유만 |
| 직접 등록 | POST /api/wardrobe/custom | 본인 fashion_items, 사진 소유권 확인 |
| 제거 | DELETE /api/wardrobe/{id} | 본인 옷장만 삭제, 본인 개인 상품만 비활성화 |
| 사진 저장 | POST /api/uploads | 파일 시그니처·용량 검사, private_photos 소유자 기록 |
| 사진 표시 | GET /uploads/{filename} | 로그인과 파일 소유권, 다른 회원은 404 |
| 사진 분석 | GET /api/vision/status, POST /api/vision/analyze | 로그인, 동의 필요, API 키는 서버만 보관 |
| 기준 색상 | GET /api/outfits/anchor-colors | 공용 상품 + 본인 개인 상품 |
| 추천 | POST /api/outfits/recommend | 본인 옷장·프로필 반영, 이력 저장 |
| 이력 | GET /api/outfits/history | 본인 최근 30회 |
| 사계절 사진 | GET /api/seasonal-looks | 참고 샘플 2개 |
| 트렌드 | GET /api/trends | 관리자 입력 예시 자료 |
| 서버 상태 | GET /api/health | 프로세스 응답 여부. DB 점검을 의미하지 않음 |

인증 토큰은 DB에 SHA-256 해시로만 저장합니다. 변경 요청은 APP_BASE_URL과 Origin이 일치해야 합니다. 비밀 파일과 Python 원본·백업 ZIP은 웹에서 내려받을 수 없습니다.
이메일 인증 링크는 15분, 세션은 30일입니다. 만료 링크·세션·요청제한 레코드 정리는 운영 시 정기 작업으로 설정할 수 있습니다. 자동 정리 스케줄은 이번 ZIP에서 설정하지 않았습니다.
