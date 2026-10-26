"""Drawings API — views and export helpers."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, cast

from onshape_sdk import DrawingView

from ..path import OnshapeIds
from .api_base import ApiBase

if TYPE_CHECKING:
    pass


class DrawingsApi(ApiBase):
    """Endpoints under ``/{API_VERSION_PATH}/drawings``."""

    _path_prefix = '/drawings'

    def get_views(self, ids: OnshapeIds) -> list[DrawingView]:
        """List all views in the drawing."""
        suffix = '/views'
        data = self.get(ids, suffix=suffix)
        items = data if isinstance(data, list) else data.get('views', [])
        return [DrawingView.from_dict(v) for v in items if isinstance(v, dict)]

    def get_view_geometry(
        self,
        ids: OnshapeIds,
        view_id: str,
    ) -> dict[str, Any]:
        """Get the JSON geometry for a specific drawing view."""
        suffix = f'/views/{view_id}/jsongeometry'
        r = self.get(ids, suffix=suffix)
        return cast(dict[str, Any], r)
