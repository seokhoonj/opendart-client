"""정기보고서 재무정보 (DS003) -- financial statements and indicators.

Each method returns the API's own response keys as rows; no field is renamed here.
The 주요계정 response is long -- one row per ``account_nm`` x ``fs_div`` (CFS 연결 /
OFS 별도) x ``sj_div`` (BS / IS), with amount columns ``thstrm_amount`` (this period),
``frmtrm_amount`` (prior), and -- for annual reports -- ``bfefrmtrm_amount`` (two
periods prior). ``bsns_year`` is available from 2015 onward.
"""

from __future__ import annotations

from collections.abc import Sequence
from typing import Any

from ._endpoint import DartEndpoint
from .session import DartSession
from .types import IndexClass, ReportCode, StatementDiv, StatementKind

Rows = list[dict[str, Any]]

_MAX_CORP_CODES = 100   # DART returns status 021 above this; fail fast with a clear error


def _join_corp_codes(corp_codes: Sequence[str]) -> str:
    """Comma-join corp_codes for a bulk endpoint, enforcing DART's 100-company cap
    so an oversized batch fails fast with a clear message instead of wasting a call
    on a 021 the caller has to decode."""
    if not 1 <= len(corp_codes) <= _MAX_CORP_CODES:
        raise ValueError(
            f"corp_codes must hold 1..{_MAX_CORP_CODES} codes; got {len(corp_codes)}"
        )
    return ",".join(corp_codes)

SINGLE_ACCOUNTS = DartEndpoint(
    "fnlttSinglAcnt", "DS003", "2019016",
    required=("corp_code", "bsns_year", "reprt_code"),
)
MULTI_ACCOUNTS = DartEndpoint(
    "fnlttMultiAcnt", "DS003", "2019017",
    required=("corp_code", "bsns_year", "reprt_code"),
)
FULL_STATEMENTS = DartEndpoint(
    "fnlttSinglAcntAll", "DS003", "2019020",
    required=("corp_code", "bsns_year", "reprt_code", "fs_div"),
)
SINGLE_INDICATORS = DartEndpoint(
    "fnlttSinglIndx", "DS003", "2022001",
    required=("corp_code", "bsns_year", "reprt_code", "idx_cl_code"),
)
MULTI_INDICATORS = DartEndpoint(
    "fnlttCmpnyIndx", "DS003", "2022002",
    required=("corp_code", "bsns_year", "reprt_code", "idx_cl_code"),
)
XBRL_DOCUMENT = DartEndpoint(
    "fnlttXbrl", "DS003", "2019019",
    required=("rcept_no", "reprt_code"), payload_kind="zip",
)
XBRL_TAXONOMY = DartEndpoint("xbrlTaxonomy", "DS003", "2020001", required=("sj_div",))


class Finance:
    """정기보고서 재무정보 (DS003). Reach it as ``DartClient.finance``."""

    def __init__(self, session: DartSession) -> None:
        self._session = session

    def single_accounts(
        self, corp_code: str, *, fiscal_year: int, report_code: ReportCode = "11011"
    ) -> Rows:
        """단일회사 주요계정 (2019016) -- key accounts for one company and period.
        Returns both CFS and OFS rows (distinguished by ``fs_div``) in one call."""
        return self._session.fetch_list(
            SINGLE_ACCOUNTS,
            corp_code=corp_code, bsns_year=str(fiscal_year), reprt_code=report_code,
        )

    def multi_accounts(
        self,
        corp_codes: Sequence[str],
        *,
        fiscal_year: int,
        report_code: ReportCode = "11011",
    ) -> Rows:
        """다중회사 주요계정 (2019017) -- the same key accounts for several companies
        in one call (corp_codes joined comma-separated, max 100). The bulk path that
        keeps a universe ingest under the daily call limit."""
        return self._session.fetch_list(
            MULTI_ACCOUNTS,
            corp_code=_join_corp_codes(corp_codes),
            bsns_year=str(fiscal_year),
            reprt_code=report_code,
        )

    def full_statements(
        self,
        corp_code: str,
        *,
        fiscal_year: int,
        statement_div: StatementDiv,
        report_code: ReportCode = "11011",
    ) -> Rows:
        """단일회사 전체 재무제표 (2019020) -- every line item of BS/IS/CIS/CF for one
        company. ``statement_div`` (CFS 연결 / OFS 별도) is required here."""
        return self._session.fetch_list(
            FULL_STATEMENTS,
            corp_code=corp_code, bsns_year=str(fiscal_year),
            reprt_code=report_code, fs_div=statement_div,
        )

    def single_indicators(
        self,
        corp_code: str,
        *,
        fiscal_year: int,
        index_class: IndexClass,
        report_code: ReportCode = "11011",
    ) -> Rows:
        """단일회사 주요 재무지표 (2022001) -- one company's ratios for one
        ``index_class`` (수익성 / 안정성 / 성장성 / 활동성)."""
        return self._session.fetch_list(
            SINGLE_INDICATORS,
            corp_code=corp_code, bsns_year=str(fiscal_year),
            reprt_code=report_code, idx_cl_code=index_class,
        )

    def multi_indicators(
        self,
        corp_codes: Sequence[str],
        *,
        fiscal_year: int,
        index_class: IndexClass,
        report_code: ReportCode = "11011",
    ) -> Rows:
        """다중회사 주요 재무지표 (2022002) -- the same ratios for several companies
        in one call (corp_codes joined comma-separated, max 100)."""
        return self._session.fetch_list(
            MULTI_INDICATORS,
            corp_code=_join_corp_codes(corp_codes), bsns_year=str(fiscal_year),
            reprt_code=report_code, idx_cl_code=index_class,
        )

    def xbrl_document(self, rcept_no: str, *, report_code: ReportCode) -> bytes:
        """재무제표 원본파일(XBRL) (2019019) -- the raw XBRL zip for one filing. Keyed
        by ``rcept_no`` (not corp_code); the caller unzips and parses the XBRL."""
        return self._session.fetch_bytes(
            XBRL_DOCUMENT, rcept_no=rcept_no, reprt_code=report_code
        )

    def xbrl_taxonomy(self, *, statement_kind: StatementKind) -> Rows:
        """XBRL택사노미재무제표양식 (2020001) -- the standard account taxonomy for a
        statement kind (``sj_div``: BS1-4 / IS1-4 / CIS1-4 / CF1-4 / SCE1-2 / ...)."""
        return self._session.fetch_list(XBRL_TAXONOMY, sj_div=statement_kind)
