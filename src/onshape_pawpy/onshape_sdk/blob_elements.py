"""Blob Elements API — upload and download binary files."""

from __future__ import annotations

import os
from typing import TYPE_CHECKING, Optional

import requests as _requests

from .api_version import API_VERSION_PATH
from .types import Element
from .utils import build_wvm_path

if TYPE_CHECKING:
    from .client import OnshapeClient


class BlobElementsApi:
    """Endpoints under ``/{API_VERSION_PATH}/blobelements``."""

    _BASE = f"{API_VERSION_PATH}/blobelements"

    def __init__(self, client: "OnshapeClient") -> None:
        self._c = client

    def download(
        self,
        did: str,
        wvm: str,
        wvm_id: str,
        eid: str,
    ) -> bytes:
        """Download the raw contents of a blob element.

        Handles the S3 redirect that Onshape typically returns.
        """
        path = f"{self._BASE}{build_wvm_path(did, wvm, wvm_id, eid)}"
        r = self._c.get(path, accept="application/octet-stream")
        if r.status_code in (301, 302, 303, 307, 308):
            r = _requests.get(r.headers["Location"])
        r.raise_for_status()
        return r.content

    def upload(
        self,
        did: str,
        wid: str,
        file_path: str,
        *,
        content_type: Optional[str] = None,
    ) -> Element:
        """Upload a file as a new blob element in the document.

        Parameters
        ----------
        file_path : str
            Local file to upload.
        content_type : str, optional
            MIME type.  Auto-detected from extension if not given.
        """
        if not content_type:
            import mimetypes
            content_type = mimetypes.guess_type(file_path)[0] or "application/octet-stream"

        filename = os.path.basename(file_path)
        path = f"{self._BASE}/d/{did}/w/{wid}"

        # Build multipart headers manually since Onshape expects
        # the HMAC to be signed with application/json content type
        # but the actual upload is multipart
        headers = self._c._sign("POST", path, content_type="application/json")
        del headers["Content-Type"]  # let requests set the multipart boundary

        with open(file_path, "rb") as f:
            files = {"file": (filename, f, content_type)}
            url = self._c.base_url + path
            r = _requests.post(url, headers=headers, files=files)

        r.raise_for_status()
        return Element.from_dict(r.json())
