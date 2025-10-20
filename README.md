벙커링 DDD 계산기 — FastAPI + Jinja UI

## 개요
- 벙커링에서 DDD(Days after Delivery) 기준의 지급기일을 계산하기 위한 프로젝트입니다.
- Python FastAPI 기반 REST API, Jinja 템플릿 기반의 웹 UI를 제공하며, 밝은 그라디언트/글라스 카드 스타일을 적용했습니다.
- Google Calendar API를 통한 다국가 공휴일 조회 및 연도별 캐싱을 지원합니다.

## 실행(개발)
### 환경 설정
1. 가상환경 생성 및 의존성 설치:
   ```bash
   python -m venv .venv
   .venv\Scripts\activate  # Windows
   # source .venv/bin/activate  # macOS/Linux
   pip install -r requirements.txt
   ```

2. 환경 변수 설정 (`.env` 파일 생성):
   ```
   GOOGLE_CAL_API_KEY=your_google_api_key_here
   ```

3. 서버 시작:
   ```bash
   uvicorn app.main:app --reload
   ```

4. UI 열기: http://127.0.0.1:8000/

## 주요 기능
### 웹 UI
- **날짜 입력**: 연/월/일 세그먼트(YYYY-MM-DD)로 입력
  - 연도 4자리 입력 후 자동으로 월로 포커스 이동
  - 월 2자리 입력 후 일로 자동 이동
  - 클라이언트 측 유효성 검증

- **다국가 선택**: 태그 방식으로 여러 국가 선택 가능
  - 지원 국가: 한국, 일본, 중국, 싱가포르, UAE 등 30+ 국가

- **Payment Term**: DDD / COD / CIA 선택
  - DDD 선택 시 일수(Days) 입력 필드 활성화

- **옵션**:
  - ✅ 주말을 DDD에 포함 (체크 시 주말도 계산에 포함)
  - ✅ 공급당일을 1DDD로 포함 (체크 시 배송일을 첫날로 계산)

- **결과 표시**:
  - 계산된 결제일 표시
  - 달력 시각화 (배송일, 결제일, 제외된 주말/공휴일 표시)
  - 공휴일 상세 정보 (국가별 공휴일 이름)

### REST API
- 클라이언트-서버 분리 아키텍처
- JSON 요청/응답 형식
- Pydantic 모델 기반 검증

### 공휴일 조회
- Google Calendar API 통합
- 연도별 캐싱 (`.cache/holidays/{COUNTRY}_{YEAR}.json`)
- 캐시 만료 기간: 7일
- 다국가 공휴일 병합 지원

## 프로젝트 구조(클린 레이어링)
```
app/
├── core/              # 설정, i18n, 앱 팩토리
├── api/v1/routers/    # REST API 엔드포인트
│   ├── health.py      # 헬스 체크
│   └── calculate.py   # DDD 계산 API
├── web/               # 웹 UI 라우터 (Jinja 템플릿 렌더)
├── templates/         # Jinja 템플릿 (base.html, index.html)
├── static/            # 정적 자원 (CSS, JavaScript)
├── domain/            # 도메인 엔티티/값 객체 (순수 Python)
│   └── ddd/          # DDD 계산 도메인 로직
├── use_cases/         # 애플리케이션 서비스 (DDD 계산)
└── infrastructure/    # 외부 시스템 어댑터
    └── google_calendar_holiday_provider.py
```

## API 엔드포인트

### 웹 UI
- `GET /` — 웹 UI (지급기일 계산 폼)

### REST API
- `GET /api/v1/health` — 헬스 체크

- `POST /api/v1/calculate` — DDD 계산

  **요청 본문**:
  ```json
  {
    "delivery_date": "2025-10-20",
    "country_codes": ["KR", "SG"],
    "term_kind": "DDD",
    "days": 30,
    "skip_weekends": false,
    "skip_holidays": true,
    "include_delivery_as_day_one": true
  }
  ```

  **응답**:
  ```json
  {
    "country_codes": ["KR", "SG"],
    "delivery_date": "2025-10-20",
    "term_kind": "DDD",
    "days": 30,
    "due_date": "2025-11-18",
    "excluded_weekends": [],
    "excluded_holidays": ["2025-10-03", "2025-10-09"],
    "holiday_names": {
      "2025-10-03": {"KR": "National Foundation Day"},
      "2025-10-09": {"KR": "Hangeul Proclamation Day"}
    },
    "holidays_excluded": true
  }
  ```

## 디자인
- **폰트**: Pretendard (한글/라틴 최적화)
- **스타일**: 밝은 블루 톤 그라디언트 배경, 글라스모피즘 카드
- **반응형**: 모바일/태블릿/데스크톱 지원
- **다국어**: 한국어/영어 자동 감지 (Accept-Language 헤더)

## 캐싱 전략
- **방식**: 연도별 캐싱 (`{COUNTRY}_{YEAR}.json`)
- **위치**: `.cache/holidays/`
- **만료**: 7일 후 자동 invalidate
- **장점**: 같은 연도 요청 시 캐시 재사용으로 API 호출 최소화

## 다음 단계
- 말일 처리 규칙 추가
- 테스트 커버리지 확대 (도메인/유스케이스/라우터)
- 도커라이징
- CI/CD 파이프라인 구축
