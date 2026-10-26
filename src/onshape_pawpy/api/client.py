"""Thin Onshape REST client (API-key Basic auth)."""

from __future__ import annotations

import os
import time
from pathlib import Path
from typing import Any

import httpx
from dotenv import load_dotenv
from httpx import Response

from ids import OnshapeIds

API_VERSION = 'v10'
BASE_URL = f'https://cad.onshape.com/api/{API_VERSION}'
_HEADERS = {
    'Accept': 'application/json;charset=UTF-8; qs=0.09',
    'Content-Type': 'application/json;charset=UTF-8; qs=0.09',
}
PROJECT_ROOT = Path(__file__).parent.parent.parent


def build_path(ids: OnshapeIds, prefix: str = '', suffix: str = '') -> str:
    """Build the ``/d/{did}/{wvm}/{wvm_id}[/e/{eid}]`` path fragment."""
    did, wvm, wvm_id, eid = ids
    path = f'{BASE_URL}{prefix}/d/{did}/{wvm}/{wvm_id}'
    if eid:
        path += f'/e/{eid}'
    if suffix:
        path += suffix
    return path


class OnshapeError(RuntimeError):
    pass


def _load_dotenv(path: Path = PROJECT_ROOT / '.env') -> None:
    if not path.exists():
        raise FileNotFoundError(f'.env file not found at {path}')
    load_dotenv(dotenv_path=path, override=False)


class OnshapeClient:
    def __init__(
            self,
            access_key: str | None = None,
            secret_key: str | None = None,
            transport: httpx.BaseTransport | None = None,
            max_retries: int = 3,
    ) -> None:
        access = access_key or os.environ.get('ONSHAPE_ACCESS_KEY')
        secret = secret_key or os.environ.get('ONSHAPE_SECRET_KEY')
        if not access or not secret:
            raise OnshapeError(
                'ONSHAPE_ACCESS_KEY and ONSHAPE_SECRET_KEY must be set (env or .env).'
            )
        self._max_retries = max_retries
        self._http = httpx.Client(
            base_url=BASE_URL,
            auth=(access, secret),
            headers=_HEADERS,
            timeout=30,
            transport=transport,
        )

    def request(
            self, method: str, path: str, *, json: Any = None, params: dict | None = None, fetch_next: bool = True
    ) -> Response:
        response = None
        for attempt in range(self._max_retries + 1):
            response = self._http.request(method, path, json=json, params=params)
            if response.status_code == 429 and attempt < self._max_retries:
                time.sleep(float(response.headers.get('Retry-After', 2 ** attempt)))
                continue
            break
        if not response:
            raise ValueError('No response')
        response.raise_for_status()

        if response and response.is_error:
            raise OnshapeError(f'{method} {path} -> {response.status_code}: {response.text[:500]}')
        if fetch_next and hasattr(response, 'next_request') and response.next_request:
            return self.get(response.next_request.url)
        # try:
        #     return response.json() if response and response.content else {}
        # except (JSONDecodeError, UnicodeDecodeError):
        return response

    def get(self, path: str, **params: Any) -> Any:
        return self.request('GET', path, params=params or None)

    def post(self, path: str, body: Any) -> Any:
        return self.request('POST', path, json=body)

    def delete(self, path: str) -> Any:
        return self.request('DELETE', path)
