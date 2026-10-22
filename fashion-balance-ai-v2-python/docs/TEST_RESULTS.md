# V2.1 검증 결과 · 2026-10-22

## 수행 결과

| 항목 | 결과 | 실제 검증 범위 |
|---|---|---|
| Python 문법 | 통과 | app/auth/db/recommend/vision/migrate_photos/run |
| Python 자동 테스트 | 17개 통과 | FastAPI TestClient, MySQL 응답은 모의 DB |
| React 프로덕션 빌드 | 성공 | 실행용 dist 포함 |
| 화면 크기 검사 | 32개 통과 | Chromium에서 8개 화면 × 320·390·768·1440px, 문서 전체 가로 넘침 없음 |
| 주요 조작 흐름 | 4개 통과 | 추천·채택, 체형 그림/선택 동기화·저장 팝업, 샘플 추가·사진 미리보기·직접 등록, 최소 입력 가입 폼 |
| 브라우저 오류 | 0건 | 위 모의 API 기반 검사 중 pageerror/console.error |
| 시각 확인 | 수행 | PC·휴대폰 크기 메인 화면, 기존 색상·이미지·한글 글꼴 확인 |
| npm audit --omit=dev | 알려진 취약점 0건 | 검사 시점 프런트엔드 운영 의존성 기준 |

Python 테스트에서는 비로그인 401, 다른 회원 사진 404, 다른 회원 사진 재사용 403, 다른 회원 상품 등록 차단, 체형/이력 사용자 분리, 로그아웃 후 세션 무효화, 인증 링크 한 번 소비, 쿠키 HttpOnly/SameSite, Origin·관리자 권한, 동의 없는 AI 요청 차단, 보유품 구매비용 0원과 액세서리 추천을 확인했습니다.
React 테스트는 **실제 빌드 파일을 Python 서버에서 제공**하고 API만 모의 응답으로 바꿔 화면과 이벤트 연결을 검사했습니다. 브라우저의 여러 화면 폭은 휴대폰 실기기 테스트를 대신하지 않습니다.
테스트 환경의 Starlette가 httpx 기반 TestClient에 폐기 예정 경고를 1건 출력합니다. 실행 실패는 아니며 서버의 HTTPX AI 호출과는 별개입니다.

## 미실행 항목

- 사용자의 실제 MySQL에 SQL 적용 및 기존 자료와의 통합.
- 실제 SMTP 이메일 발송·수신과 링크 인증 왕복.
- 실제 OpenAI 사진 분석 호출·요금/할당량 확인.
- iPhone Safari·Android Chrome 실기기 카메라, 메일 앱 브라우저, QR 촬영.
- 외부 도메인 HTTPS 배포·방화벽·집 밖 접속.

## 직접 확인할 순서

1. 설치 가이드에 따라 MySQL·SMTP·APP_BASE_URL을 설정합니다. 가입 → 인증 → 메인 이동 → 새로고침 로그인 유지 → 로그아웃을 확인합니다.
2. PC와 휴대폰에서 각각 사진 선택·촬영, 체형 그림 선택, 등록·저장 팝업, 코디 추천과 이력을 확인합니다.
3. 서로 다른 브라우저 A/B로 가입하고 B에서 A의 옷·사진·체형·이력이 보이지 않는지 확인합니다. A 사진 주소는 B에서 404, 비로그인에서 401이어야 합니다.

## 재실행

프로젝트 루트에서:

```powershell
.\.venv\Scripts\python.exe -m pytest -q tests
```

React 브라우저 검사는 별도 Playwright 설치가 필요합니다. Python 서버를 한 터미널에서 켠 뒤, 다른 터미널에서 다음을 실행합니다. API 모의 응답을 쓰므로 실제 회원 데이터 검증 용도로 사용하지 마세요.

```powershell
npm install --no-save playwright
npx playwright install chromium
node tests/browser.cjs
```

`tests/browser.cjs`의 기본 접속 주소는 `http://localhost:3000`입니다. 결과는 `browser-results.json`에 저장됩니다. 테스트 중 개인 자료나 인증 메일을 실제로 생성하지 않습니다.


V2.1에서는 모바일 주소/manifest/아이콘/서비스워커 응답과 개인 API·사진 캐시 제외, .env의 비밀번호를 보존하는 주소 설정 도구도 검사했습니다. Docker 구성 파일은 제공하지만 실제 Docker 기동과 MySQL 초기화는 이 환경에서 실행하지 않았습니다.
