# 배포 구성 — 실행 파일과 운영 배포 구분

## 현재 제공 범위

PC/같은 Wi-Fi에서 실행 가능한 소스와 React 빌드를 제공합니다. Dockerfile·compose.yaml은 새 MySQL 인스턴스와 사진 영구 볼륨을 함께 구성하는 배포용 파일입니다. 이 환경에서 Docker 기동·실제 DB·SMTP·HTTPS 도메인 배포는 실행하지 않았습니다.

## 새 Docker 환경에서 실행

Docker Engine/Compose 또는 Docker Desktop을 준비합니다. .env에 서로 다른 충분한 DB_PASSWORD, MYSQL_ROOT_PASSWORD를 설정하고 APP_BASE_URL·SMTP·MAIL_FROM·ADMIN_EMAILS를 채웁니다. Docker 내부 앱 사용자는 fashion_app, DB는 fashion_balance입니다.

```powershell
docker compose up -d --build
docker compose logs --tail 80 app
```

초기화 SQL은 MySQL 볼륨이 비어 있는 첫 실행에만 적용됩니다. 기존 사용자의 DB를 자동 복사하거나 덮어쓰지 않습니다. 기존 DB는 백업·복구 절차를 계획해 이전해야 합니다. MySQL 포트는 외부에 노출하지 않고 앱 포트 3000만 엽니다.

## 외부 HTTPS 운영

운영 호스트·실제 도메인을 지정하고 DNS를 연결한 뒤 호스트의 TLS 리버스 프록시로 443 → 앱 3000을 연결합니다. APP_BASE_URL=https://실제도메인, NODE_ENV=production으로 설정하고 앱을 다시 시작합니다. 프록시/인증서는 운영 호스트 환경에 맞춰 구성해야 하며 이 프로젝트가 임의 도메인이나 인증서를 발급하지 않습니다.
원본 APP_BASE_URL과 접속 Origin이 다르면 변경 요청이 거절됩니다. 포트/주소를 바꿨다면 QR과 홈 화면 바로가기도 새 주소로 다시 추가합니다.

## 영구 자료와 갱신

fashion_mysql 볼륨은 DB, fashion_photos 볼륨은 개인 사진입니다. 컨테이너 교체 시 유지하고 정기 백업합니다. 앱 이미지에는 키·개인 사진·DB 백업을 포함하지 않습니다. .env는 도커 빌드 대상에서 제외합니다.
코드를 갱신해 docker compose up -d --build를 실행하기 전에 백업과 테스트를 수행합니다. 이전 소스와 해당 시점 DB/사진을 함께 복구할 수 있어야 합니다. 변경 전후의 실제 커밋·테스트 근거를 Notion에 기록합니다.

공식 참고: https://docs.docker.com/compose/ / https://docs.docker.com/guides/databases/ / https://developer.mozilla.org/en-US/docs/Web/API/Service_Worker_API
