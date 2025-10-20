from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from app.core.i18n import detect_language, get_translations


router = APIRouter(include_in_schema=False)
templates = Jinja2Templates(directory="app/templates")


@router.get("/", response_class=HTMLResponse)
def index(request: Request):
    """웹 UI 인덱스 페이지"""
    # Detect language from Accept-Language header
    accept_language = request.headers.get("accept-language")
    lang = detect_language(accept_language)
    t = get_translations(lang)

    return templates.TemplateResponse(
        "index.html",
        {"request": request, "t": t},
    )
