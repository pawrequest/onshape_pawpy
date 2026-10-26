"""Translations API — async CAD format export/import with polling.

This is the most important module for exporting STEP, DXF, PDF, DWG, IGES,
STL (high-quality), and other formats from Onshape.
"""

from __future__ import annotations

import time
from typing import TYPE_CHECKING, Any, Optional

import requests as _requests

from .api_version import API_VERSION_PATH
from .types import TranslationStatus
from .utils import build_wvm_path

if TYPE_CHECKING:
    from .client import OnshapeClient


class TranslationError(Exception):
    """Raised when a translation job fails or times out."""

    def __init__(self, status: TranslationStatus, message: str = "") -> None:
        self.status = status
        super().__init__(message or f"Translation {status.id} failed: {status.failure_reason}")


class TranslationsApi:
    """Async export/import engine under ``/{API_VERSION_PATH}/…/translations``."""

    # Supported format names (non-exhaustive)
    FORMATS = (
        "STEP", "IGES", "STL", "PARASOLID", "ACIS",
        "DXF", "DWG", "PDF",
        "SOLIDWORKS", "RHINO", "OBJ", "GLTF",
        "CATIA", "CATIA_V4", "JT", "3MF",
    )

    # Element-type to path segment
    _ELEMENT_TYPES = {
        "partstudios": "partstudios",
        "partstudio": "partstudios",
        "assemblies": "assemblies",
        "assembly": "assemblies",
        "drawings": "drawings",
        "drawing": "drawings",
        "blobelements": "blobelements",
        "blob": "blobelements",
    }

    def __init__(self, client: "OnshapeClient") -> None:
        self._c = client

    # ── Core ──────────────────────────────────────────────────────────────────

    def create(
        self,
        did: str,
        wvm: str,
        wvm_id: str,
        eid: str,
        format_name: str,
        *,
        element_type: str = "partstudios",
        part_ids: Optional[list[str]] = None,
        store_in_document: bool = False,
        link_document_id: Optional[str] = None,
        configuration: Optional[str] = None,
        **extra_body: Any,
    ) -> TranslationStatus:
        """Create a translation (export) job.

        Parameters
        ----------
        format_name : str
            Target format, e.g. ``"STEP"``, ``"DXF"``, ``"PDF"``.
        element_type : str
            One of ``"partstudios"``, ``"assemblies"``, ``"drawings"``, ``"blobelements"``.
        part_ids : list[str], optional
            Restrict export to specific part IDs.
        store_in_document : bool
            If True the result is stored as a blob element in the document.
        """
        seg = self._ELEMENT_TYPES.get(element_type.lower(), element_type.lower())
        path = f"{API_VERSION_PATH}/{seg}{build_wvm_path(did, wvm, wvm_id, eid)}/translations"

        body: dict = {
            "formatName": format_name.upper(),
            "storeInDocument": store_in_document,
            **extra_body,
        }
        if part_ids:
            body["partIds"] = part_ids
        if link_document_id:
            body["linkDocumentId"] = link_document_id
        if configuration:
            body["configuration"] = configuration

        r = self._c.post(path, body=body)
        r.raise_for_status()
        return TranslationStatus.from_dict(r.json())

    def get_status(self, translation_id: str) -> TranslationStatus:
        """Poll the status of a translation job."""
        r = self._c.get(f"{API_VERSION_PATH}/translations/{translation_id}")
        r.raise_for_status()
        return TranslationStatus.from_dict(r.json())

    def wait(
        self,
        translation_id: str,
        *,
        timeout: float = 120,
        poll_interval: float = 3,
        verbose: bool = False,
    ) -> TranslationStatus:
        """Block until a translation job completes or fails.

        Parameters
        ----------
        timeout : float
            Maximum seconds to wait.
        poll_interval : float
            Seconds between status polls.
        verbose : bool
            Print progress to stdout.

        Raises
        ------
        TranslationError
            If the job fails or the timeout is exceeded.
        """
        deadline = time.monotonic() + timeout
        status = self.get_status(translation_id)

        while status.is_active and time.monotonic() < deadline:
            if verbose:
                print(f"  translation {translation_id[:12]}… → {status.request_state}"
                      f" ({status.progress:.0f}%)")
            time.sleep(poll_interval)
            status = self.get_status(translation_id)

        if status.is_failed:
            raise TranslationError(status)
        if status.is_active:
            raise TranslationError(
                status, f"Translation {translation_id} timed out after {timeout}s"
            )
        if verbose:
            print(f"  translation {translation_id[:12]}… → DONE")
        return status

    def download(self, did: str, external_data_id: str) -> bytes:
        """Download the binary result of a completed translation.

        Handles the S3 redirect that Onshape typically returns.
        """
        path = f"{API_VERSION_PATH}/documents/d/{did}/externaldata/{external_data_id}"
        r = self._c.get(path, accept="application/octet-stream")
        # Onshape often 302-redirects to an S3 signed URL
        if r.status_code in (301, 302, 303, 307, 308):
            r = _requests.get(r.headers["Location"])
        r.raise_for_status()
        return r.content

    # ── High-level convenience ────────────────────────────────────────────────

    def export(
        self,
        did: str,
        wvm: str,
        wvm_id: str,
        eid: str,
        format_name: str,
        *,
        output_path: Optional[str] = None,
        element_type: str = "partstudios",
        part_ids: Optional[list[str]] = None,
        timeout: float = 120,
        poll_interval: float = 3,
        verbose: bool = False,
        **extra_body: Any,
    ) -> bytes:
        """All-in-one: create translation → poll → download → optionally save.

        Parameters
        ----------
        output_path : str, optional
            If given, write the exported bytes to this file path.

        Returns
        -------
        bytes
            The raw exported file content.
        """
        status = self.create(
            did, wvm, wvm_id, eid, format_name,
            element_type=element_type,
            part_ids=part_ids,
            store_in_document=False,
            **extra_body,
        )
        status = self.wait(
            status.id,
            timeout=timeout,
            poll_interval=poll_interval,
            verbose=verbose,
        )
        if not status.result_external_data_ids:
            raise TranslationError(
                status, "Translation completed but returned no downloadable data."
            )
        data = self.download(did, status.result_external_data_ids[0])
        if output_path:
            with open(output_path, "wb") as f:
                f.write(data)
            if verbose:
                print(f"  saved → {output_path} ({len(data)} bytes)")
        return data
