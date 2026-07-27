"""opendartkit -- a clean, sync, typed client for Korea's OpenDART (전자공시) API.

    from opendartkit import DartClient

    dart = DartClient(api_key="...")          # or set OPENDART_API_KEY
    rows = dart.disclosure.search(corp_code="00126380",
                                  begin_date="20260101", end_date="20260131")
    profile = dart.disclosure.company("00126380")
    corps = dart.corp_codes()

Returns raw ``list[dict]`` / ``dict``; frame it with ``to_pandas`` / ``to_polars`` or
your own. Zero runtime dependencies.
"""

from __future__ import annotations

from ._endpoint import DartEndpoint
from .client import DartClient
from .errors import (
    AuthError,
    DartError,
    RateLimitError,
    ServerError,
    ValidationError,
)
from .frames import to_pandas, to_polars
from .session import DartSession
from .types import (
    CorpClass,
    DisclosureType,
    ReportCode,
    SortField,
    SortOrder,
    StatementDiv,
)

__version__ = "0.1.0"

__all__ = [
    "AuthError",
    "CorpClass",
    "DartClient",
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
