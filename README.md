# opendart-client

[![check](https://github.com/seokhoonj/opendart-client/actions/workflows/check.yml/badge.svg)](https://github.com/seokhoonj/opendart-client/actions/workflows/check.yml)
[![PyPI](https://img.shields.io/pypi/v/opendart-client)](https://pypi.org/project/opendart-client/)
[![Python](https://img.shields.io/pypi/pyversions/opendart-client)](https://pypi.org/project/opendart-client/)
[![License](https://img.shields.io/pypi/l/opendart-client)](https://github.com/seokhoonj/opendart-client/blob/main/LICENSE)

**English** | [한국어](https://github.com/seokhoonj/opendart-client/blob/main/README.ko.md)

A clean, typed Python client for Korea's **OpenDART** (전자공시) — the Financial
Supervisory Service's electronic disclosure system.

Zero dependencies. Sync. Returns plain `dict` / `list[dict]`, so you frame it your way.

## Install

```bash
pip install opendart-client
```

Get a free API key (40 chars) at <https://opendart.fss.or.kr>.

## Quickstart

```python
from opendart_client import OpenDart

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

# want a DataFrame? returns are list[dict], which the constructors take directly
import pandas as pd
pd.DataFrame(rows)
# or
import polars as pl
pl.DataFrame(rows)
```

## Features

- **All 85 OpenDART endpoints** across six groups — disclosure, periodic reports,
  financial statements, ownership, major-event reports, securities registration —
  as readable methods (`dart.event.convertible_bond(...)`, not `cvbdIsDecsn`).
- **Company resolver** — name / ticker / 초성 (`ㅅㅅㅈㅈ`) / typo → `corp_code`.
- **Zero runtime dependencies** — the standard library carries it all. Rows come back
  as `list[dict]`, which `pandas.DataFrame` / `polars.DataFrame` accept directly, so
  no DataFrame adapter is needed.
- **Fully typed**, ships `py.typed`; closed vocabularies are `Literal`s, so a bad code
  fails the type checker, not the API.
- **Raw returns** — `list[dict]` (flat), `dict[str, list[dict]]` (grouped), `bytes`
  (zip endpoints). `status 013` (no data) is an empty result; other errors raise a
  typed `DartError`.

## API

Top level: `dart.corp_codes()` (all corp_code ↔ name / ticker), `dart.resolver()` →
`CorpResolver.resolve(query)` / `.search(query)`.

`report_code` defaults to `"11011"` (annual report). Others: `11012` half-year,
`11013` Q1, `11014` Q3.

### disclosure

| Method | Description |
|---|---|
| `search(corp_code=…, begin_date=…, end_date=…, …)` | Filings matching the window / filters (auto-paginated) |
| `company(corp_code)` | Company profile (name, ceo, address, industry, …) |
| `document(rcept_no)` | Original filing as raw zip `bytes` |

### report (periodic-report key items)

All take `(corp_code, *, fiscal_year, report_code="11011")`.

| Method | Description |
|---|---|
| `total_shares` | Total number of shares |
| `treasury_shares` | Treasury stock acquired and disposed |
| `dividends` | Dividends |
| `capital_changes` | Capital increase / reduction history |
| `debt_securities_issued` | Debt securities issuance record |
| `commercial_paper_outstanding` | Commercial paper outstanding balance |
| `short_term_bond_outstanding` | Short-term bond outstanding balance |
| `corporate_bond_outstanding` | Corporate bond outstanding balance |
| `hybrid_security_outstanding` | Hybrid capital security outstanding balance |
| `contingent_capital_outstanding` | Contingent capital security outstanding balance |
| `public_offering_fund_usage` | Use of public-offering proceeds |
| `private_placement_fund_usage` | Use of private-placement proceeds |
| `audit_opinion` | External auditor name and audit opinion |
| `audit_service_contracts` | Audit service contracts |
| `non_audit_service_contracts` | Non-audit service contracts with the auditor |
| `outside_directors` | Outside (independent) directors and changes |
| `largest_shareholders` | Largest shareholder |
| `largest_shareholder_changes` | Largest shareholder changes |
| `minority_shareholders` | Minority shareholders |
| `executives` | Officers / executives |
| `employees` | Employees |
| `unregistered_executive_pay` | Unregistered-executive compensation |
| `director_pay_approved` | Director & auditor pay (AGM-approved amount) |
| `director_pay_total` | Director & auditor pay (total paid) |
| `director_pay_by_type` | Director & auditor pay (by type) |
| `individual_pay` | Individual director/auditor pay (>= 500M KRW) |
| `individual_pay_v2` | Individual pay (>= 500M KRW) Ver2.0 — filings after 2026-05, grouped |
| `top5_individual_pay` | Top-5 individual pay (>= 500M KRW) |
| `top5_individual_pay_v2` | Top-5 individual pay Ver2.0 — filings after 2026-05, grouped |
| `equity_investments` | Investments in other corporations |

### finance

| Method | Description |
|---|---|
| `single_accounts(corp_code, *, fiscal_year, report_code)` | Key accounts, one company |
| `multi_accounts(corp_codes, *, fiscal_year, report_code)` | Key accounts, several companies |
| `full_statements(corp_code, *, fiscal_year, statement_div, report_code)` | Full statements (every BS/IS/CIS/CF line) |
| `single_indicators(corp_code, *, fiscal_year, index_class, report_code)` | Key financial ratios, one company |
| `multi_indicators(corp_codes, *, fiscal_year, index_class, report_code)` | Key financial ratios, several companies |
| `xbrl_document(rcept_no, *, report_code)` | Raw XBRL zip for one filing (`bytes`) |
| `xbrl_taxonomy(*, statement_kind)` | Standard XBRL account taxonomy |

### ownership

| Method | Description |
|---|---|
| `insider_holdings(corp_code)` | Insider (officer / major-shareholder) ownership filings |
| `five_percent_holdings(corp_code)` | 5%-rule large-holding filings |

### event (major-event reports)

All take `(corp_code, *, begin_date, end_date)`.

| Method | Description |
|---|---|
| `default_occurrence` | Default (부도) occurrence |
| `business_suspension` | Business suspension |
| `rehabilitation_filing` | Rehabilitation-procedure filing |
| `dissolution_cause` | Dissolution cause occurrence |
| `paid_in_capital_increase` | Paid-in capital increase decision |
| `bonus_issue` | Bonus issue (free capital increase) decision |
| `combined_capital_increase` | Combined paid-in / bonus increase decision |
| `capital_reduction` | Capital reduction decision |
| `creditor_management_start` | Creditor-bank management-procedure start |
| `creditor_management_stop` | Creditor-bank management-procedure stop |
| `litigation` | Litigation filed |
| `overseas_listing_decision` | Overseas listing decision |
| `overseas_delisting_decision` | Overseas delisting decision |
| `overseas_listing` | Overseas listing |
| `overseas_delisting` | Overseas delisting |
| `convertible_bond` | Convertible bond (CB) issuance decision |
| `bond_with_warrant` | Bond with warrant (BW) issuance decision |
| `exchangeable_bond` | Exchangeable bond (EB) issuance decision |
| `contingent_convertible_bond` | Write-down contingent capital security issuance decision |
| `treasury_acquisition` | Treasury stock acquisition decision |
| `treasury_disposal` | Treasury stock disposal decision |
| `treasury_trust_contract` | Treasury-stock trust-contract decision |
| `treasury_trust_termination` | Treasury-stock trust-termination decision |
| `asset_transaction` | Asset transfer (other) / put-back option |
| `business_acquisition` | Business acquisition decision |
| `business_transfer` | Business transfer decision |
| `tangible_asset_acquisition` | Tangible asset acquisition decision |
| `tangible_asset_transfer` | Tangible asset transfer decision |
| `equity_stake_acquisition` | Acquisition of another company's shares / equity |
| `equity_stake_transfer` | Transfer of another company's shares / equity |
| `equity_bond_acquisition` | Acquisition of share-related bonds |
| `equity_bond_transfer` | Transfer of share-related bonds |
| `merger` | Company merger decision |
| `spinoff` | Company split (spin-off) decision |
| `split_merger` | Split-merger decision |
| `stock_exchange` | Stock exchange / transfer decision |

### registration (securities-registration statements)

All take `(corp_code, *, begin_date, end_date)`.

| Method | Description |
|---|---|
| `equity_securities` | Equity securities |
| `debt_securities` | Debt securities |
| `depositary_receipts` | Depositary receipts |
| `merger` | Merger |
| `stock_exchange` | Comprehensive stock exchange / transfer |
| `division` | Division |

## License

MIT © Seokhoon Joo
