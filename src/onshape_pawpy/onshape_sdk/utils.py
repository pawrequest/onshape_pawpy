"""Utility helpers for working with Onshape URLs and IDs."""

from __future__ import annotations

import re
from typing import TypedDict

from onshape_sdk.api_version import API_VERSION_PATH
from onshape_sdk.ids import OnshapeLoc


class OnshapeIds(TypedDict):
    """IDs parsed from an Onshape document URL."""

    did: str  # document ID
    wvm_type: str  # 'w' (workspace), 'v' (version), or 'm' (microversion)
    wvm_id: str  # workspace / version / microversion ID
    eid: str  # element ID


def parse_onshape_url(url: str) -> OnshapeIds:
    """Extract document, workspace/version/microversion, and element IDs from an Onshape URL.

    Parameters
    ----------
    url : str
        Full Onshape URL, e.g.
        ``https://cad.onshape.com/documents/<did>/w/<wid>/e/<eid>``

    Returns
    -------
    OnshapeIds
        Dict with keys ``did``, ``wvm_type``, ``wvm_id``, ``eid``.

    Raises
    ------
    ValueError
        If the URL doesn't match the expected Onshape pattern.
    """
    pattern = r'documents/([a-f0-9]+)/([wvm])/([a-f0-9]+)/e/([a-f0-9]+)'
    match = re.search(pattern, url)
    if not match:
        raise ValueError(
            'Could not parse Onshape URL. Expected format:\n'
            'https://cad.onshape.com/documents/<did>/<w|v|m>/<wid>/e/<eid>'
        )
    did, wvm_type, wvm_id, eid = match.groups()
    return OnshapeIds(did=did, wvm_type=wvm_type, wvm_id=wvm_id, eid=eid)


def build_wvm_path(
    did: str,
    wvm: str,
    wvm_id: str,
    eid: str | None = None,
) -> str:
    """Build the ``/d/{did}/{wvm}/{wvm_id}[/e/{eid}]`` path fragment.

    Parameters
    ----------
    did : str
        Document ID.
    wvm : str
        One of ``'w'``, ``'v'``, ``'m'``.
    wvm_id : str
        Workspace / version / microversion ID.
    eid : str, optional
        Element ID.  If *None* the ``/e/…`` suffix is omitted.
    """
    path = f'/d/{did}/{wvm}/{wvm_id}'
    if eid:
        path += f'/e/{eid}'
    return path


def build_full_wvm_path_tup(ids_tup: OnshapeLoc, prefix: str = '', suffix: str = '') -> str:
    """Build the ``/d/{did}/{wvm}/{wvm_id}[/e/{eid}]`` path fragment."""
    did, wvm, wvm_id, eid = ids_tup
    path = f'{API_VERSION_PATH}{prefix}/d/{did}/{wvm}/{wvm_id}'
    if eid:
        path += f'/e/{eid}'
    if suffix:
        path += suffix
    return path
