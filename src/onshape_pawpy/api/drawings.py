"""Drawings API — views and export helpers."""

from __future__ import annotations

from typing import Any, TYPE_CHECKING, cast

from api.api_base import ApiBase
from ids import OnshapeIds
from onshape_sdk import DrawingView

if TYPE_CHECKING:
    from .client import OnshapeClient


class DrawingsApi(ApiBase):
    """Endpoints under ``/{API_VERSION_PATH}/drawings``."""

    _path_prefix = '/drawings'

    def __init__(self, client: 'OnshapeClient') -> None:
        self._c = client

    def get_views(self, ids: OnshapeIds) -> list[DrawingView]:
        """List all views in the drawing."""
        suffix = '/views'
        path = self.build_path(ids, suffix=suffix)
        data = self._c.get(path)
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
