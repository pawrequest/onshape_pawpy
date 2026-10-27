import inspect
from collections.abc import Callable, Iterator
from functools import wraps
from typing import Any, Self, get_args, get_origin, get_type_hints
import time

import httpx
from pydantic import BaseModel, TypeAdapter

from onshape_pawpy.api.settings import OnshapeSettings
from onshape_pawpy.api.exceptions import OnshapeError
from onshape_pawpy.api.util import _body, _list_adapter


class Page[M](BaseModel):
    items: list[M]
    next: str | None = None


class OnshapeClient3:
    def __init__(
        self,
        settings: OnshapeSettings,
        transport: httpx.BaseTransport | None = None,
    ) -> None:
        self.settings = settings
        self._max_retries = settings.max_retries
        self._http = httpx.Client(
            base_url=settings.base_url,
            auth=settings.auth,
            headers=settings.headers,
            timeout=30,
            transport=transport,
        )

    def __enter__(self) -> Self:
        return self

    def __exit__(self, *exc: object) -> None:
        self.close()

    def close(self) -> None:
        self._http.close()

    # ---- the single request path ----

    def _send(self, method: str, path: str, **kw: Any) -> httpx.Response:
        attempt = 0
        while True:
            resp = self._http.request(method, path, **kw)
            if resp.status_code != 429 or attempt >= self._max_retries:
                break
            time.sleep(float(resp.headers.get('Retry-After', 2**attempt)))
            attempt += 1

        try:
            resp.raise_for_status()
        except httpx.HTTPStatusError as e:
            raise OnshapeError(f'{method} {path} -> {resp.status_code}: {resp.text[:500]}') from e
        return resp

    # ---- typed helpers ----

    def get_model[M: BaseModel](self, path: str, model: type[M], **kw: Any) -> M:
        return model.model_validate_json(self._send('GET', path, **kw).content)

    def get_list[M: BaseModel](self, path: str, model: type[M], **kw: Any) -> list[M]:
        return _list_adapter(model).validate_json(self._send('GET', path, **kw).content)

    def post_model[M: BaseModel](
        self, path: str, model: type[M], body: BaseModel | None = None, **kw: Any
    ) -> M:
        resp = self._send('POST', path, json=_body(body), **kw)
        return model.model_validate_json(resp.content)

    def delete(self, path: str, **kw: Any) -> None:
        self._send('DELETE', path, **kw)

    # ---- pagination ----

    def iter_items[M: BaseModel](self, path: str, model: type[M], **kw: Any) -> Iterator[M]:
        url: str | None = path
        while url:
            resp = self._send('GET', url, **kw)
            page = Page[model].model_validate_json(resp.content)  # pyright: ignore[reportInvalidTypeArguments]
            yield from page.items
            url, kw = page.next, {}  # next URL already carries its query string


def endpoint[F: Callable[..., Any]](
    method: str,
    path: str,
    *,
    body: str | None = None,  # name of the param holding the request model
    query: tuple[str, ...] = (),  # names of params sent as query string
) -> Callable[[F], F]:
    def deco(fn: F) -> F:
        sig = inspect.signature(fn)
        returns = get_type_hints(fn)['return']

        paginated = get_origin(returns) is Iterator
        adapter = None if (paginated or returns is type(None)) else TypeAdapter(returns)

        @wraps(fn)
        def wrapper(self, *args, **kwargs):
            bound = sig.bind(self, *args, **kwargs)
            bound.apply_defaults()
            a = bound.arguments

            url = path.format(**a)  # '{ref.path}' and '{did}' both work
            kw: dict[str, Any] = {}
            if query:
                kw['params'] = {k: a[k] for k in query if a[k] is not None}
            if body:
                kw['json'] = _body(a[body])

            client = self.client
            if paginated:
                return client.iter_items(url, get_args(returns)[0], **kw)
            if adapter is None:
                client._send(method, url, **kw)
                return None
            return client.request_as(method, url, adapter, **kw)

        return wrapper  # type: ignore[return-value]

    return deco
