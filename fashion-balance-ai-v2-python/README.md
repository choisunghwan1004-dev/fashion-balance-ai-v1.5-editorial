# Fashion Balance AI V2.1 — React + Python

화면은 React, 인증·추천·사진·DB 처리는 Python/FastAPI로 전환한 버전입니다. MySQL 8과 기존 패션 디자인·이미지·세부 기능을 유지했습니다. PC와 휴대폰을 함께 지원하는 반응형 웹입니다. 한글 글꼴도 빌드에 포함해 외부 글꼴 서비스 연결 없이 표시합니다.

최신 문서 전체: [자료 목록](docs/00_DOCUMENT_INDEX.md) · [휴대폰 실행](docs/08_MOBILE_GUIDE.md) · [기획서](docs/01_PROJECT_PLAN.md) · [기능정의서](docs/02_FUNCTION_SPEC.md) · [화면설계서](docs/03_SCREEN_DESIGN.md) · [DB 사전](docs/04_DB_DICTIONARY.md)

## 처음 실행

압축을 푼 폴더에서 `docs/INSTALL_UPDATE_KO.md` 순서대로 DB와 `.env`를 설정하세요. React 빌드 결과가 포함되어 있어 **일반 실행에는 Node.js가 필요하지 않습니다.** 화면 소스를 수정해 다시 빌드할 때만 Node.js가 필요합니다.

```powershell
py -3 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
Copy-Item .env.example .env
notepad .env
.\.venv\Scripts\python.exe migrate_photos.py
.\.venv\Scripts\python.exe run.py
```

`http://localhost:3000` 접속. 기존 `.env`가 있다면 복사 명령으로 덮어쓰지 말고 기존 파일을 새 폴더에 복사하세요. DB SQL 적용이 먼저 필요합니다.

## 유지·전환한 기능

| 영역 | 구현 |
|---|---|
| 화면 | 기존 색상·레이아웃·사진·메뉴를 React 요소로 렌더링. 입력·선택·사진·추천 결과는 React 상태로 관리 |
| 추천 | Python으로 사계절·스타일·예산·기준 옷·색상·옷장 우선 규칙 이식. 최대 두 코디, 액세서리, 추가 구매 0원 계산 보존 |
| 체형 | 슬림·보통·통통 그림 선택과 다른 실루엣 선택을 양방향 동기화 |
| 사진 | 기기 내 색상 추정, 미리보기, 수동 입력, 동의 후 AI 의류·얼굴형·실루엣 분석 |
| 회원 | QR 가입 페이지, 닉네임·이메일 인증 링크, 30일 세션 유지·로그아웃 |
| 개인 자료 | 옷장·사진·프로필·추천 이력 사용자별 권한 검사. 샘플과 개인 소유자 구분 |
| 관리자 | ADMIN_EMAILS로 인증된 관리자만 공용 상품 등록 |
| 저장 | 완료 팝업에서 메인으로 이동 또는 계속 관리 선택 |
| 기기 | PC·태블릿·휴대폰 반응형, 큰 터치 영역·입력 글씨, 사진 선택과 별도 촬영 입력 |

얼굴·전신 분석 사진은 해당 분석 기능에서 서버 파일/DB에 보관하지 않습니다. 의류 사진은 등록 시 비공개 폴더에 저장됩니다. AI 결과는 추정값이며 사용자가 확인한 뒤 저장합니다.
기존의 '코디 채택'은 화면 내 선택을 유지합니다. 추천 이력은 DB에 저장되지만 채택 여부를 새로 DB에 저장하는 기능을 임의 추가하지 않았습니다.

## 구성

- `app.py`: API와 빌드된 React 화면 제공.
- `auth.py`: 인증 메일·일회용 링크·세션·요청 제한.
- `recommend.py`: Python 코디 계산.
- `vision.py`: 이미지 검증·선택적 AI 분석.
- `db.py`: MySQL 연결·트랜잭션·바인딩 SQL.
- `frontend/src/main.jsx`: React 상태와 사용자 흐름.
- `frontend/src/templates/`: 기존 화면 구조를 보존한 로컬 레이아웃. 서버/사용자 입력 HTML을 실행하는 용도가 아닙니다.
- `frontend/src/style.css`: 기존 CSS와 기기별 보강.
- `frontend/dist/`: 실행용 React 빌드.
- `public/images/`: 기존 참고 이미지·체형 그림.
- `database/`: 기존 SQL와 V1.9 인증 테이블 변경 SQL.
- `AGENTS.md`, `docs/DEVELOPMENT_GUIDELINES_KO.md`: PC·휴대폰 필수 지원 지침.
- `V1.9_ORIGINAL_BACKUP.zip`: 전환 전 전체 코드 보존본. 새 실행에 사용하지 않습니다.

## 화면 수정·빌드

Node.js 22.12 이상을 사용합니다. React는 Python으로 작성하는 라이브러리가 아니므로 화면 소스는 JSX, 핵심 서버 소스는 Python으로 구분했습니다. Express 서버는 새 실행에 사용하지 않습니다.

```powershell
cd frontend
npm ci
npm run build
cd ..
.\.venv\Scripts\python.exe run.py
```

## 문서·검증

- [설치·업데이트 및 휴대폰 연결](docs/INSTALL_UPDATE_KO.md)
- [기능·API 연결](docs/API_MAP.md)
- [DB ERD](docs/ERD.md)
- [개발지침](docs/DEVELOPMENT_GUIDELINES_KO.md)
- [검증 결과와 미실행 항목](docs/TEST_RESULTS.md)
- [변경 이력](CHANGELOG.md)

```powershell
.\.venv\Scripts\python.exe -m pytest -q tests
```

Python 테스트의 DB 응답은 모의 DB입니다. 실제 MySQL·SMTP·외부 AI와 실기기 테스트는 따로 확인해야 합니다.

기술 참고: [React 상태](https://react.dev/learn/preserving-and-resetting-state), [React createRoot](https://react.dev/reference/react-dom/client/createRoot), [FastAPI 테스트](https://fastapi.tiangolo.com/tutorial/testing/).
