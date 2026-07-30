---
name: search
description: "List a Korean company's OpenDART disclosures (filings) in a date window. Holds no logic of its own -- it calls the opendart-client package's CLI (`opendart search`) and shows the result to the user. Trigger phrases: 공시 보여줘, 공시 목록, disclosures, 최근 공시, 전자공시 검색, filings for, 무슨 공시 냈어."
---

# opendart — search a company's disclosures

Take a company handle and print its OpenDART disclosures (which filing, filed when) in a
date window. The fetching lives in the opendart-client package (on PyPI); this skill is a
thin wrapper that calls its CLI and relays the result.

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
opendart search "<COMPANY>" [options]
```

`<COMPANY>` is a name, ticker, initials, typo, or 8-digit `corp_code` (resolved to a
corp_code internally). Options (`opendart search --help` is the source of truth):
- `--begin YYYYMMDD` — start of the filing-date window.
- `--end YYYYMMDD` — end of the window.
- `--limit N` — how many rows to show in the text summary (default 20).
- `--all` — fetch every page, not just the first.
- `--json` — the full list as JSON instead of the text summary.

The text output is a header (`corp_code  N filings`) then one line per filing
(`rcept_dt  rcept_no  report_nm`).

## Procedure

1. **Get the company.** Find a handle in the user's message. If there is none, ask.
2. **Run.** Add `--begin`/`--end` only when the user asked for a specific window; add
   `--json` when they want the full list.
   ```bash
   opendart search "삼성전자" --begin 20260101 --end 20260131
   ```
3. **Relay the result.** Show the CLI's stdout. You may trim a long list, but keep the
   header line.
4. **Error handling.** When the CLI exits non-zero, relay the one-line `error: <message>`
   from stderr as-is. Common ones:
   - `command not found: opendart` -> not installed; point the user at
     `pipx install opendart-client`.
   - `OpenDART API key required: ...` -> no key; point the user at the config file above.
   - `no company matches '...'` -> the handle did not resolve; ask for a clearer one.
   - a rate-limit message -> OpenDART is throttling; wait and retry.

## What this skill does not do

- It does not re-implement the search or pagination (the package does); it calls the CLI.
- It lists filings only -- for the profile use `company`, for financials use `finance`.
