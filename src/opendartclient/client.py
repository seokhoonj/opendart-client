"""OpenDart -- the entry point.

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
from .errors import DartError, error_from_xml
from .event import Event
from .finance import Finance
from .ownership import Ownership
from .registration import Registration
from .report import Report
from .resolver import CorpResolver
from .session import DartSession

CORP_CODE = DartEndpoint("corpCode", "DS001", "2019018", payload_kind="zip")


class OpenDart:
    """Client for the OpenDART REST API. Groups endpoints as sub-surfaces."""

    def __init__(self, api_key: str | None = None, *, timeout: float = 30.0) -> None:
        self._session = DartSession(api_key, timeout=timeout)
        self.disclosure = Disclosure(self._session)      # 공시정보 (DS001)
        self.report = Report(self._session)              # 정기보고서 주요정보 (DS002)
        self.finance = Finance(self._session)            # 정기보고서 재무정보 (DS003)
        self.ownership = Ownership(self._session)        # 지분공시 (DS004)
        self.event = Event(self._session)                # 주요사항보고서 (DS005)
        self.registration = Registration(self._session)  # 증권신고서 (DS006)
        self._resolver: CorpResolver | None = None

    def __repr__(self) -> str:
        return f"OpenDart({self._session!r})"

    def resolver(self) -> CorpResolver:
        """A name / ticker / 초성 / typo -> corp_code resolver, built once from
        ``corp_codes()`` and cached on this client. The single network call happens on
        first use only (opt-in), never in the constructor."""
        if self._resolver is None:
            self._resolver = CorpResolver(self.corp_codes())
        return self._resolver

    def corp_codes(self) -> list[dict[str, Any]]:
        """고유번호 (2019018). The full corp_code mapping, one dict per company:
        ``corp_code`` (8-digit DART id), ``corp_name``, ``stock_code`` (6-digit for
        listed companies, else ``None``), ``modify_date``. The base table every
        corp_code-keyed endpoint depends on."""
        return _parse_corp_code_zip(self._session.fetch_bytes(CORP_CODE))


def _parse_corp_code_zip(content: bytes) -> list[dict[str, Any]]:
    """Parse a corpCode.xml zip payload into rows. On a non-zip payload (OpenDART
    returns XML for errors) raise DartError. Pure function of the bytes -- testable
    without a live call."""
    try:
        archive = zipfile.ZipFile(io.BytesIO(content))
    except zipfile.BadZipFile:
        raise error_from_xml(content) from None
    with archive:
        names = archive.namelist()
        if not names:
            raise DartError("empty-zip", "corpCode.xml archive has no entries")
        xml_bytes = archive.read(names[0])
    try:
        root = ET.fromstring(xml_bytes)
    except ET.ParseError as err:
        raise DartError("parse", "corpCode.xml entry is not valid XML") from err
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
