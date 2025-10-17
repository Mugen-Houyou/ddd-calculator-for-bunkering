벙커링 DDD 계산기 — FastAPI + Jinja UI

개요
- 벙커링에서 DDD(Days after Delivery) 기준의 지급기일을 계산하기 위한 FastAPI 기반 클린 아키텍처 프로젝트입니다.
- Jinja 템플릿 기반의 웹 UI를 제공하며, 밝은 그라디언트/글라스 카드 스타일(참고: pdfm.asdv.cx/pdf-merger 톤)을 적용했습니다.

실행(개발)
- 가상환경 생성 및 의존성 설치:
  - python -m venv .venv
  - .venv\Scripts\activate
  - pip install -r requirements.txt
- 서버 시작:
  - uvicorn app.main:app --reload
- UI 열기: http://127.0.0.1:8000/

사용 방법 (웹 UI)
- 날짜 입력: 연/월/일 세그먼트(YYYY-MM-DD)로 입력합니다.
  - 연도 4자리 입력 후 자동으로 월로 포커스 이동, 월 2자리 후 일로 이동
  - 제출 시 유효성 검증 후 ISO 형식으로 결합되어 서버로 전송
- Payment Term: 드롭다운(DDD/COD/CIA), 가용 너비를 채우도록 브라우저별 폭 처리(-webkit-fill-available, -moz-available)
- Days(for DDD): 동일 행(row)에 인라인으로 표시, DDD일 때만 활성화/표시
- Sticky Form: 계산 이후에도 입력값이 유지되어 수정이 편리합니다.

프로젝트 구조(클린 레이어링)
- app/
  - core/           - 설정, 앱 팩토리 헬퍼
  - api/            - FastAPI 라우터/의존성 (헬스 등)
  - web/            - 웹 라우터(Jinja 템플릿 렌더)
  - templates/      - Jinja 템플릿(`base.html`, `index.html`)
  - static/         - 정적 자원(CSS 등)
  - domain/         - 도메인 엔티티/값 객체(순수 파이썬)
  - use_cases/      - 애플리케이션 서비스(DDD 계산 등)
  - infrastructure/ - 외부 시스템 어댑터(필요 시)

엔드포인트
- GET /v1/health — 헬스 체크(준비 상태)
- GET / — 웹 UI(지급기일 계산 폼)
- POST /calculate — 폼 제출 처리(서버 측 계산)

디자인 메모
- Pretendard 폰트, 밝은 블루 톤 그라디언트 배경, 유리감 카드, pill 형태의 그라디언트 버튼 적용
- 드롭다운 폭: `#term_kind { width: 100%; -webkit-fill-available; -moz-available; }`

다음 단계
- 주말/공휴일 롤링 규칙, 말일 처리 등의 옵션 추가
- "30ddd" 단일 문자열 파싱 입력 모드 지원
- 도메인/유스케이스/라우터 단위 테스트 추가
