from datetime import date, datetime, timedelta
from typing import Optional
import json
import os
from pathlib import Path

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from app.infrastructure.holiday_provider import HolidayProvider


class GoogleCalendarHolidayProvider(HolidayProvider):
    """Google Calendar API를 사용하여 공휴일을 조회하는 구현체"""

    # Google Calendar의 공휴일 캘린더 ID 매핑
    CALENDAR_IDS = {
        # 아시아
        "KR": "en.south_korea#holiday@group.v.calendar.google.com",
        "JP": "en.japanese#holiday@group.v.calendar.google.com",
        "CN": "en.china#holiday@group.v.calendar.google.com",
        "HK": "en.hong_kong#holiday@group.v.calendar.google.com",
        "TW": "en.taiwan#holiday@group.v.calendar.google.com",
        "SG": "en.singapore#holiday@group.v.calendar.google.com",
        "MY": "en.malaysia#holiday@group.v.calendar.google.com",
        "TH": "en.th#holiday@group.v.calendar.google.com",
        "ID": "en.indonesian#holiday@group.v.calendar.google.com",
        "PH": "en.philippines#holiday@group.v.calendar.google.com",
        "VN": "en.vietnamese#holiday@group.v.calendar.google.com",
        "IN": "en.indian#holiday@group.v.calendar.google.com",
        # 중동
        "UAE": "en.ae#holiday@group.v.calendar.google.com",
        "SA": "en.sa#holiday@group.v.calendar.google.com",
        # 유럽
        "GB": "en.uk#holiday@group.v.calendar.google.com",
        "DE": "en.german#holiday@group.v.calendar.google.com",
        "FR": "en.french#holiday@group.v.calendar.google.com",
        "IT": "en.italian#holiday@group.v.calendar.google.com",
        "ES": "en.spanish#holiday@group.v.calendar.google.com",
        "NL": "en.dutch#holiday@group.v.calendar.google.com",
        "BE": "en.be#holiday@group.v.calendar.google.com",
        "GR": "en.greek#holiday@group.v.calendar.google.com",
        "NO": "en.norwegian#holiday@group.v.calendar.google.com",
        "SE": "en.swedish#holiday@group.v.calendar.google.com",
        "DK": "en.danish#holiday@group.v.calendar.google.com",
        "FI": "en.finnish#holiday@group.v.calendar.google.com",
        "PL": "en.polish#holiday@group.v.calendar.google.com",
        "RU": "en.russian#holiday@group.v.calendar.google.com",
        # 아메리카
        "US": "en.usa#holiday@group.v.calendar.google.com",
        "CA": "en.canadian#holiday@group.v.calendar.google.com",
        "MX": "en.mexican#holiday@group.v.calendar.google.com",
        "BR": "en.brazilian#holiday@group.v.calendar.google.com",
        "AR": "en.ar#holiday@group.v.calendar.google.com",
        "CL": "en.cl#holiday@group.v.calendar.google.com",
        # 오세아니아
        "AU": "en.australian#holiday@group.v.calendar.google.com",
        "NZ": "en.new_zealand#holiday@group.v.calendar.google.com",
        # 아프리카
        "ZA": "en.sa#holiday@group.v.calendar.google.com",
    }

    # 캐시 만료 기간 (일주일)
    CACHE_EXPIRY_DAYS = 7

    def __init__(self, api_key: str, cache_dir: Optional[str] = None):
        """
        Args:
            api_key: Google API Key
            cache_dir: 캐시 파일을 저장할 디렉토리 경로 (기본값: .cache/holidays)
        """
        self.api_key = api_key
        self._service = None
        self._cache: dict[tuple[str, date, date], dict[date, str]] = {}

        # 캐시 디렉토리 설정
        if cache_dir is None:
            cache_dir = os.path.join(os.getcwd(), ".cache", "holidays")
        self.cache_dir = Path(cache_dir)

        # 캐시 디렉토리 생성
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def _get_service(self):
        """Google Calendar API 서비스 인스턴스를 반환합니다 (lazy initialization)"""
        if self._service is None:
            self._service = build("calendar", "v3", developerKey=self.api_key)
        return self._service

    def _get_cache_file_path(self, country_code: str, start_date: date, end_date: date) -> Path:
        """캐시 파일 경로를 생성합니다."""
        cache_key = f"{country_code}_{start_date.isoformat()}_{end_date.isoformat()}.json"
        return self.cache_dir / cache_key

    def _load_cache(self, country_code: str, start_date: date, end_date: date) -> Optional[dict[date, str]]:
        """파일에서 캐시를 로드합니다. 만료된 캐시는 None을 반환합니다."""
        cache_file = self._get_cache_file_path(country_code, start_date, end_date)

        if not cache_file.exists():
            return None

        try:
            with open(cache_file, "r", encoding="utf-8") as f:
                cache_data = json.load(f)

            # 캐시 만료 확인
            cached_time = datetime.fromisoformat(cache_data.get("timestamp", "1970-01-01T00:00:00"))
            now = datetime.now()

            if (now - cached_time).days > self.CACHE_EXPIRY_DAYS:
                # 만료된 캐시 파일 삭제
                cache_file.unlink(missing_ok=True)
                return None

            # 날짜 문자열을 date 객체로 변환
            holidays = {
                datetime.strptime(date_str, "%Y-%m-%d").date(): name
                for date_str, name in cache_data.get("holidays", {}).items()
            }

            return holidays

        except (json.JSONDecodeError, ValueError, OSError) as e:
            print(f"Error loading cache: {e}")
            return None

    def _save_cache(self, country_code: str, start_date: date, end_date: date, holidays: dict[date, str]):
        """캐시를 파일에 저장합니다."""
        cache_file = self._get_cache_file_path(country_code, start_date, end_date)

        try:
            cache_data = {
                "timestamp": datetime.now().isoformat(),
                "holidays": {dt.isoformat(): name for dt, name in holidays.items()}
            }

            with open(cache_file, "w", encoding="utf-8") as f:
                json.dump(cache_data, f, ensure_ascii=False, indent=2)

        except OSError as e:
            print(f"Error saving cache: {e}")

    def get_holidays(
        self, country_code: str, start_date: date, end_date: date
    ) -> dict[date, str]:
        """
        특정 기간의 공휴일 목록을 조회합니다.

        Args:
            country_code: 국가 코드 (예: 'KR', 'US', 'SG')
            start_date: 조회 시작일
            end_date: 조회 종료일

        Returns:
            공휴일 날짜와 이름의 딕셔너리 {date: holiday_name}
        """
        # 메모리 캐시 확인
        cache_key = (country_code, start_date, end_date)
        if cache_key in self._cache:
            return self._cache[cache_key]

        # 파일 캐시 확인
        cached_holidays = self._load_cache(country_code, start_date, end_date)
        if cached_holidays is not None:
            self._cache[cache_key] = cached_holidays
            return cached_holidays

        calendar_id = self.CALENDAR_IDS.get(country_code.upper())
        if not calendar_id:
            # 지원하지 않는 국가는 빈 딕셔너리 반환
            return {}

        holidays = {}

        try:
            service = self._get_service()

            # Google Calendar API는 datetime을 RFC3339 형식으로 요구
            time_min = datetime.combine(start_date, datetime.min.time()).isoformat() + "Z"
            time_max = datetime.combine(end_date, datetime.max.time()).isoformat() + "Z"

            events_result = (
                service.events()
                .list(
                    calendarId=calendar_id,
                    timeMin=time_min,
                    timeMax=time_max,
                    singleEvents=True,
                    orderBy="startTime",
                )
                .execute()
            )

            events = events_result.get("items", [])

            for event in events:
                # 공휴일은 종일 이벤트로 date 형식으로 저장됨
                start = event.get("start", {})
                if "date" in start:
                    # description 필드를 확인하여 실제 공휴일만 포함
                    # Observance는 기념일이므로 제외
                    description = event.get("description", "")
                    if "Public holiday" in description or "public holiday" in description:
                        holiday_date = datetime.strptime(start["date"], "%Y-%m-%d").date()
                        holiday_name = event.get("summary", "Holiday")
                        holidays[holiday_date] = holiday_name

        except HttpError as error:
            # API 오류 발생 시 빈 딕셔너리 반환 (에러 로깅은 상위 레이어에서 처리)
            print(f"Google Calendar API error: {error}")
            return {}

        # 메모리 캐시에 저장
        self._cache[cache_key] = holidays

        # 파일 캐시에 저장 (일주일 동안 유지)
        self._save_cache(country_code, start_date, end_date, holidays)

        return holidays

    def is_holiday(self, country_code: str, check_date: date) -> bool:
        """
        특정 날짜가 공휴일인지 확인합니다.

        Args:
            country_code: 국가 코드
            check_date: 확인할 날짜

        Returns:
            공휴일 여부
        """
        holidays = self.get_holidays(country_code, check_date, check_date)
        return check_date in holidays
