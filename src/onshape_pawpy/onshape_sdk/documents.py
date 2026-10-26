"""Documents API — create, list, search, and manage Onshape documents."""

from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from .api_version import API_VERSION_PATH, ApiBase
from .types import Document, DocumentVersion, Element, PaginatedList, Workspace
from .utils import build_wvm_path

if TYPE_CHECKING:
    from .client_og import OnshapeClient


class DocumentsApi(ApiBase):
    """Endpoints under ``/{API_VERSION_PATH}/documents``."""
    _path_prefix = '/documents'


    def __init__(self, client: "OnshapeClient") -> None:
        self._c = client

    # ── Read ──────────────────────────────────────────────────────────────────

    def list(
        self,
        *,
        owner_type: int = 0,
        limit: int = 20,
        offset: int = 0,
        sort_column: str = "modifiedAt",
        sort_order: str = "desc",
    ) -> PaginatedList[Document]:
        """List documents accessible to the current user.

        Parameters
        ----------
        owner_type : int
            0 = owned by me, 1 = created by me, 2 = shared with me, …
        """
        r = self._c.get(
            f"{API_VERSION_PATH}/documents",
            query_params={
                "filter": owner_type,
                "limit": limit,
                "offset": offset,
                "sortColumn": sort_column,
                "sortOrder": sort_order,
            },
        )
        r.raise_for_status()
        return PaginatedList.from_dict(r.json(), Document)

    def get(self, did: str) -> Document:
        """Get a single document by ID."""
        r = self._c.get(f"{API_VERSION_PATH}/documents/{did}")
        r.raise_for_status()
        return Document.from_dict(r.json())

    def search(
        self,
        query: str,
        *,
        limit: int = 20,
        offset: int = 0,
    ) -> PaginatedList[Document]:
        """Full-text search across documents."""
        r = self._c.post(
            f"{API_VERSION_PATH}/documents/search",
            body={"rawQuery": query, "limit": limit, "offset": offset},
        )
        r.raise_for_status()
        return PaginatedList.from_dict(r.json(), Document)

    # ── Elements / Versions / Workspaces ──────────────────────────────────────

    def get_elements(
        self, did: str, wvm: str, wvm_id: str
    ) -> list[Element]:
        """List all elements (tabs) in a document workspace/version."""
        path = f"{API_VERSION_PATH}/documents{build_wvm_path(did, wvm, wvm_id)}/elements"
        r = self._c.get(path)
        r.raise_for_status()
        return [Element.from_dict(e) for e in r.json()]

    def get_versions(self, did: str) -> list[DocumentVersion]:
        """List all versions of a document."""
        r = self._c.get(f"{API_VERSION_PATH}/documents/d/{did}/versions")
        r.raise_for_status()
        return [DocumentVersion.from_dict(v) for v in r.json()]

    def get_workspaces(self, did: str) -> list[Workspace]:
        """List workspaces (branches) of a document."""
        r = self._c.get(f"{API_VERSION_PATH}/documents/d/{did}/workspaces")
        r.raise_for_status()
        return [Workspace.from_dict(w) for w in r.json()]

    # ── Write ─────────────────────────────────────────────────────────────────

    def create(
        self,
        name: str,
        *,
        description: str = "",
        owner_id: Optional[str] = None,
        owner_type: Optional[int] = None,
        is_public: bool = False,
    ) -> Document:
        """Create a new empty document."""
        body: dict = {"name": name, "isPublic": is_public}
        if description:
            body["description"] = description
        if owner_id:
            body["ownerId"] = owner_id
        if owner_type is not None:
            body["ownerType"] = owner_type
        r = self._c.post("{API_VERSION_PATH}/documents", body=body)
        r.raise_for_status()
        return Document.from_dict(r.json())

    def create_version(
        self,
        did: str,
        wid: str,
        name: str,
        *,
        description: str = "",
    ) -> DocumentVersion:
        """Create a named version from the current workspace state."""
        body: dict = {"name": name, "documentId": did, "workspaceId": wid}
        if description:
            body["description"] = description
        r = self._c.post(f"{API_VERSION_PATH}/documents/d/{did}/versions", body=body)
        r.raise_for_status()
        return DocumentVersion.from_dict(r.json())

    def delete(self, did: str, *, forever: bool = False) -> None:
        """Move a document to trash (or delete permanently if *forever*)."""
        r = self._c.delete(
            f"{API_VERSION_PATH}/documents/{did}",
            query_params={"forever": str(forever).lower()} if forever else None,
        )
        r.raise_for_status()
