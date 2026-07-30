---
name: company
description: "Show a Korean company's OpenDART profile -- name, CEO, address, industry, listing class, and more. Holds no logic of its own -- it calls the opendart-client package's CLI (`opendart company`) and shows the result to the user. Trigger phrases: 기업개황, 회사 정보, company profile, 대표이사 누구, 회사 프로필, 어디 회사야."
---

# opendart — company profile

Take a company handle and print its OpenDART profile (기업개황): name, listing class,
CEO, address, industry code, homepage, and the like. The fetching lives in the
opendart-client package (on PyPI); this skill is a thin wrapper that calls its CLI.

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
opendart company "<COMPANY>" [--json]
```

`<COMPANY>` is a name, ticker, initials, typo, or 8-digit `corp_code` (resolved to a
corp_code internally). `--json` returns the full profile dict instead of the labeled
text summary.

The text output is a handful of labeled lines (corp_name, corp_cls, ceo_nm, stock_code,
est_dt, adres, induty_code, hm_url) -- only the fields the company actually has.

## Procedure

1. **Get the company.** Find a handle in the user's message. If there is none, ask.
2. **Run.** Add `--json` when the user wants every field.
   ```bash
   opendart company "삼성전자"
   ```
3. **Relay the result.** Show the CLI's stdout.
4. **Error handling.** When the CLI exits non-zero, relay the one-line `error: <message>`
   from stderr as-is. Common ones:
   - `command not found: opendart` -> not installed; point the user at
     `pipx install opendart-client`.
   - `OpenDART API key required: ...` -> no key; point the user at the config file above.
   - `no company matches '...'` -> the handle did not resolve; ask for a clearer one.

## What this skill does not do

- It does not re-implement the fetch (the package does); it always calls the CLI.
- It shows the profile only -- for filings use `search`, for financials use `finance`.
