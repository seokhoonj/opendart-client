"""DartSession tests -- status contract, response shapes, boundary validation.

No network and no API key: the HTTP layer (``_get``) is stubbed to return canned
bytes, so the whole parse/validate pipeline is exercised offline.
"""

import json

import pytest

from opendartkit._endpoint import DartEndpoint
from opendartkit.errors import AuthError, DartError, RateLimitError
from opendartkit.session import DartSession

FLAT = DartEndpoint("list", "DS001", "2019001")
GROUPED = DartEndpoint("estkRs", "DS006", "2020054", response_shape="grouped")
REQUIRED = DartEndpoint("company", "DS001", "2019002", required=("corp_code",))


def _session(body: dict, *, capture: dict | None = None) -> DartSession:
    """A session whose HTTP layer always returns ``body`` (JSON-encoded)."""
    session = DartSession(api_key="TESTKEY")

    def _fake_get(endpoint, params):
        if capture is not None:
            capture.update(params)
        return json.dumps(body).encode("utf-8")

    session._get = _fake_get  # type: ignore[method-assign]
    return session


def test_missing_key_raises(monkeypatch):
    monkeypatch.delenv("OPENDART_API_KEY", raising=False)
    with pytest.raises(ValueError, match="OPENDART_API_KEY"):
        DartSession()


def test_env_key_is_used(monkeypatch):
    monkeypatch.setenv("OPENDART_API_KEY", "FROMENV")
    assert DartSession().api_key == "FROMENV"


def test_endpoint_url_and_guide():
    assert FLAT.url == "https://opendart.fss.or.kr/api/list.json"
    assert "apiGrpCd=DS001" in FLAT.guide_url and "apiId=2019001" in FLAT.guide_url


def test_fetch_list_ok_returns_rows():
    body = {"status": "000", "message": "정상",
            "list": [{"corp_name": "삼성전자", "rcept_no": "20260724800306"}]}
    rows = _session(body).fetch_list(FLAT)
    assert rows == [{"corp_name": "삼성전자", "rcept_no": "20260724800306"}]


def test_fetch_list_no_data_returns_empty():
    body = {"status": "013", "message": "조회된 데이터가 없습니다."}
    assert _session(body).fetch_list(FLAT) == []


def test_fetch_list_rate_limit_maps_to_subclass_with_guide():
    with pytest.raises(RateLimitError) as exc:
        _session({"status": "020", "message": "요청 제한 초과"}).fetch_list(FLAT)
    assert exc.value.status == "020"
    assert exc.value.guide_url and "apiId=2019001" in exc.value.guide_url


def test_fetch_list_bad_key_maps_to_auth_error():
    with pytest.raises(AuthError):
        _session({"status": "010", "message": "등록되지 않은 키"}).fetch_list(FLAT)


def test_fetch_list_on_grouped_body_raises_not_silent_empty():
    # The P0 guard: a grouped body has no top-level 'list'. fetch_list must RAISE,
    # never return a silent [] that masks 100% data loss on a 000 success.
    grouped_body = {"status": "000", "group": [{"title": "일반", "list": [{"a": 1}]}]}
    with pytest.raises(DartError, match="grouped endpoint"):
        _session(grouped_body).fetch_list(FLAT)


def test_fetch_groups_parses_titled_groups():
    body = {"status": "000", "group": [
        {"title": "증권의 종류", "list": [{"stksen": "보통주", "stkcnt": "100"}]},
        {"title": "인수인 정보", "list": [{"actsen": "대표주관", "actnmn": "A증권"}]},
    ]}
    groups = _session(body).fetch_groups(GROUPED)
    assert set(groups) == {"증권의 종류", "인수인 정보"}
    assert groups["증권의 종류"] == [{"stksen": "보통주", "stkcnt": "100"}]


def test_fetch_groups_no_data_returns_empty_dict():
    assert _session({"status": "013"}).fetch_groups(GROUPED) == {}


def test_fetch_groups_on_flat_body_raises():
    with pytest.raises(DartError, match="flat endpoint"):
        _session({"status": "000", "list": [{"a": 1}]}).fetch_groups(GROUPED)


def test_required_param_rejected_before_any_http():
    called = {"hit": False}
    session = DartSession(api_key="TESTKEY")

    def _must_not_run(endpoint, params):
        called["hit"] = True
        return b"{}"

    session._get = _must_not_run  # type: ignore[method-assign]
    with pytest.raises(ValueError, match="corp_code"):
        session.fetch_body(REQUIRED)  # no corp_code
    assert not called["hit"]


def test_crtfc_key_injected_into_query():
    captured: dict = {}
    _session({"status": "000", "list": []}, capture=captured).fetch_list(
        FLAT, corp_code="00126380")
    # the key is added inside _get, which the stub replaces, so we assert the
    # caller-supplied params reach _get untouched (key injection is _get's job).
    assert captured["corp_code"] == "00126380"
