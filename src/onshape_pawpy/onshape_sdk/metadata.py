"""Metadata API — custom properties on elements and parts."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Optional

from .api_version import API_VERSION_PATH
from .types import MetadataProperty
from .utils import build_wvm_path

if TYPE_CHECKING:
    from .client import OnshapeClient


class MetadataApi:
    """Endpoints under ``/{API_VERSION_PATH}/metadata``."""

    def __init__(self, client: "OnshapeClient") -> None:
        self._c = client

    def get(
        self,
        did: str,
        wvm: str,
        wvm_id: str,
        eid: str,
        *,
        part_id: Optional[str] = None,
    ) -> list[MetadataProperty]:
        """Get metadata properties for an element or specific part.

        Parameters
        ----------
        part_id : str, optional
            If given, return metadata for that specific part within the element.
        """
        base = f"{API_VERSION_PATH}/metadata{build_wvm_path(did, wvm, wvm_id, eid)}"
        if part_id:
            base += f"/p/{part_id}"
        r = self._c.get(base)
        r.raise_for_status()
        data = r.json()
        props = data.get("properties", data if isinstance(data, list) else [])
        return [MetadataProperty.from_dict(p) for p in props if isinstance(p, dict)]

    def update(
        self,
        did: str,
        wvm: str,
        wvm_id: str,
        eid: str,
        properties: list[dict],
        *,
        part_id: Optional[str] = None,
    ) -> dict[str, Any]:
        """Update metadata properties.

        Parameters
        ----------
        properties : list[dict]
            Each dict should have ``propertyId`` and ``value``.
        """
        base = f"{API_VERSION_PATH}/metadata{build_wvm_path(did, wvm, wvm_id, eid)}"
        if part_id:
            base += f"/p/{part_id}"
        r = self._c.post(base, body={"properties": properties})
        r.raise_for_status()
        return r.json()
