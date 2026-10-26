"""Typed dataclasses for Onshape API responses.

Every type has a ``from_dict`` classmethod that safely builds an instance from
a JSON dict returned by the API — unknown keys are silently ignored so the SDK
stays forward-compatible as Onshape adds new fields.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Generic, Optional, TypeVar

T = TypeVar("T")


# ── Helpers ───────────────────────────────────────────────────────────────────

def _pick(data: dict, *keys: str) -> dict:
    """Return a subset of *data* containing only the listed keys."""
    return {k: data[k] for k in keys if k in data}


# ── Pagination ────────────────────────────────────────────────────────────────

@dataclass
class PaginatedList(Generic[T]):
    """Wrapper for paginated list responses."""
    items: list[T]
    next: Optional[str] = None
    total: Optional[int] = None

    @classmethod
    def from_dict(cls, data: dict, item_cls: type[T]) -> "PaginatedList[T]":
        items_raw = data.get("items", [])
        items = [item_cls.from_dict(i) if isinstance(i, dict) else i for i in items_raw]
        return cls(
            items=items,
            next=data.get("next"),
            total=data.get("total"),
        )


# ── Identity / Users ─────────────────────────────────────────────────────────

@dataclass
class UserInfo:
    id: str = ""
    name: str = ""
    email: str = ""
    company_name: str = ""
    image: str = ""
    raw: dict = field(default_factory=dict, repr=False)

    @classmethod
    def from_dict(cls, d: dict) -> "UserInfo":
        return cls(
            id=d.get("id", ""),
            name=d.get("name", ""),
            email=d.get("email", ""),
            company_name=d.get("companyName", ""),
            image=d.get("image", ""),
            raw=d,
        )


@dataclass
class Owner:
    id: str = ""
    name: str = ""
    type: str = ""  # "user", "company", "team"
    raw: dict = field(default_factory=dict, repr=False)

    @classmethod
    def from_dict(cls, d: dict) -> "Owner":
        return cls(
            id=d.get("id", ""),
            name=d.get("name", ""),
            type=d.get("type", ""),
            raw=d,
        )


# ── Documents ─────────────────────────────────────────────────────────────────

@dataclass
class Workspace:
    id: str = ""
    name: str = ""
    document_id: str = ""
    raw: dict = field(default_factory=dict, repr=False)

    @classmethod
    def from_dict(cls, d: dict) -> "Workspace":
        return cls(
            id=d.get("id", ""),
            name=d.get("name", ""),
            document_id=d.get("documentId", ""),
            raw=d,
        )


@dataclass
class DocumentVersion:
    id: str = ""
    name: str = ""
    document_id: str = ""
    created_at: str = ""
    microversion: str = ""
    description: str = ""
    raw: dict = field(default_factory=dict, repr=False)

    @classmethod
    def from_dict(cls, d: dict) -> "DocumentVersion":
        return cls(
            id=d.get("id", ""),
            name=d.get("name", ""),
            document_id=d.get("documentId", ""),
            created_at=d.get("createdAt", ""),
            microversion=d.get("microversion", ""),
            description=d.get("description", ""),
            raw=d,
        )


@dataclass
class Document:
    id: str = ""
    name: str = ""
    owner: Optional[Owner] = None
    default_workspace: Optional[Workspace] = None
    created_at: str = ""
    modified_at: str = ""
    href: str = ""
    public: bool = False
    trash: bool = False
    raw: dict = field(default_factory=dict, repr=False)

    @classmethod
    def from_dict(cls, d: dict) -> "Document":
        owner = Owner.from_dict(d["owner"]) if d.get("owner") else None
        dw = d.get("defaultWorkspace")
        ws = Workspace.from_dict(dw) if dw else None
        return cls(
            id=d.get("id", ""),
            name=d.get("name", ""),
            owner=owner,
            default_workspace=ws,
            created_at=d.get("createdAt", ""),
            modified_at=d.get("modifiedAt", ""),
            href=d.get("href", ""),
            public=d.get("public", False),
            trash=d.get("trash", False),
            raw=d,
        )


# ── Elements ──────────────────────────────────────────────────────────────────

@dataclass
class Element:
    """An element within a document (Part Studio, Assembly, Drawing, Blob, etc.)."""
    id: str = ""
    name: str = ""
    element_type: str = ""  # PARTSTUDIO, ASSEMBLY, DRAWING, BLOB, APPLICATION, ...
    data_type: str = ""
    micro_version_id: str = ""
    raw: dict = field(default_factory=dict, repr=False)

    @classmethod
    def from_dict(cls, d: dict) -> "Element":
        return cls(
            id=d.get("id", ""),
            name=d.get("name", ""),
            element_type=d.get("elementType", d.get("type", "")),
            data_type=d.get("dataType", ""),
            micro_version_id=d.get("microversionId", ""),
            raw=d,
        )


# ── Parts ─────────────────────────────────────────────────────────────────────

@dataclass
class Part:
    part_id: str = ""
    name: str = ""
    body_type: str = ""  # "solid", "surface", "wire", ...
    description: str = ""
    material: Optional[dict] = None
    appearance: Optional[dict] = None
    custom_properties: Optional[dict] = None
    state: str = ""
    raw: dict = field(default_factory=dict, repr=False)

    @classmethod
    def from_dict(cls, d: dict) -> "Part":
        return cls(
            part_id=d.get("partId", ""),
            name=d.get("name", ""),
            body_type=d.get("bodyType", ""),
            description=d.get("description", ""),
            material=d.get("material"),
            appearance=d.get("appearance"),
            custom_properties=d.get("customProperties"),
            state=d.get("state", ""),
            raw=d,
        )


# ── Features & Variables (Part Studio) ────────────────────────────────────────

@dataclass
class FeatureParameter:
    parameter_id: str = ""
    type: str = ""
    value: Any = None
    expression: str = ""
    raw: dict = field(default_factory=dict, repr=False)

    @classmethod
    def from_dict(cls, d: dict) -> "FeatureParameter":
        return cls(
            parameter_id=d.get("parameterId", d.get("btType", "")),
            type=d.get("type", d.get("typeName", "")),
            value=d.get("value", d.get("defaultValue")),
            expression=d.get("expression", ""),
            raw=d,
        )


@dataclass
class Feature:
    id: str = ""
    name: str = ""
    feature_type: str = ""
    suppressed: bool = False
    parameters: list[FeatureParameter] = field(default_factory=list)
    raw: dict = field(default_factory=dict, repr=False)

    @classmethod
    def from_dict(cls, d: dict) -> "Feature":
        params_raw = d.get("parameters", [])
        params = [FeatureParameter.from_dict(p) for p in params_raw if isinstance(p, dict)]
        return cls(
            id=d.get("id", d.get("featureId", "")),
            name=d.get("name", ""),
            feature_type=d.get("featureType", d.get("typeName", "")),
            suppressed=d.get("suppressed", False),
            parameters=params,
            raw=d,
        )


@dataclass
class Variable:
    name: str = ""
    type: str = ""
    value: Any = None
    description: str = ""
    expression: str = ""
    raw: dict = field(default_factory=dict, repr=False)

    @classmethod
    def from_dict(cls, d: dict) -> "Variable":
        return cls(
            name=d.get("name", ""),
            type=d.get("type", ""),
            value=d.get("value"),
            description=d.get("description", ""),
            expression=d.get("expression", ""),
            raw=d,
        )


# ── Assemblies ────────────────────────────────────────────────────────────────

@dataclass
class Occurrence:
    id: str = ""
    name: str = ""
    path: list[str] = field(default_factory=list)
    transform: list[float] = field(default_factory=list)  # 4x4 matrix as flat list
    part_id: str = ""
    element_id: str = ""
    document_id: str = ""
    hidden: bool = False
    raw: dict = field(default_factory=dict, repr=False)

    @classmethod
    def from_dict(cls, d: dict) -> "Occurrence":
        return cls(
            id=d.get("id", ""),
            name=d.get("name", ""),
            path=d.get("path", []),
            transform=d.get("transform", []),
            part_id=d.get("partId", ""),
            element_id=d.get("elementId", ""),
            document_id=d.get("documentId", ""),
            hidden=d.get("hidden", False),
            raw=d,
        )


@dataclass
class BomHeader:
    id: str = ""
    name: str = ""
    property_name: str = ""
    value_type: str = ""
    visible: bool = False
    raw: dict = field(default_factory=dict, repr=False)

    @classmethod
    def from_dict(cls, d: dict) -> "BomHeader":
        return cls(
            id=d.get("id", ""),
            name=d.get("name", ""),
            property_name=d.get("propertyName", ""),
            value_type=d.get("valueType", ""),
            visible=d.get("visible", False),
            raw=d,
        )


@dataclass
class BomRow:
    item_number: str = ""
    quantity: int = 0
    part_number: str = ""
    name: str = ""
    material: Any = None
    item_source: dict = field(default_factory=dict)
    header_values: dict[str, Any] = field(default_factory=dict, repr=False)
    property_to_header: dict[str, str] = field(default_factory=dict, repr=False)
    description: str = ""
    revision: str = ""
    raw: dict = field(default_factory=dict, repr=False)

    def get_value(self, property_name: str, default: Any = None) -> Any:
        header_id = self.property_to_header.get(property_name)
        if not header_id:
            return default
        return self.header_values.get(header_id, default)

    @property
    def material_name(self) -> str:
        value = self.material
        if isinstance(value, dict):
            return value.get("displayName") or value.get("name") or "—"
        if isinstance(value, str) and value.strip():
            return value
        return "—"

    @classmethod
    def from_dict(cls, d: dict, property_to_header: Optional[dict[str, str]] = None) -> "BomRow":
        header_values = d.get("headerIdToValue", {}) if isinstance(d.get("headerIdToValue", {}), dict) else {}
        property_to_header = property_to_header or {}

        def value_for(property_name: str, default: Any = None) -> Any:
            header_id = property_to_header.get(property_name)
            if not header_id:
                return default
            return header_values.get(header_id, default)

        return cls(
            item_number=str(value_for("item", d.get("itemNumber", d.get("item", ""))) or ""),
            quantity=int(float(value_for("quantity", d.get("quantity", 0)) or 0)),
            part_number=str(value_for("partNumber", d.get("partNumber", "")) or ""),
            name=str(value_for("name", d.get("name", "")) or ""),
            material=value_for("material"),
            item_source=d.get("itemSource", {}) if isinstance(d.get("itemSource", {}), dict) else {},
            header_values=header_values,
            property_to_header=dict(property_to_header),
            description=d.get("description", ""),
            revision=d.get("revision", ""),
            raw=d,
        )


@dataclass
class BomTable:
    headers: list[BomHeader] = field(default_factory=list)
    rows: list[BomRow] = field(default_factory=list)
    property_to_header: dict[str, str] = field(default_factory=dict, repr=False)
    raw: dict = field(default_factory=dict, repr=False)

    def header_id(self, property_name: str) -> str:
        return self.property_to_header.get(property_name, "")

    @classmethod
    def from_dict(cls, d: dict) -> "BomTable":
        headers_raw = d.get("headers", [])
        headers = [BomHeader.from_dict(h) for h in headers_raw if isinstance(h, dict)]
        property_to_header = {h.property_name: h.id for h in headers if h.property_name and h.id}
        rows = [BomRow.from_dict(r, property_to_header) for r in d.get("rows", []) if isinstance(r, dict)]
        return cls(headers=headers, rows=rows, property_to_header=property_to_header, raw=d)


@dataclass
class MateFeature:
    id: str = ""
    name: str = ""
    mate_type: str = ""
    suppressed: bool = False
    mated_entities: list[dict] = field(default_factory=list)
    raw: dict = field(default_factory=dict, repr=False)

    @classmethod
    def from_dict(cls, d: dict) -> "MateFeature":
        return cls(
            id=d.get("id", d.get("featureId", "")),
            name=d.get("name", ""),
            mate_type=d.get("mateType", d.get("featureType", "")),
            suppressed=d.get("suppressed", False),
            mated_entities=d.get("matedEntities", []),
            raw=d,
        )


@dataclass
class AssemblyDefinition:
    root_assembly: dict = field(default_factory=dict)
    sub_assemblies: list[dict] = field(default_factory=list)
    parts: list[Part] = field(default_factory=list)
    raw: dict = field(default_factory=dict, repr=False)

    @classmethod
    def from_dict(cls, d: dict) -> "AssemblyDefinition":
        parts_raw = d.get("parts", [])
        parts = [Part.from_dict(p) for p in parts_raw if isinstance(p, dict)]
        return cls(
            root_assembly=d.get("rootAssembly", {}),
            sub_assemblies=d.get("subAssemblies", []),
            parts=parts,
            raw=d,
        )


# ── Drawings ──────────────────────────────────────────────────────────────────

@dataclass
class DrawingView:
    id: str = ""
    name: str = ""
    view_type: str = ""
    raw: dict = field(default_factory=dict, repr=False)

    @classmethod
    def from_dict(cls, d: dict) -> "DrawingView":
        return cls(
            id=d.get("id", d.get("viewId", "")),
            name=d.get("name", d.get("label", "")),
            view_type=d.get("viewType", d.get("type", "")),
            raw=d,
        )


# ── Translations / Export ─────────────────────────────────────────────────────

@dataclass
class TranslationStatus:
    id: str = ""
    request_state: str = ""  # "ACTIVE", "DONE", "FAILED"
    progress: float = 0.0
    result_external_data_ids: list[str] = field(default_factory=list)
    result_element_ids: list[str] = field(default_factory=list)
    failure_reason: str = ""
    name: str = ""
    raw: dict = field(default_factory=dict, repr=False)

    @property
    def is_done(self) -> bool:
        return self.request_state == "DONE"

    @property
    def is_failed(self) -> bool:
        return self.request_state in ("FAILED", "ERROR")

    @property
    def is_active(self) -> bool:
        return self.request_state == "ACTIVE"

    @classmethod
    def from_dict(cls, d: dict) -> "TranslationStatus":
        return cls(
            id=d.get("id", ""),
            request_state=d.get("requestState", ""),
            progress=d.get("progress", 0.0),
            result_external_data_ids=d.get("resultExternalDataIds", []),
            result_element_ids=d.get("resultElementIds", []),
            failure_reason=d.get("failureReason", ""),
            name=d.get("name", ""),
            raw=d,
        )


# ── Metadata ──────────────────────────────────────────────────────────────────

@dataclass
class MetadataProperty:
    property_id: str = ""
    name: str = ""
    value: Any = None
    value_type: str = ""
    editable: bool = False
    raw: dict = field(default_factory=dict, repr=False)

    @classmethod
    def from_dict(cls, d: dict) -> "MetadataProperty":
        return cls(
            property_id=d.get("propertyId", ""),
            name=d.get("name", ""),
            value=d.get("value"),
            value_type=d.get("valueType", ""),
            editable=d.get("editable", False),
            raw=d,
        )


# ── Thumbnails ────────────────────────────────────────────────────────────────

@dataclass
class ThumbnailSize:
    size: str = ""
    href: str = ""
    media_type: str = ""
    raw: dict = field(default_factory=dict, repr=False)

    @classmethod
    def from_dict(cls, d: dict) -> "ThumbnailSize":
        return cls(
            size=d.get("size", ""),
            href=d.get("href", ""),
            media_type=d.get("mediaType", ""),
            raw=d,
        )


@dataclass
class ThumbnailInfo:
    sizes: list[ThumbnailSize] = field(default_factory=list)
    raw: dict = field(default_factory=dict, repr=False)

    @classmethod
    def from_dict(cls, d: dict) -> "ThumbnailInfo":
        sizes = [ThumbnailSize.from_dict(s) for s in d.get("sizes", []) if isinstance(s, dict)]
        return cls(sizes=sizes, raw=d)


# ── Webhooks ──────────────────────────────────────────────────────────────────

@dataclass
class Webhook:
    id: str = ""
    url: str = ""
    events: list[str] = field(default_factory=list)
    filter: str = ""
    options: dict = field(default_factory=dict)
    raw: dict = field(default_factory=dict, repr=False)

    @classmethod
    def from_dict(cls, d: dict) -> "Webhook":
        return cls(
            id=d.get("id", ""),
            url=d.get("url", ""),
            events=d.get("events", []),
            filter=d.get("filter", ""),
            options=d.get("options", {}),
            raw=d,
        )
