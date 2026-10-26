"""Assemblies API — definitions, BOM, occurrences, mates."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Optional

from .api_version import API_VERSION_PATH
from .types import AssemblyDefinition, BomTable, MateFeature, Occurrence
from .utils import build_wvm_path

if TYPE_CHECKING:
    from .client import OnshapeClient


class AssembliesApi:
    """Endpoints under ``/{API_VERSION_PATH}/assemblies``."""

    _BASE = f"{API_VERSION_PATH}/assemblies"

    def __init__(self, client: "OnshapeClient") -> None:
        self._c = client

    def _path(self, did: str, wvm: str, wvm_id: str, eid: str) -> str:
        return f"{self._BASE}{build_wvm_path(did, wvm, wvm_id, eid)}"

    # ── Definition ────────────────────────────────────────────────────────────

    def get_definition(
        self,
        did: str,
        wvm: str,
        wvm_id: str,
        eid: str,
        *,
        include_mate_features: bool = False,
        include_non_solids: bool = False,
    ) -> AssemblyDefinition:
        """Get the full assembly definition (parts, sub-assemblies, instances)."""
        params: dict = {}
        if include_mate_features:
            params["includeMateFeatures"] = "true"
        if include_non_solids:
            params["includeNonSolids"] = "true"
        r = self._c.get(
            f"{self._path(did, wvm, wvm_id, eid)}/definition",
            query_params=params or None,
        )
        r.raise_for_status()
        return AssemblyDefinition.from_dict(r.json())

    # ── BOM ───────────────────────────────────────────────────────────────────

    def get_bom(
        self,
        did: str,
        wvm: str,
        wvm_id: str,
        eid: str,
        *,
        indented: bool = True,
        multi_level: bool = True,
    ) -> BomTable:
        """Get the Bill of Materials for the assembly."""
        params: dict = {
            "indented": str(indented).lower(),
            "multiLevel": str(multi_level).lower(),
        }
        r = self._c.get(
            f"{self._path(did, wvm, wvm_id, eid)}/bom",
            query_params=params,
        )
        r.raise_for_status()
        return BomTable.from_dict(r.json())

    # ── Features (mates) ─────────────────────────────────────────────────────

    def get_features(
        self,
        did: str,
        wvm: str,
        wvm_id: str,
        eid: str,
    ) -> list[MateFeature]:
        """Get mate features in the assembly."""
        r = self._c.get(f"{self._path(did, wvm, wvm_id, eid)}/features")
        r.raise_for_status()
        data = r.json()
        raw = data.get("features", data if isinstance(data, list) else [])
        return [MateFeature.from_dict(f) for f in raw if isinstance(f, dict)]

    # ── Occurrences ──────────────────────────────────────────────────────────

    def get_occurrences(
        self,
        did: str,
        wvm: str,
        wvm_id: str,
        eid: str,
    ) -> list[Occurrence]:
        """List all part occurrences with their transforms."""
        r = self._c.get(f"{self._path(did, wvm, wvm_id, eid)}/occurrences")
        r.raise_for_status()
        return [Occurrence.from_dict(o) for o in r.json()]

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
