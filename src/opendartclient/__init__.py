"""opendartclient -- a clean, sync, typed client for Korea's OpenDART (전자공시) API.

    from opendartclient import OpenDart

    dart = OpenDart(api_key="...")          # or set OPENDART_API_KEY
    rows = dart.disclosure.search(corp_code="00126380",
                                  begin_date="20260101", end_date="20260131")
    profile = dart.disclosure.company("00126380")
    corps = dart.corp_codes()

Returns raw ``list[dict]`` / ``dict``; frame it with ``to_pandas`` / ``to_polars`` or
your own. Zero runtime dependencies.
"""

from __future__ import annotations

from importlib.metadata import PackageNotFoundError, version

from ._endpoint import DartEndpoint
from .client import OpenDart
from .errors import (
    AuthError,
    DartError,
    RateLimitError,
    ServerError,
    ValidationError,
)
from .frames import to_pandas, to_polars
from .resolver import CorpResolver
from .session import DartSession
from .types import (
    CorpClass,
    DisclosureType,
    ReportCode,
    SortField,
    SortOrder,
    StatementDiv,
)

try:
    __version__ = version("opendartclient")   # single source of truth: pyproject.toml
except PackageNotFoundError:               # running from source without an install
    __version__ = "0.0.0+unknown"

__all__ = [
    "AuthError",
    "CorpClass",
    "CorpResolver",
    "OpenDart",
    "DartEndpoint",
    "DartError",
    "DartSession",
    "DisclosureType",
    "RateLimitError",
    "ReportCode",
    "ServerError",
    "SortField",
    "SortOrder",
    "StatementDiv",
    "ValidationError",
    "to_pandas",
    "to_polars",
]
