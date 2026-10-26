"""Thin Onshape REST client (API-key Basic auth)."""

import time
from functools import cached_property
from typing import Any

import httpx
from httpx import Response
from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

from onshape_pawpy.api.assemblies_mod import AssembliesApi
from onshape_pawpy.api.auth import OnshapeHmacAuth
from onshape_pawpy.api.exceptions import OnshapeError
from onshape_pawpy.api.util import PROJECT_ROOT
from onshape_pawpy.path import OnshapeIds


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


class OnshapeClient:
    def __init__(
        self,
        settings: OnshapeSettings,
        transport: httpx.BaseTransport | None = None,
    ) -> None:
        self._max_retries = settings.max_retries if settings else 3
        self.settings = settings
        self._http = httpx.Client(
            base_url=self.settings.base_url,
            auth=self.settings.auth,
            headers=self.settings.headers,
            timeout=30,
            transport=transport,
        )

    def request(
        self,
        method: str,
        path: str,
        *,
        json: Any = None,
        params: dict | None = None,
        fetch_next: bool = True,
    ) -> Response:
        response = None
        for attempt in range(self._max_retries + 1):
            response = self._http.request(
                method, path, json=json, params=params if params else None
            )
            if response.status_code == 429 and attempt < self._max_retries:
                time.sleep(float(response.headers.get('Retry-After', 2**attempt)))
                continue
            break
        if not response:
            raise ValueError('No response')
        response.raise_for_status()

        if response and response.is_error:
            raise OnshapeError(f'{method} {path} -> {response.status_code}: {response.text[:500]}')
        if fetch_next and hasattr(response, 'next_request') and response.next_request:
            return self.get(response.next_request.url)
        return response

    def get(self, path: str, params: dict | None = None) -> Any:
        return self.request('GET', path, params=params)

    def post(self, path: str, body: Any) -> Any:
        return self.request('POST', path, json=body)

    def delete(self, path: str) -> Any:
        return self.request('DELETE', path)

    @property
    def assemblies(self):
        return AssembliesApi(client=self)


if __name__ == '__main__':
    ids = OnshapeIds.from_url(
        r'https://cad.onshape.com/documents/9323f6caa9681a8ed00b5323/w/b3c14a29fe0d314db7853c55/e/188a1128c6d01fb539ddeffa'
    )
    settings_ = OnshapeSettings()
    client = OnshapeClient(settings=settings_)
    res = client.assemblies.get_definition(ids=ids)
    ...
