"""The DartEndpoint value object shared by every OpenDART sub-surface.

Each endpoint declares its operation stem, its API group, and the ``api_id`` of its
official guide page -- the authority for the endpoint's parameters and response
fields. ``guide_url`` resolves to that page so a reader can open the spec directly.

``operation`` is the bare stem (``"list"``, ``"piicDecsn"``); the ``.json`` / ``.xml``
suffix is chosen from ``payload_kind`` in :pyattr:`url`, so the wire format lives in
exactly one place. ``response_shape`` distinguishes a flat ``{status, list}`` body
from a nested ``{status, group:[{title, list}]}`` one, so a grouped endpoint can never
be routed silently through the flat fetch (the empty-frame trap).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

BASE_URL = "https://opendart.fss.or.kr/api"
GUIDE_URL = "https://opendart.fss.or.kr/guide/detail.do"

PayloadKind = Literal["json", "zip"]
ResponseShape = Literal["flat", "grouped"]


@dataclass(frozen=True, slots=True)
class DartEndpoint:
    """One OpenDART operation and where its spec lives."""

    operation: str                          # stem: "list", "piicDecsn"
    group: str                              # "DS001"
    api_id: str                             # guide page id = spec authority
    required: tuple[str, ...] = ()          # required params beyond crtfc_key
    payload_kind: PayloadKind = "json"      # "json" | "zip" (corpCode/document/xbrl)
    response_shape: ResponseShape = "flat"  # flat=body.list, grouped=body.group[].list

    @property
    def suffix(self) -> str:
        return "xml" if self.payload_kind == "zip" else "json"

    @property
    def url(self) -> str:
        return f"{BASE_URL}/{self.operation}.{self.suffix}"

    @property
    def guide_url(self) -> str:
        return f"{GUIDE_URL}?apiGrpCd={self.group}&apiId={self.api_id}"
