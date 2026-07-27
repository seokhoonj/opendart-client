"""DartClient -- the entry point.

Built from an API key (constructor or ``OPENDART_API_KEY`` env), it holds a
``DartSession`` and wires the grouped sub-surfaces. ``corp_codes`` lives here because
its payload is a zip of XML, not a JSON list, so it bypasses the JSON fetches and has
a dedicated parse.
"""

from __future__ import annotations

import io
import xml.etree.ElementTree as ET
import zipfile
from typing import Any

from ._endpoint import DartEndpoint
from .disclosure import Disclosure
from .errors import DartError, error_for
from .session import DartSession

CORP_CODE = DartEndpoint("corpCode", "DS001", "2019018", payload_kind="zip")


class DartClient:
    """Client for the OpenDART REST API. Groups endpoints as sub-surfaces."""

    def __init__(self, api_key: str | None = None, *, timeout: float = 30.0) -> None:
        self._session = DartSession(api_key, timeout=timeout)
        self.disclosure = Disclosure(self._session)   # 공시정보 (DS001)

    def __repr__(self) -> str:
        return f"DartClient({self._session!r})"

    def corp_codes(self) -> list[dict[str, Any]]:
        """고유번호 (2019018). The full corp_code mapping, one dict per company:
        ``corp_code`` (8-digit DART id), ``corp_name``, ``stock_code`` (6-digit for
        listed companies, else ``None``), ``modify_date``. The base table every
        corp_code-keyed endpoint depends on."""
        return _parse_corp_code_zip(self._session.get_bytes(CORP_CODE))


def _parse_corp_code_zip(content: bytes) -> list[dict[str, Any]]:
    """Parse a corpCode.xml zip payload into rows. On a non-zip payload (OpenDART
    returns XML for errors) raise DartError. Pure function of the bytes -- testable
    without a live call."""
    try:
        archive = zipfile.ZipFile(io.BytesIO(content))
    except zipfile.BadZipFile:
        raise _error_from_xml(content) from None
    with archive:
        names = archive.namelist()
        if not names:
            raise DartError("empty-zip", "corpCode.xml archive has no entries")
        xml_bytes = archive.read(names[0])
    root = ET.fromstring(xml_bytes)
    return [
        {
            "corp_code": _text(node, "corp_code"),
            "corp_name": _text(node, "corp_name"),
            "stock_code": _text(node, "stock_code") or None,
            "modify_date": _text(node, "modify_date"),
        }
        for node in root.iter("list")
    ]


def _text(node: ET.Element, tag: str) -> str:
    text = node.findtext(tag)
    return text.strip() if text else ""


def _error_from_xml(content: bytes) -> DartError:
    try:
        root = ET.fromstring(content)
        status = (root.findtext("status") or "").strip()
        message = (root.findtext("message") or "").strip()
    except ET.ParseError:
        status, message = "?", content[:200].decode("utf-8", "replace")
    return error_for(status or "?", message or "unrecognized response")
