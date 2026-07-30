---
name: finance
description: "Summarize a Korean company's key financial accounts (revenue, operating and net income, total assets/liabilities/equity) from OpenDART. Holds no logic of its own -- it calls the opendart-client package's CLI (`opendart finance`) and shows the result to the user. Trigger phrases: 재무 요약, 재무제표, 주요계정, financials, 매출 영업이익, 재무 보여줘, 실적 어때."
---

# opendart — key financial accounts

Take a company handle and print its OpenDART key accounts (주요계정) for a fiscal year:
revenue, operating income, net income, and total assets/liabilities/equity. The fetching
lives in the opendart-client package (on PyPI); this skill is a thin wrapper that calls
its CLI.

## Prerequisite

This plugin calls the `opendart` CLI, so install the package first:

```
pipx install opendart-client        # or: pip install opendart-client
```

That puts the `opendart` command on PATH (also `python -m opendart_client`).

It also needs a free OpenDART API key (get one at <https://opendart.fss.or.kr>). The
simplest cross-platform way to supply it is a config file -- create
`~/.config/opendart-client/credentials.json` with:

```json
{ "api_key": "..." }
```

(Alternatively set the `OPENDART_API_KEY` environment variable, or pass `--api-key`.)

## Running

```
opendart finance "<COMPANY>" [options]
```

`<COMPANY>` is a name, ticker, initials, typo, or 8-digit `corp_code` (resolved to a
corp_code internally). Options (`opendart finance --help` is the source of truth):
- `--year N` — fiscal year (default: last calendar year).
- `--report CODE` — report period: `11011` annual (default), `11012` half-year,
  `11013` Q1, `11014` Q3.
- `--separate` — separate statements (OFS 별도) instead of consolidated (CFS 연결).
- `--json` — the full account rows as JSON instead of the summary.

The text output is a header (`name (corp_code)  year report  (CFS/OFS)`) then the key
accounts with their amounts.

## Procedure

1. **Get the company.** Find a handle in the user's message. If there is none, ask.
2. **Run.** Add `--year`/`--report` when the user named a specific period; add
   `--separate` for the separate (별도) statements; add `--json` for every line item.
   ```bash
   opendart finance "삼성전자" --year 2024
   ```
3. **Relay the result.** Show the CLI's stdout. Amounts are in KRW (원).
4. **Error handling.** When the CLI exits non-zero, relay the one-line `error: <message>`
   from stderr as-is. Common ones:
   - `command not found: opendart` -> not installed; point the user at
     `pipx install opendart-client`.
   - `OpenDART API key required: ...` -> no key; point the user at the config file above.
   - `no company matches '...'` -> the handle did not resolve; ask for a clearer one.
   - `no data` -> OpenDART has no key accounts for that company/year/report (e.g. the
     annual report is not filed yet); suggest a different `--year` or `--report`.

## What this skill does not do

- It does not re-implement the fetch (the package does); it always calls the CLI.
- It summarizes the key accounts only -- for the full statements or ratios, use the
  package's `finance.full_statements` / `finance.single_indicators` from Python.
