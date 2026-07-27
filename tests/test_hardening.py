"""Hardening tests added after the council review -- error-path typing, response-shape
guards, pagination edges, the endpoint-mapping contract, and bulk limits."""

import io
import json
import zipfile

import pytest

from opendartkit import (
    AuthError,
    DartClient,
    DartError,
    RateLimitError,
    ServerError,
    ValidationError,
)
from opendartkit._endpoint import DartEndpoint
from opendartkit.disclosure import Disclosure
from opendartkit.errors import error_for
from opendartkit.session import DartSession


def _session_returning_bytes(payload: bytes) -> DartSession:
    session = DartSession(api_key="TESTKEY")
    session._get = lambda endpoint, params: payload  # type: ignore[method-assign]
    return session


# --- error-path typing -----------------------------------------------------

def test_non_json_body_raises_dart_error_not_jsondecodeerror():
    # OpenDART serves HTML during maintenance; the caller must see a DartError.
    session = _session_returning_bytes(b"<html>maintenance</html>")
    from opendartkit.disclosure import SEARCH
    with pytest.raises(DartError) as exc:
        session.fetch_list(SEARCH)
    assert exc.value.status == "parse"


def test_fetch_bytes_on_error_xml_raises_typed_error_not_badzipfile():
    # A zip endpoint that fails returns error XML, not a zip. fetch_bytes must raise
    # AuthError -- not hand back bytes that later blow up as BadZipFile.
    err_xml = b"<result><status>010</status><message>bad key</message></result>"
    from opendartkit.client import CORP_CODE
    with pytest.raises(AuthError) as exc:
        _session_returning_bytes(err_xml).fetch_bytes(CORP_CODE)
    assert exc.value.status == "010"


def test_fetch_bytes_passes_a_real_zip_through():
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w") as archive:
        archive.writestr("x.xml", "<result></result>")
    zip_bytes = buffer.getvalue()
    from opendartkit.client import CORP_CODE
    assert _session_returning_bytes(zip_bytes).fetch_bytes(CORP_CODE) == zip_bytes


@pytest.mark.parametrize(
    ("status", "cls"),
    [
        ("010", AuthError), ("011", AuthError), ("012", AuthError),
        ("101", AuthError), ("901", AuthError),
        ("020", RateLimitError), ("021", RateLimitError),
        ("100", ValidationError),
        ("800", ServerError), ("900", ServerError),
        ("999", DartError),   # unknown -> base class fallback
    ],
)
def test_status_maps_to_the_right_error_class(status, cls):
    err = error_for(status, "msg", "http://guide")
    assert type(err) is cls
    assert err.status == status and err.guide_url == "http://guide"


# --- response-shape guards -------------------------------------------------

def test_fetch_groups_disambiguates_duplicate_titles():
    body = {"status": "000", "group": [
        {"title": "일반", "list": [{"a": "1"}]},
        {"title": "일반", "list": [{"b": "2"}]},   # same title -> must NOT overwrite
    ]}
    grouped = DartEndpoint("estkRs", "DS006", "2020054", response_shape="grouped")
    groups = _session_returning_bytes(json.dumps(body).encode()).fetch_groups(grouped)
    assert len(groups) == 2                       # both survive
    assert [{"a": "1"}] in groups.values() and [{"b": "2"}] in groups.values()


# --- pagination edges ------------------------------------------------------

def _paging_disclosure(pages: list[dict]) -> Disclosure:
    session = DartSession(api_key="TESTKEY")
    def _get(endpoint, params):
        return json.dumps(pages[int(str(params.get("page_no", "1"))) - 1]).encode()

    session._get = _get  # type: ignore[method-assign]
    return Disclosure(session)


def test_search_missing_total_page_stops_after_one_page():
    disclosure = _paging_disclosure([{"status": "000", "list": [{"n": "1"}]}])
    assert disclosure.search(corp_code="00126380") == [{"n": "1"}]


def test_search_zero_total_page_stops_after_one_page():
    disclosure = _paging_disclosure([{"status": "000", "total_page": "0", "list": []}])
    assert disclosure.search(corp_code="00126380") == []


def test_search_clamps_page_count_and_rejects_bad_max_pages():
    captured: dict = {}
    session = DartSession(api_key="TESTKEY")

    def _capture(endpoint, params):
        captured.update(params)
        return b'{"status": "000", "total_page": 1, "list": []}'

    session._get = _capture  # type: ignore[method-assign]
    Disclosure(session).search(corp_code="00126380", page_count=500)
    assert captured["page_count"] == "100"        # clamped to the DART max
    with pytest.raises(ValueError, match="max_pages"):
        Disclosure(session).search(corp_code="00126380", max_pages=0)


# --- the endpoint-mapping contract (all 85) --------------------------------

def _all_endpoints() -> list[DartEndpoint]:
    from opendartkit import (
        client,
        disclosure,
        event,
        finance,
        ownership,
        registration,
        report,
    )
    seen: dict[str, DartEndpoint] = {}
    for module in (client, disclosure, report, finance, ownership, event, registration):
        for value in vars(module).values():
            if isinstance(value, DartEndpoint):
                seen[value.operation] = value
    return list(seen.values())


def test_exactly_85_endpoints_are_wired():
    assert len(_all_endpoints()) == 85


def test_every_endpoint_is_well_formed():
    for ep in _all_endpoints():
        assert ep.operation and "." not in ep.operation   # a stem, no file extension
        assert ep.group in {"DS001", "DS002", "DS003", "DS004", "DS005", "DS006"}
        assert ep.payload_kind in {"json", "zip"}
        assert ep.response_shape in {"flat", "grouped"}
        assert f"apiId={ep.api_id}" in ep.guide_url
        assert ep.url.endswith(f"{ep.operation}.{'xml' if ep.payload_kind == 'zip' else 'json'}")


# --- bulk limit ------------------------------------------------------------

def test_multi_accounts_enforces_the_100_company_cap():
    client = DartClient(api_key="TESTKEY")

    def _get(endpoint, params):
        return b'{"status":"000","list":[]}'

    client._session._get = _get  # type: ignore[method-assign]
    with pytest.raises(ValueError, match="1..100"):
        client.finance.multi_accounts([], fiscal_year=2024)
    with pytest.raises(ValueError, match="1..100"):
        client.finance.multi_accounts([str(i) for i in range(101)], fiscal_year=2024)
