"""Client tests -- the corpCode zip parse (pure, no network)."""

import io
import zipfile

import pytest

from opendartclient.client import _parse_corp_code_zip
from opendartclient.errors import AuthError, DartError

_XML = (
    "<result>"
    "<list><corp_code>00126380</corp_code><corp_name>삼성전자</corp_name>"
    "<stock_code>005930</stock_code><modify_date>20230101</modify_date></list>"
    "<list><corp_code>00434003</corp_code><corp_name>Unlisted Co</corp_name>"
    "<stock_code> </stock_code><modify_date>20230102</modify_date></list>"
    "</result>"
)


def _zip_of(xml: str, name: str = "CORPCODE.xml") -> bytes:
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as archive:
        archive.writestr(name, xml.encode("utf-8"))
    return buffer.getvalue()


def test_parse_corp_code_zip_returns_rows():
    rows = _parse_corp_code_zip(_zip_of(_XML))
    assert rows[0] == {
        "corp_code": "00126380", "corp_name": "삼성전자",
        "stock_code": "005930", "modify_date": "20230101",
    }
    # A blank stock_code (unlisted company) becomes None, not "".
    assert rows[1]["stock_code"] is None


def test_parse_corp_code_zip_empty_list():
    assert _parse_corp_code_zip(_zip_of("<result></result>")) == []


def test_parse_corp_code_zip_error_xml_maps_to_subclass():
    err = b"<result><status>010</status><message>unregistered key</message></result>"
    with pytest.raises(AuthError) as exc:      # 010 -> AuthError, not a bare DartError
        _parse_corp_code_zip(err)
    assert exc.value.status == "010" and "unregistered" in exc.value.message


def test_parse_corp_code_zip_unrecognized_payload_raises():
    with pytest.raises(DartError):
        _parse_corp_code_zip(b"not xml, not zip")
