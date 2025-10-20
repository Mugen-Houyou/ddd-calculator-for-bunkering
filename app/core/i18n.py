"""Internationalization support"""

TRANSLATIONS = {
    "ko": {
        # Page header
        "app_title": "벙커링 DDD 계산기",
        "app_subtitle": "저는 DDD를 계산하기에는 너무나도 머리가 안 굴러갑니다",

        # Form labels
        "delivery_date": "BDN 배송일 (YYYY-MM-DD)",
        "country_region": "국가 / 지역",
        "payment_term": "지급 조건",
        "days_label": "Days (예: 30)",
        "calculate_button": "지급기일 계산",
        "example_text": "예시: 배송일 2025-05-01 + 30 DDD → 2025-05-31",

        # Checkboxes
        "include_weekends": "주말을 DDD에 포함",
        "include_holidays": "공휴일을 DDD에 포함",
        "include_delivery_as_day_one": "공급당일을 1DDD로 포함",
        "adjust_to_weekday": "결제일이 주말/공휴일이면 이전 평일로 조정",

        # Payment terms
        "ddd_full": "DDD (Days after Delivery)",
        "cod_full": "COD",
        "cia_full": "CIA (Cash in Advance)",

        # Country selector
        "add_country": "+ 국가 추가",
        "no_countries": "선택된 국가 없음",

        # Results
        "result_title": "결과",
        "delivery": "배송",
        "countries": "국가",
        "excluded_days": "제외된 날짜",
        "weekends": "주말",
        "holidays": "공휴일",

        # Errors
        "invalid_date": "잘못된 날짜 형식입니다. YYYY-MM-DD 형식을 사용하세요.",
        "days_required": "DDD 조건에는 일수가 필요합니다.",
        "unsupported_term": "지원하지 않는 지급 조건입니다. DDD, COD, CIA 중 하나를 사용하세요.",
        "valid_date_required": "유효한 날짜를 입력하세요 (YYYY-MM-DD).",

        # Region labels
        "region_asia": "아시아",
        "region_middle_east": "중동",
        "region_europe": "유럽",
        "region_americas": "아메리카",
        "region_oceania": "오세아니아",
        "region_africa": "아프리카",
    },
    "en": {
        # Page header
        "app_title": "Bunkering DDD Calculator",
        "app_subtitle": "Automatic calculation of payment due dates based on business days",

        # Form labels
        "delivery_date": "BDN Delivery Date (YYYY-MM-DD)",
        "country_region": "Country / Region",
        "payment_term": "Payment Term",
        "days_label": "Days (e.g., 30)",
        "calculate_button": "Calculate Due Date",
        "example_text": "Example: Delivery 2025-05-01 + 30 DDD → 2025-05-31",

        # Checkboxes
        "include_weekends": "Include weekends in DDD",
        "include_holidays": "Include holidays in DDD",
        "include_delivery_as_day_one": "Count delivery date as Day 1",
        "adjust_to_weekday": "Adjust due date to previous weekday if falls on weekend/holiday",

        # Payment terms
        "ddd_full": "DDD (Days after Delivery)",
        "cod_full": "COD",
        "cia_full": "CIA (Cash in Advance)",

        # Country selector
        "add_country": "+ Add Country",
        "no_countries": "No countries selected",

        # Results
        "result_title": "Result",
        "delivery": "Delivery",
        "countries": "Countries",
        "excluded_days": "Excluded Days",
        "weekends": "Weekends",
        "holidays": "Holidays",

        # Errors
        "invalid_date": "Invalid delivery date format. Use YYYY-MM-DD.",
        "days_required": "Days required for DDD term.",
        "unsupported_term": "Unsupported term kind. Use DDD, COD, or CIA.",
        "valid_date_required": "Please enter a valid date (YYYY-MM-DD).",

        # Region labels
        "region_asia": "Asia",
        "region_middle_east": "Middle East",
        "region_europe": "Europe",
        "region_americas": "Americas",
        "region_oceania": "Oceania",
        "region_africa": "Africa",
    }
}


def detect_language(accept_language: str | None) -> str:
    """
    Detect user's preferred language from Accept-Language header.

    Args:
        accept_language: Accept-Language header value

    Returns:
        Language code ('ko' or 'en')
    """
    if not accept_language:
        return "en"

    # Parse Accept-Language header (e.g., "ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7")
    accept_language = accept_language.lower()

    # Check for Korean
    if "ko" in accept_language.split(",")[0]:
        return "ko"

    return "en"


def get_translations(lang: str) -> dict[str, str]:
    """
    Get translations for the specified language.

    Args:
        lang: Language code ('ko' or 'en')

    Returns:
        Translation dictionary
    """
    return TRANSLATIONS.get(lang, TRANSLATIONS["en"])
