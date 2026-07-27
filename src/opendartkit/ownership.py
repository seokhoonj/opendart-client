"""지분공시 종합정보 (DS004) -- insider and 5%-holding reports.

Two standalone equity disclosures, keyed by ``corp_code`` (no date range): the whole
history the company has on file is returned.
"""

from __future__ import annotations

from typing import Any

from ._endpoint import DartEndpoint
from .session import DartSession

Rows = list[dict[str, Any]]

EXECUTIVE_HOLDINGS = DartEndpoint(
    "elestock", "DS004", "2019022", required=("corp_code",)
)
MAJOR_HOLDINGS = DartEndpoint(
    "majorstock", "DS004", "2019021", required=("corp_code",)
)


class Ownership:
    """지분공시 종합정보 (DS004). Reach it as ``DartClient.ownership``."""

    def __init__(self, session: DartSession) -> None:
        self._session = session

    def executive_holdings(self, corp_code: str) -> Rows:
        """임원ㆍ주요주주 소유보고 (2019022) -- insider ownership filings."""
        return self._session.fetch_list(EXECUTIVE_HOLDINGS, corp_code=corp_code)

    def major_holdings(self, corp_code: str) -> Rows:
        """대량보유 상황보고 (2019021) -- 5%-rule large-holding filings."""
        return self._session.fetch_list(MAJOR_HOLDINGS, corp_code=corp_code)
