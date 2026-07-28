"""Disclosure sub-surface tests -- pagination, explicit cap, no-data, profile."""

import json

from opendart_client.disclosure import Disclosure
from opendart_client.session import DartSession


def _session_pages(pages: list[dict]) -> DartSession:
    """A session that returns ``pages[page_no - 1]`` for each search call."""
    session = DartSession(api_key="TESTKEY")

    def _fake_get(endpoint, params):
        page = int(params.get("page_no", "1"))
        return json.dumps(pages[page - 1]).encode("utf-8")

    session._get = _fake_get  # type: ignore[method-assign]
    return session


def _page(page_no: int, total_page: int, rows: list[dict]) -> dict:
    return {"status": "000", "page_no": page_no, "total_page": total_page,
            "total_count": total_page * len(rows), "list": rows}


def test_search_auto_paginates_every_page():
    pages = [
        _page(1, 3, [{"rcept_no": "A"}]),
        _page(2, 3, [{"rcept_no": "B"}]),
        _page(3, 3, [{"rcept_no": "C"}]),
    ]
    rows = Disclosure(_session_pages(pages)).search(
        begin_date="20260101", end_date="20260131")
    # all 3 pages fetched, no silent first-page-only cut
    assert [r["rcept_no"] for r in rows] == ["A", "B", "C"]


def test_search_max_pages_is_an_explicit_cap():
    pages = [
        _page(1, 3, [{"rcept_no": "A"}]),
        _page(2, 3, [{"rcept_no": "B"}]),
        _page(3, 3, [{"rcept_no": "C"}]),
    ]
    rows = Disclosure(_session_pages(pages)).search(max_pages=1)
    assert [r["rcept_no"] for r in rows] == ["A"]            # capped ON PURPOSE


def test_search_no_data_returns_empty():
    session = DartSession(api_key="TESTKEY")
    session._get = lambda endpoint, params: b'{"status": "013"}'  # type: ignore[method-assign]
    assert Disclosure(session).search(corp_code="00126380") == []


def test_company_returns_profile_body():
    body = {"status": "000", "corp_name": "삼성전자", "ceo_nm": "한종희",
            "stock_code": "005930", "est_dt": "19690113"}
    session = DartSession(api_key="TESTKEY")
    session._get = lambda endpoint, params: json.dumps(body).encode("utf-8")  # type: ignore[method-assign]
    profile = Disclosure(session).company("00126380")
    assert profile["corp_name"] == "삼성전자" and profile["stock_code"] == "005930"
