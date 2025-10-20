from datetime import date, timedelta
from typing import Optional

from app.domain.ddd.entities import DeliveryInfo, PaymentTerm, DueDateResult
from app.domain.ddd.services import DateCalculator
from app.infrastructure.holiday_provider import HolidayProvider


def calculate_due_date(
    delivery: DeliveryInfo,
    term: PaymentTerm,
    holiday_provider: Optional[HolidayProvider] = None,
) -> DueDateResult:
    """
    지급기일을 계산합니다.

    Args:
        delivery: 배송 정보
        term: 지급 조건
        holiday_provider: 공휴일 제공자 (옵션)

    Returns:
        지급기일 계산 결과 (날짜, 제외된 주말, 제외된 공휴일)
    """
    if term.kind.upper() == "DDD":
        if term.days is None:
            raise ValueError("DDD term requires 'days'")

        # 공급당일을 1DDD로 포함하는 경우, days를 1 감소
        effective_days = term.days - 1 if term.include_delivery_as_day_one else term.days

        # 공휴일 조회 (필요한 경우)
        holidays: set[date] = set()
        holiday_names_map: dict[date, dict[str, str]] = {}
        if term.skip_holidays and holiday_provider is not None:
            # 예상 기간보다 넉넉하게 조회 (최대 2배 기간)
            # 주말/공휴일을 제외하므로 실제 소요 일수가 더 길 수 있음
            max_days = effective_days * 2 + 30
            end_date = delivery.delivery_date + timedelta(days=max_days)

            # 여러 국가의 공휴일을 병합 (국가별로 추적)
            for country_code in delivery.country_codes:
                country_holidays = holiday_provider.get_holidays(
                    country_code, delivery.delivery_date, end_date
                )
                holidays.update(country_holidays.keys())

                # 각 공휴일에 대해 국가 코드와 함께 저장
                for holiday_date, holiday_name in country_holidays.items():
                    if holiday_date not in holiday_names_map:
                        holiday_names_map[holiday_date] = {}
                    holiday_names_map[holiday_date][country_code] = holiday_name

        # 영업일 기준 날짜 계산
        due_date, excluded_weekends, excluded_holidays = DateCalculator.add_business_days(
            delivery.delivery_date,
            effective_days,
            skip_weekends=term.skip_weekends,
            skip_holidays=term.skip_holidays,
            holidays=holidays,
        )

        return DueDateResult(
            due_date=due_date,
            excluded_weekends=excluded_weekends,
            excluded_holidays=excluded_holidays,
            holiday_names=holiday_names_map if holiday_names_map else None,
        )

    elif term.kind.upper() in {"COD", "CIA"}:
        # COD(Cash on Delivery), CIA(Cash in Advance): 배송일과 동일
        return DueDateResult(
            due_date=delivery.delivery_date,
            excluded_weekends=[],
            excluded_holidays=[],
        )
    else:
        raise ValueError(f"Unsupported payment term kind: {term.kind}")

