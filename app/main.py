from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.api.v1.routers import health as health_router
from app.api.v1.routers import calculate as calculate_router
from app.core.config import get_settings
from app.web import routers as web_pages


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(title=settings.app_name, debug=settings.debug)

    api_prefix = settings.api_prefix.rstrip("/")
    app.include_router(health_router.router, prefix=api_prefix)
    app.include_router(calculate_router.router, prefix=api_prefix)

    # Web UI
    app.include_router(web_pages.router)
    app.mount("/static", StaticFiles(directory="app/static"), name="static")

    return app


app = create_app()
