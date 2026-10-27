"""Thin Onshape REST client (API-key Basic auth)."""

from __future__ import annotations

import time
from typing import Any, Self

import httpx
from httpx import Response
from pydantic import BaseModel, TypeAdapter

from onshape_pawpy.api.assemblies_mod import AssembliesApi, PartsApi
from onshape_pawpy.api.exceptions import OnshapeError
from onshape_pawpy.api.settings import OnshapeSettings
from onshape_pawpy.api.util import _list_adapter, _body
from onshape_pawpy.path import OnshapeIds


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


class OnshapeClient2(OnshapeClient):
    def __enter__(self) -> Self:
        return self

    def __exit__(self, *exc: object) -> None:
        self.close()

    def close(self) -> None:
        self._http.close()

    def _send(self, method: str, path: str, **kw: Any) -> bytes:
        resp = self._http.request(method, path, **kw)
        resp.raise_for_status()
        return resp.content

    def get_model[M: BaseModel](self, path: str, model: type[M], **kw: Any) -> M:
        return model.model_validate_json(self._send('GET', path, **kw))

    def get_list[M: BaseModel](self, path: str, model: type[M], **kw: Any) -> list[M]:
        res = self._send('GET', path, **kw)
        return _list_adapter(model).validate_json(res)

    def post_model[M: BaseModel](
        self, path: str, model: type[M], body: BaseModel | None = None, **kw: Any
    ) -> M:
        return model.model_validate_json(self._send('POST', path, json=_body(body), **kw))

    def get_as[T](self, path: str, adapter: TypeAdapter[T], **kw: Any) -> T:
        return adapter.validate_json(self._send('GET', path, **kw))

    def request_as[T](self, method: str, path: str, adapter: TypeAdapter[T], **kw: Any) -> T:
        return adapter.validate_json(self._send(method, path, **kw).content)

    @property
    def assemblies(self):
        return AssembliesApi(client=self)

    # getdef = partialmethod(get_model, model=Assembly)

    @property
    def parts(self):
        return PartsApi(client=self)

#
# def main1():
#     ids = OnshapeIds.from_url(
#         r'https://cad.onshape.com/documents/9323f6caa9681a8ed00b5323/w/b3c14a29fe0d314db7853c55/e/188a1128c6d01fb539ddeffa'
#     )
#     settings_ = OnshapeSettings()
#     client = OnshapeClient(settings=settings_)
#     res = client.assemblies.get_definition(ids=ids)
#     ...


def main_2():
    if __name__ == '__main__':
        settings_ = OnshapeSettings()
        ids = OnshapeIds.from_url(
            r'https://cad.onshape.com/documents/9323f6caa9681a8ed00b5323/w/b3c14a29fe0d314db7853c55/e/188a1128c6d01fb539ddeffa'
        )
        with OnshapeClient2(settings=settings_) as client:
            res = client.parts.get_list(ids)
            print(res)
            res = client.assemblies.get_definition(ids)
            print(res)
            ...
        ...


if __name__ == '__main__':
    main_2()
