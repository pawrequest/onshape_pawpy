"""Part Studios API — features, variables, configuration, and direct exports."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Optional

from .api_version import API_VERSION_PATH
from .types import Feature, Variable
from .utils import build_wvm_path

if TYPE_CHECKING:
    from .client_og import OnshapeClient


class PartStudiosApi:
    """Endpoints under ``/{API_VERSION_PATH}/partstudios``."""

    _BASE = f"{API_VERSION_PATH}/partstudios"

    def __init__(self, client: "OnshapeClient") -> None:
        self._c = client

    def _path(self, did: str, wvm: str, wvm_id: str, eid: str) -> str:
        return f"{self._BASE}{build_wvm_path(did, wvm, wvm_id, eid)}"

    # ── Features ──────────────────────────────────────────────────────────────

    def get_features(
        self, did: str, wvm: str, wvm_id: str, eid: str
    ) -> list[Feature]:
        """List all features in the Part Studio feature tree."""
        r = self._c.get(f"{self._path(did, wvm, wvm_id, eid)}/features")
        r.raise_for_status()
        data = r.json()
        features_raw = data.get("features", data if isinstance(data, list) else [])
        return [Feature.from_dict(f) for f in features_raw if isinstance(f, dict)]

    def add_feature(
        self,
        did: str,
        wid: str,
        eid: str,
        feature: dict,
    ) -> Feature:
        """Add a feature to the Part Studio (workspace only)."""
        r = self._c.post(
            f"{self._path(did, 'w', wid, eid)}/features",
            body={"feature": feature},
        )
        r.raise_for_status()
        return Feature.from_dict(r.json().get("feature", r.json()))

    def update_feature(
        self,
        did: str,
        wid: str,
        eid: str,
        feature_id: str,
        feature: dict,
    ) -> Feature:
        """Update an existing feature."""
        r = self._c.post(
            f"{self._path(did, 'w', wid, eid)}/features/featureid/{feature_id}",
            body={"feature": feature},
        )
        r.raise_for_status()
        return Feature.from_dict(r.json().get("feature", r.json()))

    def delete_feature(
        self,
        did: str,
        wid: str,
        eid: str,
        feature_id: str,
    ) -> None:
        """Delete a feature from the Part Studio."""
        r = self._c.delete(
            f"{self._path(did, 'w', wid, eid)}/features/featureid/{feature_id}"
        )
        r.raise_for_status()

    # ── Variables ─────────────────────────────────────────────────────────────

    def get_variables(
        self, did: str, wvm: str, wvm_id: str, eid: str
    ) -> list[Variable]:
        """Get all variables defined in the Part Studio."""
        r = self._c.get(f"{self._path(did, wvm, wvm_id, eid)}/variables")
        r.raise_for_status()
        data = r.json()
        items = data if isinstance(data, list) else data.get("variables", [])
        return [Variable.from_dict(v) for v in items if isinstance(v, dict)]

    def set_variables(
        self,
        did: str,
        wid: str,
        eid: str,
        variables: list[dict],
    ) -> list[Variable]:
        """Set variable values (workspace only).

        Parameters
        ----------
        variables : list[dict]
            Each dict should have at least ``name`` and ``value`` / ``expression``.
        """
        r = self._c.post(
            f"{self._path(did, 'w', wid, eid)}/variables",
            body=variables,
        )
        r.raise_for_status()
        data = r.json()
        items = data if isinstance(data, list) else data.get("variables", [])
        return [Variable.from_dict(v) for v in items if isinstance(v, dict)]

    # ── Configuration ─────────────────────────────────────────────────────────

    def get_configuration(
        self, did: str, wvm: str, wvm_id: str, eid: str
    ) -> dict[str, Any]:
        """Get the configuration definition for the Part Studio."""
        r = self._c.get(f"{self._path(did, wvm, wvm_id, eid)}/configuration")
        r.raise_for_status()
        return r.json()

    # ── FeatureScript ─────────────────────────────────────────────────────────

    def evaluate_featurescript(
        self,
        did: str,
        wvm: str,
        wvm_id: str,
        eid: str,
        script: str,
        *,
        queries: Optional[dict] = None,
    ) -> dict[str, Any]:
        """Evaluate a FeatureScript expression against the Part Studio.

        Parameters
        ----------
        script : str
            FeatureScript source code to evaluate.
        queries : dict, optional
            Named geometric queries to bind.
        """
        body: dict = {"script": script}
        if queries:
            body["queries"] = queries
        r = self._c.post(
            f"{self._path(did, wvm, wvm_id, eid)}/featurescript",
            body=body,
        )
        r.raise_for_status()
        return r.json()

    # ── Direct binary exports ─────────────────────────────────────────────────

    def _export(
        self,
        did: str,
        wvm: str,
        wvm_id: str,
        eid: str,
        suffix: str,
        part_ids: Optional[str | list[str]] = None,
        **extra_params: Any,
    ) -> bytes:
        """Generic helper for ``/export*`` binary endpoints."""
        params: dict = dict(extra_params)
        path = f"{self._path(did, wvm, wvm_id, eid)}/{suffix}"
        if part_ids:
            if isinstance(part_ids, list):
                part_ids = ",".join(part_ids)
            params["partIds"] = part_ids
        r = self._c.get(
            path,
            query_params=params or None,
            accept="application/octet-stream",
        )
        r.raise_for_status()
        return r.content

    def export_stl(
        self,
        did: str,
        wvm: str,
        wvm_id: str,
        eid: str,
        *,
        part_ids: Optional[str | list[str]] = None,
        mode: str = "bytes",
        units: str = "millimeter",
        angle_tolerance: float = 0.1090830782496456,
        chord_tolerance: float = 0.010000000000000002,
    ) -> bytes:
        """Export STL mesh data."""
        return self._export(
            did, wvm, wvm_id, eid, "stl",
            part_ids=part_ids,
            mode=mode,
            units=units,
            # angleTolerance=angle_tolerance,
            # chordTolerance=chord_tolerance,
        )

    def export_parasolid(
        self,
        did: str,
        wvm: str,
        wvm_id: str,
        eid: str,
        *,
        part_ids: Optional[str | list[str]] = None,
        version: str = "0",
    ) -> bytes:
        """Export Parasolid (.x_t) data."""
        return self._export(
            did, wvm, wvm_id, eid, "exportparasolid",
            part_ids=part_ids,
            version=version,
        )

    def export_dxf(
        self,
        did: str,
        wvm: str,
        wvm_id: str,
        eid: str,
        *,
        part_ids: Optional[str | list[str]] = None,
    ) -> bytes:
        """Export DXF (works best for flat / sheet-metal parts)."""
        return self._export(
            did, wvm, wvm_id, eid, "exportdxf",
            part_ids=part_ids,
        )
