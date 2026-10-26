"""Parts API — list and inspect individual parts within a Part Studio."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Optional

from .api_version import API_VERSION_PATH
from .types import Part
from .utils import build_wvm_path

if TYPE_CHECKING:
    from .client import OnshapeClient


class PartsApi:
    """Endpoints under ``/{API_VERSION_PATH}/parts``."""

    def __init__(self, client: "OnshapeClient") -> None:
        self._c = client

    def list(
        self,
        did: str,
        wvm: str,
        wvm_id: str,
        eid: str,
    ) -> list[Part]:
        """List all parts in a Part Studio element."""
        path = f"{API_VERSION_PATH}/parts{build_wvm_path(did, wvm, wvm_id, eid)}"
        r = self._c.get(path)
        r.raise_for_status()
        return [Part.from_dict(p) for p in r.json()]

    def get(
        self,
        did: str,
        wvm: str,
        wvm_id: str,
        eid: str,
        part_id: str,
    ) -> Part:
        """Get metadata for a single part."""
        path = f"{API_VERSION_PATH}/parts{build_wvm_path(did, wvm, wvm_id, eid)}/partid/{part_id}"
        r = self._c.get(path)
        r.raise_for_status()
        data = r.json()
        # API may return a list with one item or a dict
        if isinstance(data, list):
            data = data[0]
        return Part.from_dict(data)

    def get_mass_properties(
        self,
        did: str,
        wvm: str,
        wvm_id: str,
        eid: str,
        *,
        part_id: Optional[str] = None,
    ) -> dict[str, Any]:
        """Get mass properties (volume, mass, centroid, inertia) for parts.

        Returns the raw JSON dict — the structure varies by part count.
        """
        path = f"{API_VERSION_PATH}/parts{build_wvm_path(did, wvm, wvm_id, eid)}/massproperties"
        params: dict = {}
        if part_id:
            params["partId"] = part_id
        r = self._c.get(path, query_params=params or None)
        r.raise_for_status()
        return r.json()

    def get_body_details(
        self,
        did: str,
        wvm: str,
        wvm_id: str,
        eid: str,
        *,
        part_id: Optional[str] = None,
    ) -> dict[str, Any]:
        """Get topological body details (faces, edges, vertices)."""
        path = f"{API_VERSION_PATH}/parts{build_wvm_path(did, wvm, wvm_id, eid)}/bodydetails"
        params: dict = {}
        if part_id:
            params["partId"] = part_id
        r = self._c.get(path, query_params=params or None)
        r.raise_for_status()
        return r.json()

    def get_bounding_boxes(
        self,
        did: str,
        wvm: str,
        wvm_id: str,
        eid: str,
        *,
        part_id: Optional[str] = None,
    ) -> dict[str, Any]:
        """Get axis-aligned bounding boxes for parts."""
        path = f"{API_VERSION_PATH}/parts{build_wvm_path(did, wvm, wvm_id, eid)}/boundingboxes"
        params: dict = {}
        if part_id:
            params["partId"] = part_id
        r = self._c.get(path, query_params=params or None)
        r.raise_for_status()
        return r.json()
