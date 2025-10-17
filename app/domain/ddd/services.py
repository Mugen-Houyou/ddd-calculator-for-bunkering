from datetime import date, timedelta


class DateCalculator:
    """날짜 계산을 위한 도메인 서비스"""

    @staticmethod
    def is_weekend(check_date: date) -> bool:
        """주말 여부 확인 (토요일=5, 일요일=6)"""
        return check_date.weekday() in (5, 6)

    @staticmethod
    def add_business_days(
        start_date: date,
        days: int,
        skip_weekends: bool = True,
        skip_holidays: bool = True,
        holidays: set[date] | None = None,
    ) -> tuple[date, list[date], list[date]]:
        """
        영업일 기준으로 날짜를 더합니다.

        Args:
            start_date: 시작 날짜
            days: 더할 일수
            skip_weekends: 주말 제외 여부
            skip_holidays: 공휴일 제외 여부
            holidays: 공휴일 집합

        Returns:
            (계산된 날짜, 제외된 주말 목록, 제외된 공휴일 목록)
        """
        if holidays is None:
            holidays = set()

        current_date = start_date
        days_added = 0
        excluded_weekends: list[date] = []
        excluded_holidays: list[date] = []

        while days_added < days:
            current_date += timedelta(days=1)

            # 주말과 공휴일 체크
            is_valid_day = True

            if skip_weekends and DateCalculator.is_weekend(current_date):
                is_valid_day = False
                excluded_weekends.append(current_date)

            if skip_holidays and current_date in holidays:
                is_valid_day = False
                excluded_holidays.append(current_date)

            # 유효한 날짜인 경우에만 카운트 증가
            if is_valid_day:
                days_added += 1

        return current_date, excluded_weekends, excluded_holidays

    @staticmethod
    def get_next_business_day(
        check_date: date,
        skip_weekends: bool = True,
        skip_holidays: bool = True,
        holidays: set[date] | None = None,
    ) -> date:
        """
        다음 영업일을 반환합니다.

        Args:
            check_date: 확인할 날짜
            skip_weekends: 주말 제외 여부
            skip_holidays: 공휴일 제외 여부
            holidays: 공휴일 집합

        Returns:
            다음 영업일
        """
        if holidays is None:
            holidays = set()

        next_day = check_date
        while True:
            next_day += timedelta(days=1)

            is_valid_day = True

            if skip_weekends and DateCalculator.is_weekend(next_day):
                is_valid_day = False

            if skip_holidays and next_day in holidays:
                is_valid_day = False

            if is_valid_day:
                return next_day
