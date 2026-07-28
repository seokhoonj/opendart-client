"""Edge coverage added in council round 2 -- the real URL/key path, non-object JSON,
valid-empty-zip, response-shape enforcement on 013, bulk boundaries, the binary public
paths, and the company envelope."""

import io
import json
import zipfile

import pytest

from opendart_client import DartError, OpenDart
from opendart_client._endpoint import DartEndpoint
from opendart_client.session import DartSession


def _zip(names_to_xml: dict[str, str]) -> bytes:
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w") as archive:
        for name, xml in names_to_xml.items():
            archive.writestr(name, xml)
    return buffer.getvalue()


def _empty_zip() -> bytes:
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w"):
        pass
    return buffer.getvalue()   # a valid archive that begins with PK\x05\x06, not PK\x03\x04


# --- the real _get URL / key path (not stubbed away) -----------------------

def test_get_builds_url_with_key_params_and_honors_timeout(monkeypatch):
    captured: dict = {}

    class _Resp:
        def __enter__(self):
            return self

        def __exit__(self, *a):
            return False

        def read(self):
            return b'{"status": "000", "list": []}'

    def _fake_urlopen(request, timeout):
        captured["url"] = request.full_url
        captured["timeout"] = timeout
        return _Resp()

    monkeypatch.setattr("urllib.request.urlopen", _fake_urlopen)
    from opendart_client.disclosure import SEARCH
    DartSession(api_key="TESTKEY", timeout=12.5).fetch_list(SEARCH, corp_code="00126380")
    assert "crtfc_key=TESTKEY" in captured["url"]
    assert "corp_code=00126380" in captured["url"]
    assert captured["url"].startswith("https://opendart.fss.or.kr/api/list.json?")
    assert captured["timeout"] == 12.5


# --- non-object JSON --------------------------------------------------------

@pytest.mark.parametrize("payload", [b"[]", b"null", b'"text"', b"123"])
def test_non_object_json_body_raises_dart_error(payload):
    from opendart_client.disclosure import SEARCH
    session = DartSession(api_key="TESTKEY")
    session._get = lambda endpoint, params: payload  # type: ignore[method-assign]
    with pytest.raises(DartError) as exc:
        session.fetch_list(SEARCH)
    assert exc.value.status == "parse"


# --- valid empty zip --------------------------------------------------------

def test_fetch_bytes_accepts_a_valid_empty_zip():
    from opendart_client.client import CORP_CODE
    session = DartSession(api_key="TESTKEY")
    empty = _empty_zip()
    session._get = lambda endpoint, params: empty  # type: ignore[method-assign]
    assert session.fetch_bytes(CORP_CODE) == empty   # not falsely rejected as error XML


# --- response-shape enforced at entry, even on 013 --------------------------

def test_grouped_endpoint_via_fetch_list_raises_even_on_no_data():
    grouped = DartEndpoint("estkRs", "DS006", "2020054", response_shape="grouped")
    session = DartSession(api_key="TESTKEY")
    session._get = lambda endpoint, params: b'{"status": "013"}'  # type: ignore[method-assign]
    with pytest.raises(DartError, match="use fetch_groups"):
        session.fetch_list(grouped)   # the 013 would otherwise become a silent []


def test_flat_endpoint_via_fetch_groups_raises_even_on_no_data():
    flat = DartEndpoint("list", "DS001", "2019001")
    session = DartSession(api_key="TESTKEY")
    session._get = lambda endpoint, params: b'{"status": "013"}'  # type: ignore[method-assign]
    with pytest.raises(DartError, match="use fetch_list"):
        session.fetch_groups(flat)


# --- duplicate group titles, including collision with a generated suffix -----

def test_fetch_groups_survives_title_that_collides_with_the_generated_suffix():
    body = {"status": "000", "group": [
        {"title": "A (1)", "list": [{"x": "0"}]},
        {"title": "A", "list": [{"x": "1"}]},
        {"title": "A", "list": [{"x": "2"}]},   # -> "A (1)" is taken, must become "A (2)"
    ]}
    grouped = DartEndpoint("estkRs", "DS006", "2020054", response_shape="grouped")
    session = DartSession(api_key="TESTKEY")
    session._get = lambda endpoint, params: json.dumps(body).encode()  # type: ignore[method-assign]
    groups = session.fetch_groups(grouped)
    assert len(groups) == 3   # every group survives under a distinct key
    assert list(groups.values()) == [[{"x": "0"}], [{"x": "1"}], [{"x": "2"}]]


# --- bulk boundaries on BOTH bulk methods -----------------------------------

def _finance_client() -> OpenDart:
    client = OpenDart(api_key="TESTKEY")
    client._session._get = lambda endpoint, params: b'{"status":"000","list":[]}'  # type: ignore[method-assign]
    return client


@pytest.mark.parametrize("n", [1, 100])
def test_bulk_methods_accept_1_to_100(n):
    client = _finance_client()
    codes = [f"{i:08d}" for i in range(n)]
    client.finance.multi_accounts(codes, fiscal_year=2024)
    client.finance.multi_indicators(codes, fiscal_year=2024, index_class="M210000")


@pytest.mark.parametrize("n", [0, 101])
def test_bulk_methods_reject_out_of_range(n):
    client = _finance_client()
    codes = [f"{i:08d}" for i in range(n)]
    with pytest.raises(ValueError, match="1..100"):
        client.finance.multi_accounts(codes, fiscal_year=2024)
    with pytest.raises(ValueError, match="1..100"):
        client.finance.multi_indicators(codes, fiscal_year=2024, index_class="M210000")


def test_bulk_methods_reject_a_bare_str():
    client = _finance_client()
    with pytest.raises(TypeError, match="not a single str"):
        client.finance.multi_accounts("00126380", fiscal_year=2024)


# --- the three binary public paths, end to end ------------------------------

def test_corp_codes_parses_a_stubbed_zip():
    xml = ("<result><list><corp_code>00126380</corp_code><corp_name>삼성전자</corp_name>"
           "<stock_code>005930</stock_code><modify_date>20230101</modify_date></list></result>")
    client = OpenDart(api_key="TESTKEY")
    captured: dict = {}

    def _get(endpoint, params):
        captured["operation"] = endpoint.operation
        return _zip({"CORPCODE.xml": xml})

    client._session._get = _get  # type: ignore[method-assign]
    rows = client.corp_codes()
    assert captured["operation"] == "corpCode"
    assert rows[0]["corp_name"] == "삼성전자" and rows[0]["stock_code"] == "005930"


def test_document_and_xbrl_return_raw_zip_bytes():
    client = OpenDart(api_key="TESTKEY")
    payload = _zip({"doc.xml": "<x/>"})
    seen: dict = {}

    def _get(endpoint, params):
        seen["op"] = endpoint.operation
        seen["params"] = dict(params)
        return payload

    client._session._get = _get  # type: ignore[method-assign]
    assert client.disclosure.document("20260724800306") == payload
    assert seen["op"] == "document" and seen["params"]["rcept_no"] == "20260724800306"
    assert client.finance.xbrl_document("20260724800306", report_code="11011") == payload
    assert seen["op"] == "fnlttXbrl" and seen["params"]["reprt_code"] == "11011"


def test_binary_public_path_propagates_error_xml_as_typed_error():
    from opendart_client import AuthError
    client = OpenDart(api_key="TESTKEY")
    client._session._get = (  # type: ignore[method-assign]
        lambda endpoint, params: b"<result><status>010</status><message>bad key</message></result>"
    )
    with pytest.raises(AuthError):
        client.corp_codes()


# --- company returns the whole validated body -------------------------------

def test_company_returns_the_full_body_envelope():
    body = {"status": "000", "message": "정상", "corp_name": "삼성전자",
            "ceo_nm": "한종희", "stock_code": "005930", "est_dt": "19690113"}
    client = OpenDart(api_key="TESTKEY")
    client._session._get = lambda endpoint, params: json.dumps(body).encode()  # type: ignore[method-assign]
    assert client.disclosure.company("00126380") == body   # nothing stripped


def test_search_raises_on_a_000_body_missing_list():
    from opendart_client.disclosure import Disclosure
    session = DartSession(api_key="TESTKEY")
    session._get = lambda endpoint, params: b'{"status": "000", "total_page": 1}'  # type: ignore[method-assign]
    with pytest.raises(DartError, match="no 'list'"):
        Disclosure(session).search(corp_code="00126380")
