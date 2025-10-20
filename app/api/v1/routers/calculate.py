from datetime import date
from typing import Optional

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field

from app.core.config import AppSettings, get_settings
from app.domain.ddd.entities import DeliveryInfo, PaymentTerm
from app.infrastructure.google_calendar_holiday_provider import GoogleCalendarHolidayProvider
from app.use_cases.calculate_due_date import calculate_due_date


router = APIRouter(tags=["calculate"])


class CalculateRequest(BaseModel):
    """DDD 계산 요청 모델"""
    delivery_date: date = Field(..., description="배송일 (YYYY-MM-DD)")
    country_codes: list[str] = Field(["KR"], description="국가 코드 목록 (예: ['KR', 'SG'])")
    term_kind: str = Field(..., description="결제 조건 종류 (DDD/COD/CIA)")
    days: Optional[int] = Field(None, description="DDD의 경우 배송 후 일수")
    skip_weekends: bool = Field(True, description="주말 제외 여부")
    skip_holidays: bool = Field(True, description="공휴일 제외 여부")
    include_delivery_as_day_one: bool = Field(False, description="공급당일을 1DDD로 포함 (True면 days-1로 계산)")
    adjust_to_weekday: bool = Field(False, description="결제일이 주말/공휴일이면 이전 평일로 조정")


class CalculateResponse(BaseModel):
    """DDD 계산 응답 모델"""
    country_codes: list[str]
    delivery_date: str
    term_kind: str
    days: Optional[int]
    due_date: str
    excluded_weekends: list[str]
    excluded_holidays: list[str]
    holiday_names: dict[str, dict[str, str]]  # {date_string: {country_code: holiday_name}}
    holidays_excluded: bool


@router.post("/calculate", response_model=CalculateResponse)
def calculate(
    request: CalculateRequest,
    settings: AppSettings = Depends(get_settings),
) -> CalculateResponse:
    """
    배송일과 결제 조건을 기반으로 DDD(Due Date Delivery) 결제일을 계산합니다.

    Args:
        request: 계산 요청 (배송일, 국가 코드, 결제 조건 등)
        settings: 앱 설정

    Returns:
        계산 결과 (결제일, 제외된 주말/공휴일 등)
    """
    # 국가 코드 정규화
    country_codes = [c.upper() for c in request.country_codes]
    term_kind = request.term_kind.strip().upper()

    # Google Calendar API 초기화 (API Key가 있는 경우)
    # 달력 표시를 위해 항상 공휴일 정보 로드
    holiday_provider = None
    if settings.google_cal_api_key:
        holiday_provider = GoogleCalendarHolidayProvider(settings.google_cal_api_key)

    # DDD 계산
    delivery_info = DeliveryInfo(
        delivery_date=request.delivery_date,
        country_codes=country_codes
    )
    payment_term = PaymentTerm(
        kind=term_kind,
        days=request.days,
        skip_weekends=request.skip_weekends,
        skip_holidays=request.skip_holidays,
        include_delivery_as_day_one=request.include_delivery_as_day_one,
        adjust_to_weekday=request.adjust_to_weekday,
    )

    due_result = calculate_due_date(delivery_info, payment_term, holiday_provider)

    # 공휴일 이름 매핑을 문자열 키로 변환 (JSON 직렬화를 위해)
    holiday_names_str: dict[str, dict[str, str]] = {}
    if due_result.holiday_names:
        holiday_names_str = {
            dt.isoformat(): countries_dict
            for dt, countries_dict in due_result.holiday_names.items()
        }

    return CalculateResponse(
        country_codes=country_codes,
        delivery_date=request.delivery_date.isoformat(),
        term_kind=term_kind,
        days=request.days,
        due_date=due_result.due_date.isoformat(),
        excluded_weekends=[dt.isoformat() for dt in due_result.excluded_weekends],
        excluded_holidays=[dt.isoformat() for dt in due_result.excluded_holidays],
        holiday_names=holiday_names_str,
        holidays_excluded=term_kind == "DDD" and holiday_provider is not None,
    )
