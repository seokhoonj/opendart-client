"""공시정보 (DS001) -- disclosure search, company profile, original documents.

The sub-surface every event study starts from: ``search`` is the feed of "which
disclosure, filed when, by whom"; ``company`` is the profile behind a corp_code;
``document`` pulls the original filing bytes.
"""

from __future__ import annotations

from typing import Any

from ._endpoint import DartEndpoint
from .session import DartSession
from .types import CorpClass, DisclosureType, SortField, SortOrder

SEARCH = DartEndpoint("list", "DS001", "2019001")
COMPANY = DartEndpoint("company", "DS001", "2019002", required=("corp_code",))
DOCUMENT = DartEndpoint(
    "document", "DS001", "2019003", required=("rcept_no",), payload_kind="zip"
)


class Disclosure:
    """공시정보 (DS001). Reach it as ``DartClient.disclosure``."""

    def __init__(self, session: DartSession) -> None:
        self._session = session

    def search(
        self,
        *,
        corp_code: str | None = None,
        begin_date: str | None = None,
        end_date: str | None = None,
        last_report_only: bool | None = None,
        disclosure_type: DisclosureType | None = None,
        detail_type: str | None = None,
        corp_class: CorpClass | None = None,
        sort: SortField | None = None,
        sort_order: SortOrder | None = None,
        page_count: int = 100,
        max_pages: int | None = None,
    ) -> list[dict[str, Any]]:
        """공시검색 (2019001). Every filing matching the window/filters.

        Auto-paginates: requests ``page_count`` rows per page and walks every page
        through ``total_page``, so the result is complete by default -- no silent
        first-page-only truncation. ``max_pages`` caps the fetch *explicitly* when you
        want a ceiling.

        Args:
            corp_code: 공시대상회사 고유번호(8자리); omit to search all companies
                (then the DART window is limited to 3 months).
            begin_date / end_date: 접수일자 range, ``YYYYMMDD``.
            last_report_only: 최종보고서만 (정정 제외) if True.
            disclosure_type: 공시유형 (``pblntf_ty``, A~J -- see ``DisclosureType``).
            detail_type: 공시상세유형 (``pblntf_detail_ty``); a DART code family
                (A001, B001, ...), left as ``str`` because the set is large/extensible.
            corp_class: 법인구분 (Y/K/N/E).
            sort / sort_order: 정렬 기준 / 방법.
            page_count: rows per page; clamped to 1..100 (the DART max).
            max_pages: stop after this many pages (an explicit cap, not a silent one).
        """
        if max_pages is not None and max_pages < 1:
            raise ValueError(f"max_pages must be >= 1 when set; got {max_pages}")
        page_count = min(max(page_count, 1), 100)
        base: dict[str, str | None] = {
            "corp_code": corp_code,
            "bgn_de": begin_date,
            "end_de": end_date,
            "last_reprt_at": _yn(last_report_only),
            "pblntf_ty": disclosure_type,
            "pblntf_detail_ty": detail_type,
            "corp_cls": corp_class,
            "sort": sort,
            "sort_mth": sort_order,
            "page_count": str(page_count),
        }
        rows: list[dict[str, Any]] = []
        page = 1
        while True:
            body = self._session.fetch_body(SEARCH, page_no=str(page), **base)
            rows.extend(body.get("list", []))
            total_page = int(body.get("total_page", 1) or 1)
            if page >= total_page or (max_pages is not None and page >= max_pages):
                break
            page += 1
        return rows

    def company(self, corp_code: str) -> dict[str, Any]:
        """기업개황 (2019002). The company profile (name, ceo, address, industry,
        establishment date, ...) as a dict. Fields sit at the top level of the body."""
        return self._session.fetch_body(COMPANY, corp_code=corp_code)

    def document(self, rcept_no: str) -> bytes:
        """공시서류원본파일 (2019003). The original filing as raw zip bytes; the
        caller unzips (the archive holds the filing's XML)."""
        return self._session.fetch_bytes(DOCUMENT, rcept_no=rcept_no)


def _yn(flag: bool | None) -> str | None:
    if flag is None:
        return None
    return "Y" if flag else "N"
