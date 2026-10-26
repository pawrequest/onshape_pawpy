"""Onshape Python SDK — typed client for the Onshape REST API.

Quick start
-----------
>>> from onshape_sdk import OnshapeClient, parse_onshape_url
>>> client = OnshapeClient.from_env()  # reads .env
>>> client.test_auth()
>>> ids = parse_onshape_url("https://cad.onshape.com/documents/…/w/…/e/…")
>>> parts = client.parts.list(ids["did"], ids["wvm_type"], ids["wvm_id"], ids["eid"])
"""

from .client import OnshapeClient
from .utils import OnshapeIds, build_wvm_path, parse_onshape_url

# Types — re-exported so users can do ``from onshape_sdk import Document, Part, …``
from .types import (
    AssemblyDefinition,
    BomHeader,
    BomRow,
    BomTable,
    Document,
    DocumentVersion,
    DrawingView,
    Element,
    Feature,
    FeatureParameter,
    MateFeature,
    MetadataProperty,
    Occurrence,
    Owner,
    PaginatedList,
    Part,
    ThumbnailInfo,
    ThumbnailSize,
    TranslationStatus,
    UserInfo,
    Variable,
    Webhook,
    Workspace,
)

# Resource APIs — importable for type annotations
from .assemblies import AssembliesApi
from .blob_elements import BlobElementsApi
from .documents import DocumentsApi
from .drawings import DrawingsApi
from .metadata import MetadataApi
from .parts import PartsApi
from .part_studios import PartStudiosApi
from .thumbnails import ThumbnailsApi
from .translations import TranslationError, TranslationsApi
from .webhooks import WebhooksApi

__all__ = [
    # Client
    "OnshapeClient",
    # Utils
    "parse_onshape_url",
    "build_wvm_path",
    "OnshapeIds",
    # Types
    "AssemblyDefinition",
    "BomHeader",
    "BomRow",
    "BomTable",
    "Document",
    "DocumentVersion",
    "DrawingView",
    "Element",
    "Feature",
    "FeatureParameter",
    "MateFeature",
    "MetadataProperty",
    "Occurrence",
    "Owner",
    "PaginatedList",
    "Part",
    "ThumbnailInfo",
    "ThumbnailSize",
    "TranslationError",
    "TranslationStatus",
    "UserInfo",
    "Variable",
    "Webhook",
    "Workspace",
    # Resource APIs
    "AssembliesApi",
    "BlobElementsApi",
    "DocumentsApi",
    "DrawingsApi",
    "MetadataApi",
    "PartsApi",
    "PartStudiosApi",
    "ThumbnailsApi",
    "TranslationsApi",
    "WebhooksApi",
]
