from datetime import date
import re

from fastapi import APIRouter, Form, Request, Depends
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from app.core.config import AppSettings, get_settings
from app.core.i18n import detect_language, get_translations
from app.domain.ddd.entities import DeliveryInfo, PaymentTerm
from app.infrastructure.google_calendar_holiday_provider import GoogleCalendarHolidayProvider
from app.use_cases.calculate_due_date import calculate_due_date


router = APIRouter(include_in_schema=False)
templates = Jinja2Templates(directory="app/templates")


@router.get("/", response_class=HTMLResponse)
def index(request: Request):
    # Detect language from Accept-Language header
    accept_language = request.headers.get("accept-language")
    lang = detect_language(accept_language)
    t = get_translations(lang)

    return templates.TemplateResponse(
        "index.html",
        {"request": request, "result": None, "errors": [], "form": None, "t": t},
    )


@router.post("/calculate", response_class=HTMLResponse)
def post_calculate(
    request: Request,
    delivery_date: str = Form(..., description="YYYY-MM-DD"),
    country_code: list[str] = Form(["KR"], description="Country codes (multiple allowed)"),
    term_kind: str = Form(..., description="DDD/COD/CIA"),
    days: str | None = Form(None, description="Days after delivery for DDD"),
    settings: AppSettings = Depends(get_settings),
):
    # Detect language from Accept-Language header
    accept_language = request.headers.get("accept-language")
    lang = detect_language(accept_language)
    t = get_translations(lang)

    errors: list[str] = []
    result: dict | None = None

    # Prepare form values for sticky inputs
    yy = mm = dd = ""
    m = re.match(r"^(\d{4})-(\d{1,2})-(\d{1,2})$", delivery_date or "")
    if m:
        yy, mm, dd = m.group(1), m.group(2), m.group(3)

    # Normalize country codes
    country_codes = [c.upper() for c in country_code] if country_code else ["KR"]

    form_ctx = {
        "yyyy": yy,
        "mm": mm,
        "dd": dd,
        "country_codes": country_codes,
        "term_kind": (term_kind or "").upper(),
        "days": days or "",
    }

    try:
        d = date.fromisoformat(delivery_date)
    except Exception:
        errors.append(t["invalid_date"])
        return templates.TemplateResponse(
            "index.html",
            {"request": request, "result": None, "errors": errors, "form": form_ctx, "t": t},
        )

    kind = (term_kind or "").strip().upper()
    term_days: int | None = None
    if kind == "DDD":
        try:
            term_days = int(days) if days is not None and days != "" else None
        except ValueError:
            term_days = None
        if term_days is None:
            errors.append(t["days_required"])
    elif kind in {"COD", "CIA"}:
        term_days = None
    else:
        errors.append(t["unsupported_term"])

    if errors:
        return templates.TemplateResponse(
            "index.html",
            {"request": request, "result": None, "errors": errors, "form": form_ctx, "t": t},
        )

    # Google Calendar API 초기화 (API Key가 있는 경우)
    holiday_provider = None
    if settings.google_cal_api_key:
        holiday_provider = GoogleCalendarHolidayProvider(settings.google_cal_api_key)

    # DDD 계산
    delivery_info = DeliveryInfo(delivery_date=d, country_codes=country_codes)
    payment_term = PaymentTerm(
        kind=kind,
        days=term_days,
        skip_weekends=True,
        skip_holidays=True,
    )

    due_result = calculate_due_date(delivery_info, payment_term, holiday_provider)

    # 공휴일 이름 매핑을 문자열 키로 변환 (JSON 직렬화를 위해)
    # 구조: {date_string: {country_code: holiday_name}}
    holiday_names_str = {}
    if due_result.holiday_names:
        holiday_names_str = {dt.isoformat(): countries_dict for dt, countries_dict in due_result.holiday_names.items()}

    result = {
        "country_codes": country_codes,
        "delivery_date": d.isoformat(),
        "term_kind": kind,
        "days": term_days,
        "due_date": due_result.due_date.isoformat(),
        "excluded_weekends": [dt.isoformat() for dt in due_result.excluded_weekends],
        "excluded_holidays": [dt.isoformat() for dt in due_result.excluded_holidays],
        "holiday_names": holiday_names_str,
        "holidays_excluded": kind == "DDD" and holiday_provider is not None,
    }
    return templates.TemplateResponse(
        "index.html",
        {"request": request, "result": result, "errors": [], "form": form_ctx, "t": t},
    )
