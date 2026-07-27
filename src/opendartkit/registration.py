"""증권신고서 (DS006) -- securities registration statements.

Every endpoint here returns a **grouped** response: one filing splits into several
titled sub-tables (증권의 종류, 인수인, 자금의 사용목적, ...), so each method returns
``dict[str, list[dict]]`` keyed by group title -- not a flat ``list``. Same
``corp_code`` + receipt-date window as the event reports.
"""

from __future__ import annotations

from typing import Any

from ._endpoint import DartEndpoint
from .session import DartSession

Groups = dict[str, list[dict[str, Any]]]

_REQUIRED = ("corp_code", "bgn_de", "end_de")


def _make_endpoint(operation: str, api_id: str) -> DartEndpoint:
    return DartEndpoint(operation, "DS006", api_id, required=_REQUIRED, response_shape="grouped")


EQUITY_SECURITIES = _make_endpoint("estkRs", "2020054")
DEBT_SECURITIES = _make_endpoint("bdRs", "2020055")
DEPOSITARY_RECEIPTS = _make_endpoint("stkdpRs", "2020056")
MERGER = _make_endpoint("mgRs", "2020057")
STOCK_EXCHANGE = _make_endpoint("extrRs", "2020058")
DIVISION = _make_endpoint("dvRs", "2020059")


class Registration:
    """증권신고서 (DS006). Reach it as ``DartClient.registration``.

    Every method takes ``corp_code`` + ``begin_date`` / ``end_date`` (YYYYMMDD) and
    returns ``dict[str, list[dict]]`` -- the filing's titled sub-tables.
    """

    def __init__(self, session: DartSession) -> None:
        self._session = session

    def _fetch_groups(
        self, endpoint: DartEndpoint, corp_code: str, begin_date: str, end_date: str
    ) -> Groups:
        return self._session.fetch_groups(
            endpoint, corp_code=corp_code, bgn_de=begin_date, end_de=end_date
        )

    def equity_securities(
        self, *, corp_code: str, begin_date: str, end_date: str
    ) -> Groups:
        """지분증권 (2020054)."""
        return self._fetch_groups(EQUITY_SECURITIES, corp_code, begin_date, end_date)

    def debt_securities(
        self, *, corp_code: str, begin_date: str, end_date: str
    ) -> Groups:
        """채무증권 (2020055)."""
        return self._fetch_groups(DEBT_SECURITIES, corp_code, begin_date, end_date)

    def depositary_receipts(
        self, *, corp_code: str, begin_date: str, end_date: str
    ) -> Groups:
        """증권예탁증권 (2020056)."""
        return self._fetch_groups(DEPOSITARY_RECEIPTS, corp_code, begin_date, end_date)

    def merger(
        self, *, corp_code: str, begin_date: str, end_date: str
    ) -> Groups:
        """합병 (2020057)."""
        return self._fetch_groups(MERGER, corp_code, begin_date, end_date)

    def stock_exchange(
        self, *, corp_code: str, begin_date: str, end_date: str
    ) -> Groups:
        """주식의포괄적교환·이전 (2020058)."""
        return self._fetch_groups(STOCK_EXCHANGE, corp_code, begin_date, end_date)

    def division(
        self, *, corp_code: str, begin_date: str, end_date: str
    ) -> Groups:
        """분할 (2020059)."""
        return self._fetch_groups(DIVISION, corp_code, begin_date, end_date)
