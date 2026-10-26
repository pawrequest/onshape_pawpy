"""Webhooks API — event-driven notifications."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Optional, List

from .api_version import API_VERSION_PATH
from .types import Webhook

if TYPE_CHECKING:
    from .client import OnshapeClient


class WebhooksApi:
    """Endpoints under ``/{API_VERSION_PATH}/webhooks``."""

    # Common event types
    EVENTS = (
        "onshape.model.lifecycle.changed",
        "onshape.model.translation.complete",
        "onshape.document.lifecycle.statechange",
        "onshape.workflow.transition",
        "onshape.comment.create",
        "onshape.revision.created",
    )

    def __init__(self, client: "OnshapeClient") -> None:
        self._c = client

    def list(self) -> list[Webhook]:
        """List all webhooks owned by the current user."""
        r = self._c.get("{API_VERSION_PATH}/webhooks")
        r.raise_for_status()
        data = r.json()
        items = data.get("items", data if isinstance(data, list) else [])
        return [Webhook.from_dict(w) for w in items if isinstance(w, dict)]

    def create(
        self,
        url: str,
        events: List[str],
        *,
        filter: Optional[str] = None,
        options: Optional[dict] = None,
    ) -> Webhook:
        """Register a new webhook.

        Parameters
        ----------
        url : str
            Your callback endpoint (must be HTTPS).
        events : list[str]
            Event types to subscribe to (see ``WebhooksApi.EVENTS``).
        filter : str, optional
            Onshape filter expression, e.g. ``"documentId=abc123"``.
        options : dict, optional
            Additional webhook options (``collapseEvents``, etc.).
        """
        body: dict[str, Any] = {"url": url, "events": events}
        if filter:
            body["filter"] = filter
        if options:
            body["options"] = options
        r = self._c.post("{API_VERSION_PATH}/webhooks", body=body)
        r.raise_for_status()
        return Webhook.from_dict(r.json())

    def get(self, webhook_id: str) -> Webhook:
        """Get details of a specific webhook."""
        r = self._c.get(f"{API_VERSION_PATH}/webhooks/{webhook_id}")
        r.raise_for_status()
        return Webhook.from_dict(r.json())

    def update(
        self,
        webhook_id: str,
        *,
        url: Optional[str] = None,
        events: Optional[List[str]] = None,
        filter: Optional[str] = None,
        options: Optional[dict] = None,
    ) -> Webhook:
        """Update an existing webhook."""
        body: dict[str, Any] = {}
        if url is not None:
            body["url"] = url
        if events is not None:
            body["events"] = events
        if filter is not None:
            body["filter"] = filter
        if options is not None:
            body["options"] = options
        r = self._c.post(f"{API_VERSION_PATH}/webhooks/{webhook_id}", body=body)
        r.raise_for_status()
        return Webhook.from_dict(r.json())

    def delete(self, webhook_id: str) -> None:
        """Delete a webhook."""
        r = self._c.delete(f"{API_VERSION_PATH}/webhooks/{webhook_id}")
        r.raise_for_status()
