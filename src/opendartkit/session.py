"""DartSession -- key injection, HTTP over the standard library, and the fetches.

The session holds the API key and turns an endpoint + params into Python data: a
``list[dict]`` for flat endpoints, a ``dict[str, list[dict]]`` for grouped ones, or
raw ``bytes`` for the zip endpoints. No third-party HTTP client -- ``urllib`` carries
it, so the package has zero runtime dependencies.

The key comes from the constructor, or the ``OPENDART_API_KEY`` environment variable
as a fallback. The session never reads any application's config file; it is
self-contained (the consumer injects whatever it resolved).
"""

from __future__ import annotations

import io
import json
import os
import urllib.error
import urllib.parse
import urllib.request
import zipfile
from typing import Any

from ._endpoint import DartEndpoint, ResponseShape
from .errors import DartError, error_for, error_from_xml

_OK = "000"
_NO_DATA = "013"          # 조회된 데이터가 없습니다 -- an expected empty, not an error
_API_KEY_ENV = "OPENDART_API_KEY"

Params = dict[str, str | None]


class DartSession:
    """Holds the API key; fetches endpoints as raw Python data."""

    def __init__(self, api_key: str | None = None, *, timeout: float = 30.0) -> None:
        key = (api_key or os.environ.get(_API_KEY_ENV, "")).strip()
        if not key:
            raise ValueError(
                f"OpenDART API key required: pass api_key=... or set ${_API_KEY_ENV}"
            )
        self.api_key = key
        self.timeout = timeout

    def __repr__(self) -> str:
        return f"DartSession(key=...{self.api_key[-4:]})"

    # --- fetches (the public surface sub-surfaces call) ------------------

    def fetch_list(
        self, endpoint: DartEndpoint, **params: str | None
    ) -> list[dict[str, Any]]:
        """A flat endpoint's ``list`` array. status 000 -> the rows; 013 -> ``[]``;
        any other status -> DartError. A 000 body without a ``list`` key raises (it is
        almost certainly a grouped endpoint that should use ``fetch_groups``)."""
        self._require_shape(endpoint, "flat")
        body = self._body(endpoint, params)
        if body is None:
            return []
        rows = body.get("list")
        if rows is None:
            raise DartError(
                _OK, "response has no 'list' -- grouped endpoint? use fetch_groups",
                endpoint.guide_url,
            )
        return list(rows)

    def fetch_groups(
        self, endpoint: DartEndpoint, **params: str | None
    ) -> dict[str, list[dict[str, Any]]]:
        """A grouped endpoint's ``group[].list[]``, keyed by each group's title.
        status 000 -> the groups; 013 -> ``{}``; other -> DartError. A 000 body
        without a ``group`` key raises (a flat endpoint should use ``fetch_list``)."""
        self._require_shape(endpoint, "grouped")
        body = self._body(endpoint, params)
        if body is None:
            return {}
        groups = body.get("group")
        if groups is None:
            raise DartError(
                _OK, "response has no 'group' -- flat endpoint? use fetch_list",
                endpoint.guide_url,
            )
        result: dict[str, list[dict[str, Any]]] = {}
        for index, group in enumerate(groups):
            title = str(group.get("title", index))
            key, suffix = title, 1
            while key in result:               # loop to a free key so no group is ever
                key, suffix = f"{title} ({suffix})", suffix + 1   # silently overwritten
            result[key] = list(group.get("list", []))
        return result

    def fetch_body(
        self, endpoint: DartEndpoint, **params: str | None
    ) -> dict[str, Any]:
        """The full validated response body (for paginated endpoints that need
        ``total_page`` / ``total_count``, and single-object endpoints whose fields sit
        at the top level). 013 -> an empty-but-well-formed body."""
        body = self._body(endpoint, params)
        if body is None:
            return {"status": _NO_DATA, "list": [], "total_page": 0, "total_count": 0}
        return body

    def fetch_bytes(self, endpoint: DartEndpoint, **params: str | None) -> bytes:
        """A zip endpoint's raw bytes (corpCode / document / xbrl). On failure DART
        returns an error XML instead of a zip; this checks the payload really is a zip
        and raises a typed DartError otherwise, so a bad key surfaces as AuthError --
        not an opaque BadZipFile when the caller later tries to unzip."""
        self._check_required(endpoint, params)
        content = self._get(endpoint, params)
        if not zipfile.is_zipfile(io.BytesIO(content)):
            raise error_from_xml(content, endpoint.guide_url)
        return content

    # --- internals -------------------------------------------------------

    def _body(self, endpoint: DartEndpoint, params: Params) -> dict[str, Any] | None:
        """Validate params, GET, parse JSON, apply the status contract. Returns the
        body dict on 000, ``None`` on 013 (no data), and raises on any other status."""
        self._check_required(endpoint, params)
        raw = self._get(endpoint, params)
        try:
            parsed = json.loads(raw)
        except json.JSONDecodeError as err:
            # OpenDART serves an HTML page during maintenance; surface a typed error
            # instead of leaking a stdlib JSONDecodeError.
            raise DartError(
                "parse", raw[:200].decode("utf-8", "replace"), endpoint.guide_url
            ) from err
        if not isinstance(parsed, dict):
            # A valid but non-object JSON body (a bare array/scalar) would otherwise
            # blow up on body.get(...) with a raw AttributeError.
            raise DartError(
                "parse", raw[:200].decode("utf-8", "replace"), endpoint.guide_url
            )
        body: dict[str, Any] = parsed
        status = body.get("status")
        if status == _NO_DATA:
            return None
        if status != _OK:
            raise error_for(status or "?", body.get("message", ""), endpoint.guide_url)
        return body

    def _check_required(self, endpoint: DartEndpoint, params: Params) -> None:
        missing = [p for p in endpoint.required if not params.get(p)]
        if missing:
            given = sorted(k for k, v in params.items() if v)
            raise ValueError(f"{endpoint.operation} requires {missing}; got {given}")

    def _require_shape(self, endpoint: DartEndpoint, expected: ResponseShape) -> None:
        """Enforce flat-vs-grouped BEFORE the call, so a misroute raises even on a 013
        (no-data) response -- where the body-level ``list``/``group`` guard cannot fire."""
        if endpoint.response_shape != expected:
            other = "fetch_groups" if expected == "flat" else "fetch_list"
            raise DartError(
                "shape",
                f"{endpoint.operation} is {endpoint.response_shape}; use {other}",
                endpoint.guide_url,
            )

    def _get(self, endpoint: DartEndpoint, params: Params) -> bytes:
        query = {"crtfc_key": self.api_key}
        query.update({k: v for k, v in params.items() if v is not None})
        url = f"{endpoint.url}?{urllib.parse.urlencode(query)}"
        request = urllib.request.Request(url, headers={"User-Agent": "opendartkit"})
        try:
            with urllib.request.urlopen(request, timeout=self.timeout) as response:
                content: bytes = response.read()
                return content
        except urllib.error.HTTPError as err:
            raise DartError(
                "http", f"HTTP {err.code} for {endpoint.operation}", endpoint.guide_url
            ) from err
        except urllib.error.URLError as err:
            raise DartError("network", str(err.reason), endpoint.guide_url) from err
