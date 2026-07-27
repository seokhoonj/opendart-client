"""CorpResolver tests -- name / ticker / corp_code / 초성 / typo -> corp_code, offline."""

from typing import Any

import pytest

from opendartclient.resolver import CorpResolver, choseong


def _row(corp_code: str, name: str, stock: str | None) -> dict[str, Any]:
    return {"corp_code": corp_code, "corp_name": name, "stock_code": stock, "modify_date": "x"}


_ROWS: list[dict[str, Any]] = [
    _row("00126380", "삼성전자", "005930"),
    _row("00164779", "SK하이닉스", "000660"),
    _row("00126362", "삼성전자서비스", None),       # unlisted, longer name
    _row("00999999", "삼성물산", "028260"),
    _row("00000000", "없는회사", None),
]


@pytest.fixture
def resolver() -> CorpResolver:
    return CorpResolver(_ROWS)


def test_choseong_extracts_leading_consonants():
    assert choseong("삼성전자") == "ㅅㅅㅈㅈ"
    assert choseong("SK하이닉스") == "ㅎㅇㄴㅅ"     # latin dropped; 하이닉스 only
    assert choseong("") == ""


def test_resolve_passes_through_a_corp_code(resolver):
    assert resolver.resolve("00126380") == "00126380"


def test_resolve_a_ticker(resolver):
    assert resolver.resolve("005930") == "00126380"     # 삼성전자's stock code


def test_resolve_an_exact_name(resolver):
    assert resolver.resolve("삼성전자") == "00126380"


def test_resolve_a_choseong_query_prefers_the_listed_shorter_match(resolver):
    # "ㅅㅅㅈㅈ" matches both 삼성전자 (listed) and 삼성전자서비스 (unlisted, longer);
    # listed-and-shorter wins.
    assert resolver.resolve("ㅅㅅㅈㅈ") == "00126380"


def test_resolve_tolerates_a_typo(resolver):
    assert resolver.resolve("삼서전자") == "00126380"    # difflib fuzzy


def test_resolve_raises_when_nothing_matches(resolver):
    with pytest.raises(ValueError, match="no company matches"):
        resolver.resolve("존재하지않는기업명xyz")


def test_search_returns_ranked_candidates(resolver):
    hits = resolver.search("삼성")
    names = [r["corp_name"] for r in hits]
    assert "삼성전자" in names and "삼성물산" in names
    # listed companies (with a stock_code) rank before the unlisted 삼성전자서비스
    assert names.index("삼성전자") < names.index("삼성전자서비스")


def test_search_by_choseong(resolver):
    hits = resolver.search("ㅅㅅ")
    assert {r["corp_code"] for r in hits} >= {"00126380", "00126362", "00999999"}


def test_resolve_ambiguous_exact_name_raises():
    rows = [_row("A", "동명", "111111"), _row("B", "동명", "222222")]
    with pytest.raises(ValueError, match="matches 2 companies"):
        CorpResolver(rows).resolve("동명")


def test_search_empty_or_whitespace_returns_empty(resolver):
    assert resolver.search("") == []
    assert resolver.search("   ") == []


def test_resolve_all_choseong_no_match_raises(resolver):
    # a well-formed 초성 query that matches nothing raises, not returns garbage
    with pytest.raises(ValueError, match="no company matches"):
        resolver.resolve("ㅋㅋㅋㅋㅋ")


def test_search_multi_substring_ranks_deterministically(resolver):
    # "삼성" is inside three names; listed-before-unlisted then shorter-name is stable.
    names = [r["corp_name"] for r in resolver.search("삼성")]
    assert names == ["삼성전자", "삼성물산", "삼성전자서비스"]
