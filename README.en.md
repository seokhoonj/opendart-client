# opendart-client

[![check](https://github.com/seokhoonj/opendart-client/actions/workflows/check.yml/badge.svg)](https://github.com/seokhoonj/opendart-client/actions/workflows/check.yml)
[![PyPI](https://img.shields.io/pypi/v/opendart-client)](https://pypi.org/project/opendart-client/)
[![Python](https://img.shields.io/pypi/pyversions/opendart-client)](https://pypi.org/project/opendart-client/)
[![License](https://img.shields.io/pypi/l/opendart-client)](https://github.com/seokhoonj/opendart-client/blob/main/LICENSE)

**English** | [한국어](https://github.com/seokhoonj/opendart-client/blob/main/README.md)

Read disclosure data from Korea's **OpenDART** (the Financial Supervisory Service's
electronic disclosure system).

Company profiles and filing lists, financial statements and key ratios, dividends and
capital changes, largest / minority shareholders, officers, employees and their pay,
major decisions like mergers, spin-offs, business transfers and treasury-stock buybacks,
ownership filings (the 5% rule), and securities-registration statements.

## 1. Install

```bash
pip install opendart-client
```

Get a free API key (40 chars) at <https://opendart.fss.or.kr>. The key is read from
`OpenDart(api_key=...)`, the `OPENDART_API_KEY` environment variable, then a config
file — in that order.

**Config file (all platforms, recommended)** — create
`~/.config/opendart-client/credentials.json` with:

```json
{ "api_key": "..." }
```

**Environment variable** — shell-specific. macOS/Linux (bash/zsh):

```sh
export OPENDART_API_KEY=...
```

On Windows PowerShell use `setx OPENDART_API_KEY "..."` (persistent) or
`$env:OPENDART_API_KEY = "..."` (current session).

## 2. Quickstart

```python
from opendart_client import OpenDart

dart = OpenDart(api_key="...")          # or set OPENDART_API_KEY in the environment

# resolve a name / ticker / initials / typo -> corp_code
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
```

A `corp_code` resolves from a full name, ticker, initial consonants (`ㅅㅅㅈㅈ`), or a
typo (`dart.resolver().resolve(...)`). A query with no matching data comes back empty.

Returns are `list[dict]`, so pandas / polars build a DataFrame directly.

```python
import pandas as pd
import polars as pl

pd.DataFrame(rows)   # or pl.DataFrame(rows)
```

## 3. API

**Top-level helpers** — find a company, or list them all.

| Call | What it returns |
|---|---|
| `dart.corp_codes()` | Every company's corp_code ↔ name / ticker |
| `dart.resolver().resolve(query)` | One corp_code from a name, ticker, initials, or typo |
| `dart.resolver().search(query)` | Candidate matches for the same query |

**`report_code`** — the period shared by the periodic-report and finance methods
(defaults to `11011`).

| Code | Report |
|---|---|
| `11011` | Annual report (default) |
| `11012` | Half-year |
| `11013` | Q1 |
| `11014` | Q3 |

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

## 4. Terminal

Installing puts an `opendart` command on your PATH (also `python -m opendart_client`).
The key is read from `--api-key`, the environment, or the config file.

```sh
opendart resolve 삼성전자                    # name / ticker / initials / typo -> corp_code (+ candidates)
opendart search  삼성전자 --begin 20260101   # filings in a date window
opendart company 삼성전자                    # company profile
opendart finance 삼성전자 --year 2024        # key accounts (revenue, operating & net income, assets/liabilities/equity)
```

Main options:

| Option | Commands | What it does |
|---|---|---|
| `--api-key KEY` | all | pass the key directly (else the env var / config file) |
| `--timeout SEC` | all | per-request timeout in seconds, default `30` |
| `--json` | all | print the full result as JSON instead of the readable summary |
| `--begin YYYYMMDD` / `--end YYYYMMDD` | `search` | filing-date window |
| `--limit N` | `search` | rows to show, default `20` |
| `--all` | `search` | fetch every page, not just the first |
| `--year N` | `finance` | fiscal year, default the most recently filed year |
| `--report CODE` | `finance` | `11011` annual · `11012` half-year · `11013` Q1 · `11014` Q3 (default `11011`) |
| `--separate` | `finance` | separate statements (OFS), default consolidated (CFS) |

The `<company>` argument takes a name, ticker, initials, typo, or an 8-digit corp_code
— it resolves to a corp_code internally. Each command prints a readable summary by
default; `--json` prints the full result. See `--help` for the rest.

`resolve` lists corp_code, ticker, then name; an unlisted company shows `------` for
the ticker.

```
$ opendart resolve 삼성전자
00126380  005930  삼성전자
00252074  ------  삼성전자판매
00366997  ------  삼성전자로지텍
```

`finance` heads the key accounts with the company and report name (`--separate` for the
separate statements).

```
$ opendart finance 삼성전자 --year 2024
삼성전자 (00126380)  2024 사업보고서  (CFS 연결)
매출액       300,870,903,000,000
영업이익      32,725,961,000,000
당기순이익    34,451,351,000,000
자산총계     514,531,948,000,000
부채총계     112,339,878,000,000
자본총계     402,192,070,000,000
```

## 5. AI coding agents

This repo doubles as a plugin marketplace for Claude Code and Codex — it ships
`resolve`, `search`, `company`, and `finance` as skills that call the `opendart`
command. Install the package and set an API key first (above).

### 5.1. Claude Code

```
/plugin marketplace add seokhoonj/opendart-client
/plugin install opendart@opendart-client
```

Then just ask ("find Samsung Electronics' corp_code", "show 삼성전자's recent filings"),
or call a skill directly — `/opendart:resolve 삼성전자`, `/opendart:finance 삼성전자 --year 2024`.

### 5.2. Codex

```
codex plugin marketplace add seokhoonj/opendart-client
codex plugin add opendart@opendart-client
```

The `resolve`, `search`, `company`, and `finance` skills react to a company name or
ticker, and you can always run `opendart <command> <company>` directly.

Prefer not to install the plugin? Symlink a skill into your skills directory and call it
without the `opendart:` prefix, as `/resolve`:

```sh
ln -s "$PWD/plugins/opendart/skills/resolve" ~/.claude/skills/resolve
```

## 6. License

MIT © Seokhoon Joo
