# OpenDartClient

A clean, sync, typed Python client for Korea's **OpenDART** (금융감독원 전자공시시스템)
disclosure API — the Korean equivalent of the SEC's EDGAR.

- **Zero runtime dependencies.** The standard library (`urllib`, `json`, `zipfile`,
  `ElementTree`) carries the whole client. pandas / polars are opt-in extras.
- **Sync.** Fits ETL scripts and notebooks without `asyncio` ceremony.
- **Raw `dict` / `list[dict]` returns.** DataFrame-agnostic; frame it your way.
- **Fully typed**, ships `py.typed`. Closed vocabularies (report codes, corp class,
  sort order, …) are `Literal`s, so a bad code fails the type checker, not the API.
- **Readable method names.** `disclosure.search`, not the raw DART stem `list`.
- **API-only.** No website scraping, no XBRL engine — just the official endpoints, so
  it does not break when the DART site is redesigned.

## Install

```bash
pip install opendartclient
# optional frame helpers
pip install 'opendartclient[pandas]'
pip install 'opendartclient[polars]'
```

Get a free API key (40 chars) at <https://opendart.fss.or.kr>.

## Quickstart

```python
from opendartclient import OpenDart

dart = OpenDart(api_key="...")        # or set OPENDART_API_KEY in the environment

# 1) Which disclosures were filed, and when
rows = dart.disclosure.search(
    corp_code="00126380",               # 삼성전자
    begin_date="20260101", end_date="20260131",
)                                        # -> list[dict], every page fetched

# 2) Company profile behind a corp_code
profile = dart.disclosure.company("00126380")   # -> dict

# 3) The corp_code <-> stock_code mapping (the base table)
corps = dart.corp_codes()               # -> list[dict]

# 4) Resolve a name / ticker / 초성 / typo to a corp_code (optional, built once)
r = dart.resolver()
r.resolve("삼성전자")                    # -> "00126380"
r.resolve("005930")                      # ticker  -> "00126380"
r.resolve("ㅅㅅㅈㅈ")                     # 초성    -> "00126380"
r.resolve("삼서전자")                     # typo    -> "00126380"

# Frame it however you like (optional):
from opendartclient import to_pandas
df = to_pandas(rows)
```

## Return shapes

- Flat endpoints return `list[dict]` (the API's own field keys, untouched).
- Grouped endpoints (securities registration; some reports) return
  `dict[str, list[dict]]`, keyed by each group's title.
- Zip endpoints return raw `bytes`: `disclosure.document(rcept_no)` and
  `finance.xbrl_document(rcept_no, report_code=...)` hand back the archive for the
  caller to unzip. `corp_codes()` is the exception — it parses its zip into
  `list[dict]` for you.
- `status 013` (no data) is an expected empty (`[]` / `{}`), never an error.
- Other error statuses raise a typed `DartError` subclass (`AuthError`,
  `RateLimitError`, `ValidationError`, `ServerError`) carrying the status and the
  guide-page URL of the failing endpoint.

## Scope

Wraps the OpenDART REST API across its six groups (disclosure, periodic reports,
financial statements, ownership, major-event reports, securities registration).
Storage, cross-source joins, and analysis are deliberately **not** here — this is a
pure client; build those on top.

## License

MIT © Seokhoon Joo
