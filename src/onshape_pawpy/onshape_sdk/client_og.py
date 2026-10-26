"""Onshape API client with HMAC-SHA256 authentication.

Authentication reference:
    https://onshape-public.github.io/docs/auth/apikeys/

Authorization header format:
    ``On <AccessKey>:HmacSHA256:<Signature>``

The nonce goes ONLY in the ``On-Nonce`` header — never in the Authorization
string.  The full signing string is lowercased before hashing.
"""

from __future__ import annotations

import base64
import hashlib
import hmac
import os
import random
import string
from datetime import datetime, timezone
from functools import cached_property
from typing import Optional
from urllib.parse import urlencode

import requests

from onshape_sdk.api_version import API_VERSION_PATH


class OnshapeClient:
    """Lightweight Onshape REST API client using API-key HMAC auth.

    Usage
    -----
    >>> client = OnshapeClient.from_env()
    >>> client.test_auth()
    >>> parts = client.parts.list(did, "w", wid, eid)
    """

    DEFAULT_BASE_URL = 'https://cad.onshape.com'

    def __init__(
        self,
        access_key: str,
        secret_key: str,
        base_url: str = DEFAULT_BASE_URL,
    ) -> None:
        if not access_key or not secret_key:
            raise ValueError('Both access_key and secret_key are required.')
        self.access_key = access_key
        self.secret_key = secret_key
        self.base_url = base_url.rstrip('/')

    # ── Constructors ──────────────────────────────────────────────────────────

    @classmethod
    def from_env(
        cls,
        base_url: str = DEFAULT_BASE_URL,
        dotenv_path: Optional[str] = None,
    ) -> 'OnshapeClient':
        """Create a client from ``ONSHAPE_ACCESS_KEY`` / ``ONSHAPE_SECRET_KEY``
        environment variables.

        Automatically calls ``load_dotenv()`` so a ``.env`` file next to your
        script or notebook is picked up.
        """
        from dotenv import load_dotenv

        load_dotenv(dotenv_path)
        access_key = os.environ.get('ONSHAPE_ACCESS_KEY', '')
        secret_key = os.environ.get('ONSHAPE_SECRET_KEY', '')
        return cls(access_key=access_key, secret_key=secret_key, base_url=base_url)

    # ── Auth internals ────────────────────────────────────────────────────────

    @staticmethod
    def _make_nonce(length: int = 25) -> str:
        chars = string.ascii_letters + string.digits
        return ''.join(random.choices(chars, k=length))

    def _sign(
        self,
        method: str,
        path: str,
        query_params: Optional[dict] = None,
        content_type: str = 'application/json',
    ) -> dict[str, str]:
        """Build HMAC-SHA256 signed headers for a single request."""
        nonce = self._make_nonce()
        date = datetime.now(timezone.utc).strftime('%a, %d %b %Y %H:%M:%S GMT')
        query = urlencode(query_params) if query_params else ''

        # Entire signing string must be lowercased before hashing
        signing_string = (
            method.lower()
            + '\n'
            + nonce
            + '\n'
            + date
            + '\n'
            + content_type.lower()
            + '\n'
            + path.lower()
            + '\n'
            + query.lower()
            + '\n'
        ).lower()

        sig = base64.b64encode(
            hmac.new(
                self.secret_key.encode('utf-8'),
                signing_string.encode('utf-8'),
                hashlib.sha256,
            ).digest()
        ).decode('utf-8')

        return {
            'Authorization': f'On {self.access_key}:HmacSHA256:{sig}',
            'Date': date,
            'On-Nonce': nonce,
            'Content-Type': content_type,
            'Accept': 'application/json',
        }

    # ── HTTP verbs ────────────────────────────────────────────────────────────

    def get(
        self,
        path: str,
        query_params: Optional[dict] = None,
        accept: str = 'application/json',
    ) -> requests.Response:
        """Authenticated GET request."""
        headers = self._sign('GET', path, query_params)
        headers['Accept'] = accept
        url = self.base_url + path
        if query_params:
            url += '?' + urlencode(query_params)
        r = requests.get(url, headers=headers)
        return r

    def get_raise_json(
        self,
        path: str,
        query_params: Optional[dict] = None,
        accept: str = 'application/json',
        raise_status: bool = True,
        rtn_json: bool = True,
    ):
        r = self.get(path, query_params=query_params, accept=accept)
        if raise_status:
            r.raise_for_status()
        if rtn_json:
            r = r.json()
        return r

    def post(
        self,
        path: str,
        body: Optional[dict | list] = None,
        query_params: Optional[dict] = None,
    ) -> requests.Response:
        """Authenticated POST request (JSON body)."""
        headers = self._sign('POST', path, query_params)
        url = self.base_url + path
        if query_params:
            url += '?' + urlencode(query_params)
        return requests.post(url, headers=headers, json=body if body is not None else {})

    def put(
        self,
        path: str,
        body: Optional[dict | list] = None,
        query_params: Optional[dict] = None,
    ) -> requests.Response:
        """Authenticated PUT request (JSON body)."""
        headers = self._sign('PUT', path, query_params)
        url = self.base_url + path
        if query_params:
            url += '?' + urlencode(query_params)
        return requests.put(url, headers=headers, json=body if body is not None else {})

    def delete(
        self,
        path: str,
        query_params: Optional[dict] = None,
    ) -> requests.Response:
        """Authenticated DELETE request."""
        headers = self._sign('DELETE', path, query_params)
        url = self.base_url + path
        if query_params:
            url += '?' + urlencode(query_params)
        return requests.delete(url, headers=headers)

    # ── Resource APIs ─────────────────────────────────────────────────────────
    # Lazily instantiated via cached_property so they're only created once.

    @cached_property
    def documents(self):
        """Documents API — create, list, search, version."""
        from .documents import DocumentsApi

        return DocumentsApi(self)

    @cached_property
    def parts(self):
        """Parts API — list and inspect parts."""
        from .parts import PartsApi

        return PartsApi(self)

    @cached_property
    def part_studios(self):
        """Part Studios API — features, variables, direct exports."""
        from .part_studios import PartStudiosApi

        return PartStudiosApi(self)

    @cached_property
    def assemblies(self):
        """Assemblies API — definitions, BOM, mates, occurrences."""
        from .assemblies import AssembliesApi

        return AssembliesApi(self)

    @cached_property
    def drawings(self):
        """Drawings API — views and geometry."""
        from .drawings import DrawingsApi

        return DrawingsApi(self)

    @cached_property
    def translations(self):
        """Translations API — async export/import engine."""
        from .translations import TranslationsApi

        return TranslationsApi(self)

    @cached_property
    def blob_elements(self):
        """Blob Elements API — upload and download files."""
        from .blob_elements import BlobElementsApi

        return BlobElementsApi(self)

    @cached_property
    def metadata(self):
        """Metadata API — custom properties on elements and parts."""
        from .metadata import MetadataApi

        return MetadataApi(self)

    @cached_property
    def thumbnails(self):
        """Thumbnails API — preview images."""
        from .thumbnails import ThumbnailsApi

        return ThumbnailsApi(self)

    @cached_property
    def webhooks(self):
        """Webhooks API — event-driven notifications."""
        from .webhooks import WebhooksApi

        return WebhooksApi(self)

    # ── Diagnostics ───────────────────────────────────────────────────────────

    def test_auth(self) -> bool:
        """Run a quick auth diagnostic and print results.

        Tests:
            1. ``GET /{API_VERSION_PATH}/users/sessioninfo`` — verifies HMAC signing works
            2. ``GET /{API_VERSION_PATH}/documents?limit=1``  — verifies read scope

        Returns
        -------
        bool
            ``True`` if all tests pass.
        """
        sep = '─' * 50
        all_ok = True

        print(sep)
        print('Onshape Auth Diagnostic')
        print(sep)
        print(f'  Access Key : {self.access_key[:8]}…')
        print(f'  Base URL   : {self.base_url}')

        # Test 1 — session info
        print(f'\n  [1/2] GET /{API_VERSION_PATH}/users/sessioninfo')
        r1 = self.get('{API_VERSION_PATH}/users/sessioninfo')
        if r1.status_code == 200:
            me = r1.json()
            print(f'    ✅ Authenticated as: {me.get("name")} ({me.get("email")})')
        else:
            all_ok = False
            print(f'    ❌ {r1.status_code} — {self._err(r1)}')
            if r1.status_code == 401:
                print(
                    '    → ACCESS_KEY or SECRET_KEY is wrong — regenerate at dev-portal.onshape.com'
                )
            elif r1.status_code == 204:
                print('    → 204 No Content — keys may be invalid or expired')

        # Test 2 — list documents
        print(f'\n  [2/2] GET /{API_VERSION_PATH}/documents?limit=1')
        r2 = self.get(f'{API_VERSION_PATH}/documents', query_params={'filter': 0, 'limit': 1})
        if r2.status_code == 200:
            items = r2.json().get('items', [])
            print(f'    ✅ Read scope OK — found {len(items)} document(s)')
        else:
            all_ok = False
            print(f'    ❌ {r2.status_code} — {self._err(r2)}')
            if r2.status_code == 403:
                print('    → API key may be missing read permissions')

        print(f'\n{sep}')
        print(f'  Result: {"✅ All good!" if all_ok else "❌ See errors above."}')
        print(sep)
        return all_ok

    @staticmethod
    def _err(resp: requests.Response) -> str:
        try:
            return resp.json().get('message', resp.text[:200])
        except Exception:
            return resp.text[:200]

    # ── repr ──────────────────────────────────────────────────────────────────

    def __repr__(self) -> str:
        return f"OnshapeClient(access_key='{self.access_key[:8]}…', base_url='{self.base_url}')"
