from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict


class AppSettings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "DDD Calculator API"
    api_prefix: str = "/api/v1"
    debug: bool = False
    google_cal_api_key: str = ""


class HealthStatus(BaseModel):
    status: str = "ok"


def get_settings() -> AppSettings:
    return AppSettings()

