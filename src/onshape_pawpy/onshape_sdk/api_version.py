from abc import ABC
from typing import Any, ClassVar

from requests import Response

from onshape_sdk import OnshapeClient
from onshape_sdk.ids import OnshapeLoc

API_VERSION = 'v10'
API_VERSION_PATH = f'/api/{API_VERSION}'
BASE_API_PATH = f'https://cad.onshape.com{API_VERSION_PATH}'


def build_path(ids_tup: OnshapeLoc, prefix: str = '', suffix: str = '') -> str:
    """Build the ``/d/{did}/{wvm}/{wvm_id}[/e/{eid}]`` path fragment."""
    did, wvm, wvm_id, eid = ids_tup
    path = f'{API_VERSION_PATH}{prefix}/d/{did}/{wvm}/{wvm_id}'
    if eid:
        path += f'/e/{eid}'
    if suffix:
        path += suffix
    return path


class ApiBase(ABC):
    """Base class for all API endpoint classes."""

    _path_prefix: ClassVar[str]
    client: OnshapeClient

    def build_path(
        self,
        loc: OnshapeLoc,
        *,
        prefix: str = '',
        suffix: str = '',
    ) -> str:
        """Build the full API path for a given element."""
        prefix = self._path_prefix + prefix
        return build_path(loc, prefix=prefix, suffix=suffix)

    def get(
        self,
        loc: OnshapeLoc,
        *,
        prefix: str = '',
        suffix: str = '',
        raise_status: bool = True,
        parse_json: bool = True,
    ) -> dict[str, Any] | Response:
        _path = self.build_path(loc, prefix=prefix, suffix=suffix)
        res = self.client.get(_path)
        if raise_status:
            res.raise_for_status()
        if parse_json:
            res = res.json()
        return res

    def get_json(
        self,
        loc: OnshapeLoc,
        *,
        prefix: str = '',
        suffix: str = '',
    ) -> dict[str, Any]:
        _path = self.build_path(loc, prefix=prefix, suffix=suffix)
        res = self.client.get(_path)
        res.raise_for_status()
        return res.json()
