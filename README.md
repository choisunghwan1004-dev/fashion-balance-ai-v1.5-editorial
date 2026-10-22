# Fashion Balance AI — React + Python · PC·휴대폰

최신 버전은 **V2.1**이며 [fashion-balance-ai-v2-python](fashion-balance-ai-v2-python) 폴더에서 실행합니다. 기존 V1.5 코드는 원래 폴더에 보존했습니다.

- [최신 README·실행 방법](fashion-balance-ai-v2-python/README.md)
- [전체 자료 목록](fashion-balance-ai-v2-python/docs/00_DOCUMENT_INDEX.md)
- [휴대폰 실행·QR·홈 화면 아이콘](fashion-balance-ai-v2-python/docs/08_MOBILE_GUIDE.md)
- [Windows 설치·DB 업그레이드](fashion-balance-ai-v2-python/docs/INSTALL_UPDATE_KO.md)
- [Notion 프로젝트 정리](https://app.notion.com/p/40128cb9cfd781e3b356c7fbec7ed370?pvs=204)

화면은 React, 업무·인증·추천·사진·DB 처리는 Python/FastAPI, DB는 MySQL 8입니다. 실행용 React 빌드가 포함돼 있어 일반 실행에는 Python 서버 하나를 사용합니다.

휴대폰은 PC/운영 서버 주소에 접속합니다. 서버·MySQL이 켜져 있어야 하며 외부 접속·PWA 설치에는 실제 HTTPS 운영 환경을 구성해야 합니다. 실제 외부 도메인 배포는 아직 수행하지 않았습니다.

검증: Python 자동 테스트 17개, 화면 크기 검사 32개(8화면 × 4크기), 주요 조작 4개 통과. DB·이메일·AI·휴대폰 실기기 검증과 Docker 기동은 별도 인수검사가 필요합니다.
