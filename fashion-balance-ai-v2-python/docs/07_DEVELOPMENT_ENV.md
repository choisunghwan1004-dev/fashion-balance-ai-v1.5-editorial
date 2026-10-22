# 개발환경·개발자 안내

| 계층 | 구성 |
|---|---|
| 서버 | Python 3.11 이상 권장, 검증 환경 3.12 / FastAPI·Uvicorn |
| 화면 | React 19.3.1 / Vite 8.3.5 / JSX·CSS / 재빌드 시 Node.js 22.12 이상 |
| DB | MySQL 8 / PyMySQL / utf8mb4 |
| 인증 메일 | Python smtplib + TLS, SMTP 제공업체 계정 필요 |
| 사진 AI | 서버 HTTPX → OpenAI Responses API, 선택 설정 |
| 모바일 | 반응형 웹·Web App Manifest·Service Worker·홈 화면 아이콘 |
| 검사 | pytest + FastAPI TestClient / Playwright Chromium / 모의 DB·API |
| 에디터 | VS Code 사용 가능 |

일반 실행에는 포함된 frontend/dist를 사용하므로 Node.js가 없어도 Python으로 실행할 수 있습니다. React 화면 수정 후에는 npm ci → npm run build로 dist를 갱신해야 합니다. requirements.txt와 frontend/package-lock.json을 기준으로 의존성을 설치합니다.

.env는 run.py 옆에 위치합니다. DB_*·APP_BASE_URL·SMTP_*·MAIL_FROM·ADMIN_EMAILS·선택적 OPENAI_*를 설정합니다. NODE_ENV=production이면 HTTPS APP_BASE_URL이 필요합니다. 실제 포트와 접속 주소를 일치시킵니다.

frontend/public에는 공개 manifest·아이콘·서비스워커만 둡니다. private/uploads를 public이나 dist로 복사하지 않습니다. .env·사용자 사진·DB 백업·node_modules·가상환경을 Git에 추가하지 않습니다. 도커 이미지는 실행용 dist를 사용합니다.

V1.5 저장소 코드는 그대로 보존하고 최신 코드는 fashion-balance-ai-v2-python 폴더에 구분합니다. GitHub 저장소 이름에 V1.5가 있어도 최신 실행 폴더는 README의 V2.1 안내를 따릅니다.
