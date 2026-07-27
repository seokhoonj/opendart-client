# OpenDartClient

[한국어](https://github.com/seokhoonj/opendart-client/blob/main/README.ko.md)

A clean, typed Python client for Korea's **OpenDART** (전자공시) — the Financial
Supervisory Service's electronic disclosure system, Korea's answer to SEC EDGAR.

Zero dependencies. Sync. Returns plain `dict` / `list[dict]`, so you frame it your way.

## Install

```bash
pip install opendart-client
```

Get a free API key (40 chars) at <https://opendart.fss.or.kr>.

## Quickstart

```python
from opendartclient import OpenDart

dart = OpenDart(api_key="...")          # or set OPENDART_API_KEY in the environment

# resolve a name / ticker / 초성 / typo -> corp_code
code = dart.resolver().resolve("삼성전자")          # "00126380"

# disclosures filed in a date window
rows = dart.disclosure.search(
    corp_code=code, begin_date="20260101", end_date="20260131",
)

# financial statements, and any corporate event
dart.finance.single_accounts(code, fiscal_year=2025)
dart.event.paid_in_capital_increase(
    corp_code=code, begin_date="20260101", end_date="20260131",
)

# want a DataFrame? (optional extra)
from opendartclient import to_pandas
to_pandas(rows)
```

## Features

- **All 85 OpenDART endpoints** across six groups — disclosure, periodic reports,
  financial statements, ownership, major-event reports, securities registration —
  as readable methods (`dart.event.convertible_bond(...)`, not `cvbdIsDecsn`).
- **Company resolver** — name / ticker / 초성 (`ㅅㅅㅈㅈ`) / typo → `corp_code`.
- **Zero runtime dependencies** — the standard library carries it all. `pandas` and
  `polars` are opt-in extras (`pip install 'opendart-client[pandas]'`).
- **Fully typed**, ships `py.typed`; closed vocabularies are `Literal`s, so a bad code
  fails the type checker, not the API.
- **Raw returns** — `list[dict]` (flat), `dict[str, list[dict]]` (grouped), `bytes`
  (zip endpoints). `status 013` (no data) is an empty result; other errors raise a
  typed `DartError`.

## License

MIT © Seokhoon Joo
