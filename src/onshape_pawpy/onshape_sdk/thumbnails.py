"""Thumbnails API — preview images of documents and elements."""

from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from .api_version import API_VERSION_PATH
from .types import ThumbnailInfo
from .utils import build_wvm_path

if TYPE_CHECKING:
    from .client import OnshapeClient


class ThumbnailsApi:
    """Endpoints under ``/{API_VERSION_PATH}/thumbnails``."""

    def __init__(self, client: "OnshapeClient") -> None:
        self._c = client

    def get_info(
        self,
        did: str,
        wvm: str,
        wvm_id: str,
        *,
        eid: Optional[str] = None,
    ) -> ThumbnailInfo:
        """Get available thumbnail sizes for a document or element.

        Parameters
        ----------
        eid : str, optional
            If provided, get thumbnails for a specific element; otherwise
            the document-level thumbnail is returned.
        """
        path = f"{API_VERSION_PATH}/thumbnails{build_wvm_path(did, wvm, wvm_id, eid)}"
        r = self._c.get(path)
        r.raise_for_status()
        return ThumbnailInfo.from_dict(r.json())

    def download(
        self,
        did: str,
        wvm: str,
        wvm_id: str,
        *,
        size: str = "300x300",
        eid: Optional[str] = None,
    ) -> bytes:
        """Download a thumbnail image as PNG bytes.

        Parameters
        ----------
        size : str
            Desired size, e.g. ``"70x40"``, ``"300x300"``, ``"600x340"``.
        """
        path = f"{API_VERSION_PATH}/thumbnails{build_wvm_path(did, wvm, wvm_id, eid)}/s/{size}"
        r = self._c.get(path, accept="image/png")
        r.raise_for_status()
        return r.content
