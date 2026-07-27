"""Sub-surface wiring + request-shaping tests (event / finance / report /
registration / ownership), all offline via a stubbed session."""

import json

import pytest

from opendartkit import DartClient


def _client(body: dict, *, capture: dict | None = None) -> DartClient:
    client = DartClient(api_key="TESTKEY")

    def _fake_get(endpoint, params):
        if capture is not None:
            capture.clear()
            capture.update(params)
            capture["__operation__"] = endpoint.operation
        return json.dumps(body).encode("utf-8")

    client._session._get = _fake_get  # type: ignore[method-assign]
    return client


def test_client_wires_all_six_sub_surfaces():
    client = DartClient(api_key="TESTKEY")
    for surface in ("disclosure", "report", "finance", "ownership", "event", "registration"):
        assert hasattr(client, surface)


def test_event_sends_corp_code_and_date_window():
    captured: dict = {}
    body = {"status": "000", "list": [{"rcept_no": "20260724800306"}]}
    client = _client(body, capture=captured)
    rows = client.event.paid_in_capital_increase(
        corp_code="00126380", begin_date="20260101", end_date="20260731")
    assert rows == [{"rcept_no": "20260724800306"}]
    assert captured["__operation__"] == "piicDecsn"
    assert captured["corp_code"] == "00126380"
    assert captured["bgn_de"] == "20260101" and captured["end_de"] == "20260731"


def test_finance_multi_accounts_joins_corp_codes_and_stringifies_year():
    captured: dict = {}
    client = _client({"status": "000", "list": []}, capture=captured)
    client.finance.multi_accounts(["00126380", "00164779"], fiscal_year=2025)
    assert captured["__operation__"] == "fnlttMultiAcnt"
    assert captured["corp_code"] == "00126380,00164779"
    assert captured["bsns_year"] == "2025"        # int -> str at the boundary
    assert captured["reprt_code"] == "11011"       # default 사업보고서


def test_report_dividends_sends_periodic_params():
    captured: dict = {}
    client = _client({"status": "000", "list": [{"stock_knd": "보통주"}]}, capture=captured)
    rows = client.report.dividends("00126380", fiscal_year=2024, report_code="11011")
    assert rows == [{"stock_knd": "보통주"}]
    assert captured["__operation__"] == "alotMatter"
    assert captured["bsns_year"] == "2024"


def test_registration_returns_grouped_dict():
    body = {"status": "000", "group": [
        {"title": "일반사항", "list": [{"a": "1"}]},
        {"title": "인수인", "list": [{"b": "2"}]},
    ]}
    client = _client(body)
    groups = client.registration.equity_securities(
        corp_code="00126380", begin_date="20260101", end_date="20260731")
    assert set(groups) == {"일반사항", "인수인"}
    assert groups["인수인"] == [{"b": "2"}]


def test_ownership_five_percent_holdings():
    captured: dict = {}
    client = _client({"status": "000", "list": []}, capture=captured)
    client.ownership.five_percent_holdings("00126380")
    assert captured["__operation__"] == "majorstock"
    assert captured["corp_code"] == "00126380"


def test_missing_required_param_raises_before_call():
    client = DartClient(api_key="TESTKEY")
    called = {"hit": False}

    def _must_not_run(endpoint, params):
        called["hit"] = True
        return b"{}"

    client._session._get = _must_not_run  # type: ignore[method-assign]
    with pytest.raises(ValueError, match="bgn_de"):
        client.event.merger(corp_code="00126380", begin_date="", end_date="20260731")
    assert not called["hit"]
