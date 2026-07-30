"""Command-line tests with a fully offline fake client."""

import json
from typing import ClassVar

from opendart_client import cli

ROWS = [
    {
        "corp_code": "00126380",
        "corp_name": "삼성전자",
        "stock_code": "005930",
        "modify_date": "20260101",
    },
    {
        "corp_code": "00999999",
        "corp_name": "삼성전자서비스",
        "stock_code": None,
        "modify_date": "20260101",
    },
]
FILINGS = [
    {"rcept_dt": "20260103", "rcept_no": "3", "report_nm": "세 번째"},
    {"rcept_dt": "20260102", "rcept_no": "2", "report_nm": "두 번째"},
    {"rcept_dt": "20260101", "rcept_no": "1", "report_nm": "첫 번째"},
]
COMPANY = {"corp_name": "삼성전자", "ceo_nm": "대표", "stock_code": "005930"}
ACCOUNTS = [
    {"account_nm": "매출액", "fs_div": "CFS", "thstrm_amount": "1234567"},
    {"account_nm": "영업이익", "fs_div": "CFS", "thstrm_amount": "12,345"},
    # DART labels net income "당기순이익(손실)" and repeats it (지배/비지배); the summary
    # must still surface it, taking the first row only.
    {"account_nm": "당기순이익(손실)", "fs_div": "CFS", "thstrm_amount": "500000"},
    {"account_nm": "당기순이익(손실)", "fs_div": "CFS", "thstrm_amount": "400000"},
    {"account_nm": "매출액", "fs_div": "OFS", "thstrm_amount": "7654321"},
    {"account_nm": "기타", "fs_div": "CFS", "thstrm_amount": "999"},
]


class FakeResolver:
    def __init__(self):
        self.resolve_calls = []

    def search(self, query):
        return [] if query == "missing" else ROWS

    def resolve(self, company):
        self.resolve_calls.append(company)
        return "00126380"


class FakeDisclosure:
    def __init__(self):
        self.search_calls = []

    def search(self, **kwargs):
        self.search_calls.append(kwargs)
        return FILINGS

    def company(self, corp_code):
        return COMPANY


class FakeFinance:
    def single_accounts(self, corp_code, *, fiscal_year, report_code):
        return ACCOUNTS


class FakeOpenDart:
    instances: ClassVar[list["FakeOpenDart"]] = []

    def __init__(self, api_key=None, *, timeout=30.0):
        self._resolver = FakeResolver()
        self.disclosure = FakeDisclosure()
        self.finance = FakeFinance()
        self.instances.append(self)

    def resolver(self):
        return self._resolver


def test_resolve_readable(monkeypatch, capsys):
    monkeypatch.setattr(cli, "OpenDart", FakeOpenDart)
    assert cli.main(["--api-key", "x", "resolve", "삼성"]) == 0
    assert capsys.readouterr().out.splitlines() == [
        "00126380  005930  삼성전자",
        "00999999  ------  삼성전자서비스",
    ]


def test_resolve_json(monkeypatch, capsys):
    monkeypatch.setattr(cli, "OpenDart", FakeOpenDart)
    assert cli.main(["--api-key", "x", "resolve", "삼성", "--json"]) == 0
    assert json.loads(capsys.readouterr().out) == ROWS


def test_resolve_no_match(monkeypatch, capsys):
    monkeypatch.setattr(cli, "OpenDart", FakeOpenDart)
    assert cli.main(["--api-key", "x", "resolve", "missing"]) == 1
    assert "no company matches 'missing'" in capsys.readouterr().err


def test_finance_readable_and_separate(monkeypatch, capsys):
    monkeypatch.setattr(cli, "OpenDart", FakeOpenDart)
    assert cli.main(["--api-key", "x", "finance", "삼성", "--year", "2025"]) == 0
    output = capsys.readouterr().out
    assert "매출액        1,234,567" in output
    assert "영업이익       12,345" in output
    assert "당기순이익" in output and "500,000" in output   # (손실) label still matched
    assert "400,000" not in output                          # duplicate row not printed
    assert "7,654,321" not in output

    assert cli.main(
        ["--api-key", "x", "finance", "삼성", "--year", "2025", "--separate"]
    ) == 0
    output = capsys.readouterr().out
    assert "(OFS 별도)" in output
    assert "매출액        7,654,321" in output
    assert "1,234,567" not in output


def test_company_json(monkeypatch, capsys):
    monkeypatch.setattr(cli, "OpenDart", FakeOpenDart)
    assert cli.main(["--api-key", "x", "company", "삼성", "--json"]) == 0
    assert json.loads(capsys.readouterr().out) == COMPANY


def test_search_limit_and_corp_code_passthrough(monkeypatch, capsys):
    monkeypatch.setattr(cli, "OpenDart", FakeOpenDart)
    assert cli.main(["--api-key", "x", "search", "00126380", "--limit", "2"]) == 0
    output = capsys.readouterr().out.splitlines()
    assert output == [
        "00126380  3 filings",
        "20260103  3  세 번째",
        "20260102  2  두 번째",
    ]
    instance = FakeOpenDart.instances[-1]
    assert instance.resolver().resolve_calls == []


def test_no_subcommand_returns_two(capsys):
    assert cli.main([]) == 2
    assert "usage: opendart" in capsys.readouterr().out
