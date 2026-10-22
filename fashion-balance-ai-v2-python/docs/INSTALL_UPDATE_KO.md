# Windows 설치·업데이트 및 휴대폰 사용

## 1. 기존 자료부터 보존

기존 Node.js 서버를 Ctrl+C로 종료하세요. 기존 프로젝트 폴더와 MySQL `fashion_balance` DB를 백업합니다. MySQL Workbench에서는 Server → Data Export로 DB를 저장할 수 있습니다.
V2 ZIP은 **새 폴더**에 풉니다. 예: `C:\workspace\fashion-balance-ai-v2-python`. 기존 폴더에 덮어쓰지 않습니다.

V1.8 또는 V1.9의 `.env`를 새 폴더의 `run.py` 옆에 복사합니다. 비밀번호·API 키는 그대로 유지합니다. V1.9 사용자는 기존 `private\uploads` 폴더를 새 폴더의 같은 위치로 복사합니다. V1.8 사용자는 기존 `public\uploads`를 새 폴더의 같은 위치로 복사한 다음 아래 사진 이동 명령을 실행합니다. ZIP에는 사용자의 기존 DB·개인 사진·비밀번호가 포함되어 있지 않습니다.

## 2. MySQL SQL 적용 순서

MySQL Workbench에서 본인의 MySQL 서버에 접속합니다. File → Open SQL Script로 아래 파일을 열고 번개 버튼으로 실행합니다.

| 현재 상태 | SQL 적용 |
|---|---|
| V1.9 DB 적용 완료 | 추가 SQL 없음. V2는 동일한 DB 구조 사용 |
| V1.5~V1.7 DB | 기존 DB 백업 후 `upgrade_v1_6.sql` → `upgrade_v1_8.sql` → `upgrade_v1_9.sql` 순서. 이미 적용한 인증 확장은 재실행하지 않음 |
| V1.8 DB | `database/upgrade_v1_9.sql`을 **한 번만** 실행 |
| 처음 설치 | `database/schema.sql` → `database/seed.sql` → `database/seed_v1_4_demo.sql` → `database/upgrade_v1_9.sql` 순서 |

이전 버전 업그레이드 SQL을 모두 재실행하지 마세요. 기존 DB에 `seed.sql`을 다시 실행하면 샘플이 중복될 수 있습니다. `Duplicate column`이 나오면 이미 일부 적용됐을 수 있으니 멈추고 오류 내용을 확인합니다. SQL 기본 DB 이름은 `fashion_balance`입니다. 임의로 이름을 바꾸면 `.env`와 SQL의 `USE`도 맞춰야 합니다.
기존 사용자 1의 데모 데이터는 신규 가입자에게 자동 할당하지 않습니다. 기존 자료 귀속을 옮기려면 소유자 확인 후 별도 작업해야 합니다.

## 3. Python 준비

Python 3.11 이상(검증 환경 3.12)을 설치하고 아래를 실행합니다. VS Code에서 V2 폴더를 열고 터미널 → 새 터미널을 누르면 됩니다. `run.py`가 보이는 폴더에서 실행하세요.

```powershell
py -3 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

활성화 스크립트를 실행하지 않으므로 PowerShell 실행 정책을 바꿀 필요가 없습니다. `.env`를 아직 만들지 않은 **새 설치만** 아래를 실행합니다.

```powershell
Copy-Item .env.example .env
notepad .env
```

## 4. .env 설정

DB_HOST, DB_PORT, DB_USER, DB_PASSWORD, DB_NAME은 본인 MySQL 설정을 사용합니다. 비밀번호를 대화나 GitHub에 올리지 마세요.

```dotenv
APP_BASE_URL=http://localhost:3000
PORT=3000
NODE_ENV=development
SMTP_HOST=
SMTP_PORT=587
SMTP_SECURE=false
SMTP_USER=
SMTP_PASSWORD=
MAIL_FROM=
ADMIN_EMAILS=
```

SMTP 항목은 본인 메일 제공업체의 설정으로 채웁니다. 587 포트는 STARTTLS(`false`), 465 포트는 처음부터 TLS(`true`)입니다. 제공업체에 따라 앱 비밀번호가 필요합니다. 설정이 비어 있으면 인증 메일 발송이 503 안내로 종료되며 우회 로그인은 없습니다. ADMIN_EMAILS에는 상품 등록 권한을 줄 이메일을 쉼표로 구분해 입력합니다. 해당 사용자도 이메일 인증으로 가입해야 합니다.
OPENAI_API_KEY는 사진 AI 분석을 사용할 때만 설정합니다. 키가 없어도 수동 체형·옷 입력과 기기 내 색상 추정은 사용할 수 있습니다.

## 5. 사진 이동과 서버 실행

```powershell
.\.venv\Scripts\python.exe migrate_photos.py
.\.venv\Scripts\python.exe run.py
```

브라우저에서 `http://localhost:3000`을 엽니다. React 실행 빌드가 포함돼 있으므로 일반 사용에는 Node.js 설치가 필요하지 않습니다.
사진 이동은 V1.8 공용 폴더 사진을 비공개로 옮깁니다. 소유자가 불명확한 사진은 공개하지 않고 보관만 합니다. 여러 소유자가 연결되거나 같은 이름의 파일이 이미 있으면 중단하므로 확인 후 처리합니다. `public/uploads` 폴더가 남아 있으면 안전한 이전을 위해 서버가 시작되지 않습니다.

## 6. 휴대폰 연결

1. PC와 휴대폰을 같은 Wi-Fi에 연결합니다.
2. PC PowerShell에서 `ipconfig`를 실행해 사용하는 Wi-Fi의 IPv4 주소를 확인합니다.
3. 예를 들어 실제 주소가 `192.168.0.10`이면 `.env`를 `APP_BASE_URL=http://192.168.0.10:3000`으로 바꿉니다. 예시 주소를 그대로 사용하지 마세요.
4. 서버를 Ctrl+C로 종료하고 다시 `run.py`를 실행합니다.
5. PC에서도 `http://192.168.0.10:3000`으로 접속합니다. 인증 요청의 출처 검사가 있으므로 설정 주소와 실제 접속 주소를 일치시켜야 합니다.
6. 가입 화면의 QR을 휴대폰 카메라로 스캔하거나 휴대폰 주소창에 같은 주소를 입력합니다. Windows 방화벽은 신뢰하는 사설 네트워크에서만 **Python** 접속을 허용합니다.
7. 인증 메일 링크는 로그인할 휴대폰 브라우저에서 여세요. 메일 앱 안의 브라우저에서 열면 그 브라우저에만 로그인됩니다.

QR 자체는 가입 페이지 연결입니다. QR을 찍었다고 인증 없이 로그인되지는 않습니다. PC와 휴대폰은 각각 인증하면 같은 회원 자료를 볼 수 있습니다. 서로 다른 회원은 자료가 분리됩니다.
집 밖에서도 쓰려면 HTTPS 도메인을 연결한 Python 호스팅과 영구 MySQL·사진 저장소가 필요합니다. 이 ZIP은 자동으로 인터넷에 배포되지 않습니다. 서비스 운영 시 `NODE_ENV=production`, `APP_BASE_URL=https://실제주소`를 사용하며 Secure 쿠키를 적용합니다. 사진 저장 폴더는 백업·유지가 가능한 저장소를 사용하세요.

## 7. 화면 소스 수정 시에만 React 빌드

Node.js 22.12 이상 설치 후 아래를 실행합니다.

```powershell
cd frontend
npm ci
npm run build
cd ..
.\.venv\Scripts\python.exe run.py
```

`frontend/src/main.jsx`에서 React 상태·이벤트를, `src/templates/`에서 기존 화면 구조를, `src/style.css`에서 스타일을 수정합니다. 브라우저는 새 빌드 후 새로고침합니다. 개발 서버를 별도로 쓰기보다 먼저 Python 한 서버에서 동작을 확인하세요.

## 8. 확인과 복구

이메일 가입 → 인증 → 메인 이동 → 새로고침 로그인 유지 → 체형 선택·저장 → 사진 등록 → 코디 추천·이력 → 로그아웃 순서로 확인합니다. PC와 휴대폰 양쪽에서 확인하세요.
두 회원 A/B를 서로 다른 브라우저에서 만들고, B에서 A의 사진 주소를 열면 404가 나야 합니다. 로그아웃 후 개인 API는 401이어야 합니다.
문제가 생기면 새 서버를 종료하고 백업한 기존 프로그램과 DB·사진을 함께 복구합니다. `V1.9_ORIGINAL_BACKUP.zip`은 코드 비교·복구 참고용이며 개인 자료 백업을 대신하지 않습니다.


## V2.1 휴대폰 바로가기

상단 「휴대폰 연결」 또는 `/mobile.html`에서 QR·홈 화면 아이콘 안내를 볼 수 있습니다. `mobile_setup.py --url 실제주소`로 기존 비밀 설정을 보존하며 APP_BASE_URL만 바꿀 수 있습니다. 자세한 순서는 08_MOBILE_GUIDE.md를 참조하세요.
