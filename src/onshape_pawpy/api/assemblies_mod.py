from pydantic import BaseModel, Field, ConfigDict
from pydantic.alias_generators import to_camel

from onshape_pawpy.api.api_base import ApiBase
from onshape_pawpy.api.util import build_path
from onshape_pawpy.path import OnshapeIds


class OsBaseModel(BaseModel):
    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
        validate_by_alias=True,
        serialize_by_alias=True,
    )


class Part(OsBaseModel):
    part_id: str = ''
    name: str = ''
    body_type: str = ''  # "solid", "surface", "wire", ...
    description: str = ''
    material: dict | None = None
    appearance: dict | None = None
    custom_properties: dict | None = None
    state: str = ''
    raw: dict = Field(default_factory=dict, repr=False)


class Assembly(OsBaseModel):
    root_assembly: dict = Field(default_factory=dict)
    sub_assemblies: list[dict] = Field(default_factory=list)
    parts: list[Part] = Field(default_factory=list)
    raw: dict = Field(default_factory=dict, repr=False)


class AssembliesApi(ApiBase):
    """Endpoints under ``/{API_VERSION_PATH}/assemblies``."""

    _path_prefix = '/assemblies'

    # ── Definition ────────────────────────────────────────────────────────────

    def get_definition(
        self,
        ids: OnshapeIds,
        *,
        include_mate_features: bool = False,
        include_non_solids: bool = False,
    ) -> Assembly:
        """Get the full assembly definition (parts, sub-assemblies, instances)."""
        path = build_path(ids, prefix=self._path_prefix)
        params = {}
        if include_mate_features:
            params['includeMateFeatures'] = 'true'
        if include_non_solids:
            params['includeNonSolids'] = 'true'
        r = self.client.get_model(
            path,
            model=Assembly,
            **params,
        )
        return r
