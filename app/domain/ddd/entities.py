from dataclasses import dataclass
from datetime import date


@dataclass(frozen=True)
class DueDateResult:
    """지급기일 계산 결과"""
    due_date: date  # 최종 지급기일
    excluded_weekends: list[date]  # 제외된 주말 목록
    excluded_holidays: list[date]  # 제외된 공휴일 목록
    holiday_names: dict[date, dict[str, str]] | None = None  # 공휴일 이름 매핑 {date: {country_code: holiday_name}}


@dataclass(frozen=True)
class PaymentTerm:
    kind: str  # e.g., "DDD", "COD", "CIA"
    days: int | None = None  # number of days after delivery when kind == DDD
    skip_weekends: bool = True  # 주말 제외 여부
    skip_holidays: bool = True  # 공휴일 제외 여부
    include_delivery_as_day_one: bool = False  # 공급당일을 1DDD로 포함 (True면 days-1로 계산)


@dataclass(frozen=True)
class DeliveryInfo:
    delivery_date: date  # as on BDN
    country_codes: list[str] | None = None  # 국가 코드 리스트 (공휴일 조회용, 다중 선택 가능)

    def __post_init__(self):
        # country_codes가 None이면 기본값으로 ["KR"] 설정
        if self.country_codes is None:
            object.__setattr__(self, "country_codes", ["KR"])

