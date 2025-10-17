from abc import ABC, abstractmethod
from datetime import date


class HolidayProvider(ABC):
    """공휴일 조회를 위한 추상 인터페이스"""

    @abstractmethod
    def get_holidays(self, country_code: str, start_date: date, end_date: date) -> dict[date, str]:
        """
        특정 기간의 공휴일 목록을 조회합니다.

        Args:
            country_code: 국가 코드 (예: 'ko.south_korea', 'en.usa', 'en.singapore')
            start_date: 조회 시작일
            end_date: 조회 종료일

        Returns:
            공휴일 날짜와 이름의 딕셔너리 {date: holiday_name}
        """
        pass

    @abstractmethod
    def is_holiday(self, country_code: str, check_date: date) -> bool:
        """
        특정 날짜가 공휴일인지 확인합니다.

        Args:
            country_code: 국가 코드
            check_date: 확인할 날짜

        Returns:
            공휴일 여부
        """
        pass
