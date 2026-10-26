from __future__ import annotations

from abc import ABC
from dataclasses import is_dataclass
from typing import TYPE_CHECKING, ClassVar

from httpx import Response
from pydantic import BaseModel

if TYPE_CHECKING:
    from onshape_pawpy.api.client2 import OnshapeClient2
from onshape_pawpy.api.util import build_path
from onshape_pawpy.path import OnshapeIds


class ApiBase(ABC):
    """Base class for all API endpoint classes."""

    _path_prefix: ClassVar[str]
    client: OnshapeClient2

    def __init__(self, client: OnshapeClient2) -> None:
        self.client = client

    def get[T: Response | BaseModel | dict | list[T]](
        self,
        ids: OnshapeIds,
        *,
        prefix: str = '',
        suffix: str = '',
        params: dict | None = None,
        return_type: type[T] = dict,
    ) -> T:
        _path = build_path(ids, prefix=self._path_prefix + prefix, suffix=suffix)
        print(_path)
        res = self.client.get(_path, params=params)

        if issubclass(return_type, BaseModel):
            return return_type.model_validate_json(res.text)
        elif type(return_type) is list[BaseModel]:
            return [return_type.model_validate(item) for item in res.json()]
        elif return_type in [dict, list]:
            return res.json()
        elif is_dataclass(return_type):
            return return_type(**res.json())
        elif issubclass(return_type, Response):
            return res
        else:
            raise TypeError(f'Unsupported return type: {return_type}')


# class Endpoint(BaseModel):
#     prefix: str
#     suffix: str
#     return_type: type
#     input_type: type | None = None
#
#
# get_assembly_definitions = Endpoint(
#     prefix=r'/assemblies', suffix=r'definition', return_type=AssemblyDefinition
# )
