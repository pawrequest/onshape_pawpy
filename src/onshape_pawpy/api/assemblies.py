"""Assemblies API — definitions, BOM, occurrences, mates."""

from __future__ import annotations

from typing import Any, Optional, TYPE_CHECKING

from ids import OnshapeIds
from onshape_sdk import AssemblyDefinition, BomTable, MateFeature, Occurrence
from .api_base import ApiBase

if TYPE_CHECKING:
    pass


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
    ) -> AssemblyDefinition:
        """Get the full assembly definition (parts, sub-assemblies, instances)."""
        params: dict = {}
        suffix = '/definition'
        r = self.get(ids=ids, suffix=suffix, query_params=params or None)
        if not isinstance(r, dict):
            raise TypeError('wrong type')
        return AssemblyDefinition.from_dict(r)

    # ── BOM ───────────────────────────────────────────────────────────────────

    def get_bom(
            self,
            ids: OnshapeIds,
            *,
            indented: bool = True,
            multi_level: bool = True,
    ) -> BomTable:
        """Get the Bill of Materials for the assembly."""
        params: dict = {
            "indented": str(indented).lower(),
            "multiLevel": str(multi_level).lower(),
        }
        suffix = '/bom'
        r = self.get_json(ids, suffix=suffix, query_params=params)
        return BomTable.from_dict(r)

    # ── Features (mates) ─────────────────────────────────────────────────────

    def get_features(
            self,
            ids: OnshapeIds
    ) -> list[MateFeature]:
        """Get mate features in the assembly."""
        suffix = "/features"
        data = self.get_json(ids, suffix=suffix)
        raw = data.get("features", data if isinstance(data, list) else [])
        return [MateFeature.from_dict(f) for f in raw if isinstance(f, dict)]

    # ── Occurrences ──────────────────────────────────────────────────────────

    def get_occurrences(
            self,
            ids: OnshapeIds
    ) -> list[Occurrence]:
        """List all part occurrences with their transforms."""
        suffix = '/occurrences'
        r = self.get_json(ids, suffix=suffix)
        if not isinstance(r, list):
            raise TypeError('Wrong type')
        return [Occurrence.from_dict(o) for o in r]

    # ── Write operations ─────────────────────────────────────────────────────

    def insert_instance(
            self,
            did: str,
            wid: str,
            eid: str,
            *,
            document_id: str,
            element_id: str,
            part_id: Optional[str] = None,
            version_id: Optional[str] = None,
            is_assembly: bool = False,
    ) -> dict[str, Any]:
        """Insert a part or sub-assembly instance into the assembly."""
        body: dict = {
            "documentId": document_id,
            "elementId": element_id,
            "isAssembly": is_assembly,
        }
        if part_id:
            body["partId"] = part_id
        if version_id:
            body["versionId"] = version_id
        r = self._c.post(
            f"{self._path(did, 'w', wid, eid)}/instances",
            body=body,
        )
        r.raise_for_status()
        return r.json()

    def transform_occurrences(
            self,
            did: str,
            wid: str,
            eid: str,
            transforms: list[dict],
    ) -> dict[str, Any]:
        """Apply transforms to occurrences.

        Parameters
        ----------
        transforms : list[dict]
            Each dict should contain ``path`` (list[str]) and ``transform``
            (list[float] — 16-element row-major 4×4 matrix).
        """
        r = self._c.post(
            f"{self._path(did, 'w', wid, eid)}/occurrencetransforms",
            body={"occurrences": transforms, "isRelative": True},
        )
        r.raise_for_status()
        return r.json()
