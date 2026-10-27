from __future__ import annotations

from abc import ABC
from typing import TYPE_CHECKING, ClassVar

from httpx import Response
from pydantic import BaseModel

if TYPE_CHECKING:
    from onshape_pawpy.api.client import OnshapeClient2
from onshape_pawpy.api.util import build_path
from onshape_pawpy.path import OnshapeIds


class ApiBase(ABC):
    """Base class for all API endpoint classes."""

    _path_prefix: ClassVar[str]
    client: OnshapeClient2

    def __init__(self, client: OnshapeClient2) -> None:
        self.client = client

    def _build_path(self, ids: OnshapeIds, *, prefix: str = '', suffix: str = '') -> str:
        return build_path(ids, prefix=self._path_prefix + prefix, suffix=suffix)

    def go[T: Response | BaseModel | dict | list[T]](
        self,
        ids: OnshapeIds,
        *,
        prefix: str = '',
        suffix: str = '',
        params: dict | None = None,
    ) -> T:
        _path = build_path(ids, prefix=self._path_prefix + prefix, suffix=suffix)
        return self.client.get(_path, params=params)
