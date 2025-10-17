from typing import Annotated

from fastapi import Depends

from app.core.config import AppSettings, get_settings


SettingsDep = Annotated[AppSettings, Depends(get_settings)]

