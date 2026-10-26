import base64
import hmac
import secrets
import string
from collections.abc import Generator
from email.utils import formatdate

import httpx
from pydantic import SecretStr

_NONCE_CHARS = string.ascii_letters + string.digits


class SecretBasicAuth(httpx.Auth):
    def __init__(self, username: SecretStr, password: SecretStr) -> None:
        self._username = username
        self._password = password

    def auth_flow(self, request: httpx.Request):
        # unwrapped per request, never stored as plain str on self
        basic = httpx.BasicAuth(
            self._username.get_secret_value(),
            self._password.get_secret_value(),
        )
        yield from basic.auth_flow(request)

    def __repr__(self) -> str:
        return f'{type(self).__name__}(<redacted>)'


class OnshapeHmacAuth(httpx.Auth):
    def __init__(self, access_key: SecretStr, secret_key: SecretStr) -> None:
        self._access = access_key
        self._secret = secret_key

    def auth_flow(self, request: httpx.Request) -> Generator[httpx.Request, httpx.Response, None]:
        nonce = ''.join(secrets.choice(_NONCE_CHARS) for _ in range(25))
        date = formatdate(usegmt=True)
        content_type = request.headers.get('content-type', 'application/json')
        path = request.url.raw_path.split(b'?', 1)[0].decode()
        query = request.url.query.decode()

        signing_string = (
            f'{request.method}\n{nonce}\n{date}\n{content_type}\n{path}\n{query}\n'
        ).lower()

        access = self._access.get_secret_value()
        digest = hmac.digest(
            self._secret.get_secret_value().encode(), signing_string.encode(), 'sha256'
        )
        sig = base64.b64encode(digest).decode()

        request.headers['Date'] = date
        request.headers['On-Nonce'] = nonce
        request.headers['Authorization'] = f'On {access}:HmacSHA256:{sig}'
        yield request

    def __repr__(self) -> str:
        return f'{type(self).__name__}(<redacted>)'
