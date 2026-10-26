from __future__ import annotations

from abc import ABC
from typing import Any, ClassVar

from httpx import Response

from client import OnshapeClient, build_path
from ids import OnshapeIds


class ApiBase(ABC):
    """Base class for all API endpoint classes."""

    _path_prefix: ClassVar[str]
    client: OnshapeClient

    def __init__(self, client: "OnshapeClient") -> None:
        self._c = client

    def build_path(
            self,
            ids: OnshapeIds,
            *,
            prefix: str = '',
            suffix: str = '',
    ) -> str:
        """Build the full API path for a given element."""
        prefix = self._path_prefix + prefix
        return build_path(ids, prefix=prefix, suffix=suffix)

    def get(
            self,
            ids: OnshapeIds,
            *,
            prefix: str = '',
            suffix: str = '',
            **kwargs
    ) -> Response:
        _path = self.build_path(ids, prefix=prefix, suffix=suffix)
        return self.client.get(_path, **kwargs)

    def get_json(
            self,
            ids: OnshapeIds,
            prefix: str = '',
            suffix: str = '',
            **kwargs
    ) -> dict[str, Any] | list[Any]:
        res = self.get(ids, prefix=prefix, suffix=suffix, **kwargs)
        return res.json()
