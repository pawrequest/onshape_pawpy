from __future__ import annotations

from functools import cached_property

from pydantic import SecretStr, Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from onshape_pawpy.api.auth import OnshapeHmacAuth
from onshape_pawpy.api.util import PROJECT_ROOT


def default_headers() -> dict[str, str]:
    """Return default headers for Onshape API requests."""
    return {
        'Accept': 'application/json;charset=UTF-8; qs=0.09',
        'Content-Type': 'application/json;charset=UTF-8; qs=0.09',
    }


class OnshapeSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=PROJECT_ROOT / '.env',
        env_file_encoding='utf-8',
    )
    access_key: SecretStr = Field(..., alias='ONSHAPE_ACCESS_KEY')
    secret_key: SecretStr = Field(..., alias='ONSHAPE_SECRET_KEY')
    api_version: str = 'v10'
    root_url: str = Field('https://cad.onshape.com/api', alias='ONSHAPE_BASE_URL')
    headers: dict = Field(default_factory=default_headers)
    max_retries: int = 3

    @cached_property
    def auth(self):
        return OnshapeHmacAuth(self.access_key, self.secret_key)

    @cached_property
    def base_url(self):
        return f'{self.root_url}/{self.api_version}'
