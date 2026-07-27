"""Company resolver (optional Layer 2) -- turn a human handle into a corp_code.

Most OpenDART endpoints are keyed by an 8-digit ``corp_code`` that nobody remembers.
This resolves a company **name** ("삼성전자"), a 6-digit **ticker** ("005930"), an
8-digit **corp_code** (passed through), a **초성** query ("ㅅㅅㅈㅈ"), or a **typo**
("삼서전자") to the corp_code -- built once from ``OpenDart.corp_codes()`` and then
pure/offline. Zero dependencies: ``difflib`` (stdlib) does the fuzzy matching.
"""

from __future__ import annotations

import difflib
from typing import Any

# 초성 19자 (호환 자모). Index i is the leading consonant of a syllable whose
# (code - 0xAC00) // 588 == i, and is also what a user types in a 초성 query.
_CHOSEONG = "ㄱㄲㄴㄷㄸㄹㅁㅂㅃㅅㅆㅇㅈㅉㅊㅋㅌㅍㅎ"
_SYLLABLE_FIRST = 0xAC00
_SYLLABLE_LAST = 0xD7A3
_JAMO_PER_CHOSEONG = 588   # 21 jungseong x 28 jongseong

Row = dict[str, Any]


def chosung(text: str) -> str:
    """The 초성 (leading consonants) of a Korean string; non-Hangul chars are dropped.
    ``chosung("삼성전자") == "ㅅㅅㅈㅈ"``."""
    out: list[str] = []
    for char in text:
        code = ord(char)
        if _SYLLABLE_FIRST <= code <= _SYLLABLE_LAST:
            out.append(_CHOSEONG[(code - _SYLLABLE_FIRST) // _JAMO_PER_CHOSEONG])
        elif char in _CHOSEONG:               # already a bare 초성 jamo
            out.append(char)
    return "".join(out)


class CorpResolver:
    """Resolve a name / ticker / corp_code / 초성 / typo to a corp_code.

    Build from the ``corp_codes()`` rows once; every lookup is then in-memory. A row is
    ``{corp_code, corp_name, stock_code (None if unlisted), modify_date}``.
    """

    def __init__(self, rows: list[Row]) -> None:
        self._rows = [r for r in rows if r.get("corp_code")]
        self._by_corp_code: dict[str, Row] = {r["corp_code"]: r for r in self._rows}
        self._by_stock_code: dict[str, Row] = {
            r["stock_code"]: r for r in self._rows if r.get("stock_code")
        }
        self._by_name: dict[str, list[Row]] = {}
        for r in self._rows:
            self._by_name.setdefault(r.get("corp_name", ""), []).append(r)
        self._name_chosung: dict[str, str] = {
            r["corp_code"]: chosung(r.get("corp_name", "")) for r in self._rows
        }

    def search(self, query: str, *, limit: int = 10) -> list[Row]:
        """Candidate rows for a handle, best first (listed before unlisted, then shorter
        name). Exact ticker/corp_code short-circuit to a single row."""
        q = query.strip()
        if not q:
            return []
        if q in self._by_stock_code:
            return [self._by_stock_code[q]]
        if q in self._by_corp_code:
            return [self._by_corp_code[q]]
        if all(char in _CHOSEONG for char in q):          # a 초성 query like "ㅅㅅㅈㅈ"
            hits = [r for r in self._rows if self._name_chosung[r["corp_code"]].startswith(q)]
        else:
            exact = self._by_name.get(q, [])
            starts = [r for r in self._rows
                      if r["corp_name"].startswith(q) and r["corp_name"] != q]
            contains = [r for r in self._rows
                        if q in r["corp_name"] and not r["corp_name"].startswith(q)]
            hits = [*exact, *starts, *contains]
            if not hits:                                   # typo-tolerant fallback
                for name in difflib.get_close_matches(q, list(self._by_name), n=limit, cutoff=0.6):
                    hits.extend(self._by_name[name])
        seen: set[str] = set()
        unique: list[Row] = []
        for r in hits:
            if r["corp_code"] not in seen:
                seen.add(r["corp_code"])
                unique.append(r)
        unique.sort(key=lambda r: (r.get("stock_code") is None, len(r["corp_name"])))
        return unique[:limit]

    def resolve(self, query: str) -> str:
        """The single corp_code for a handle. Passes an 8-digit corp_code through and
        resolves a 6-digit ticker directly. Raises ``ValueError`` if nothing matches, or
        if a name is exactly shared by several companies (use ``search`` to disambiguate)."""
        q = query.strip()
        if q in self._by_corp_code:
            return q
        if q in self._by_stock_code:
            return str(self._by_stock_code[q]["corp_code"])
        exact = self._by_name.get(q)
        if exact:
            if len(exact) > 1:
                codes = [r["corp_code"] for r in exact]
                raise ValueError(f"{q!r} matches {len(exact)} companies {codes}; use search()")
            return str(exact[0]["corp_code"])
        hits = self.search(q, limit=1)
        if not hits:
            raise ValueError(f"no company matches {query!r}")
        return str(hits[0]["corp_code"])
