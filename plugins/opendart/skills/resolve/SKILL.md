---
name: resolve
description: "Resolve a Korean company name, ticker, initials (초성), or a typo to its OpenDART corp_code. Holds no logic of its own -- it calls the opendart-client package's CLI (`opendart resolve`) and shows the result to the user. Trigger phrases: 회사코드 찾아줘, corp_code, 회사 코드, resolve company, 삼성전자 코드, 종목코드로 회사, 초성으로 회사 찾기."
---

# opendart — resolve a company to its corp_code

Take a company handle (name, ticker, initials, or a typo) and print the matching
OpenDART `corp_code`s. Most OpenDART lookups are keyed by an 8-digit `corp_code` nobody
remembers; this turns a human handle into it. The matching lives in the opendart-client
package (on PyPI); this skill is a thin wrapper that calls its CLI and relays the result.

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
opendart resolve "<QUERY>" [--json]
```

`<QUERY>` can be a name (`삼성전자`), a 6-digit ticker (`005930`), the initials
(`ㅅㅅㅈㅈ`), a typo (`삼서전자`), or an 8-digit `corp_code` (passed through). `--json`
returns the full candidate rows instead of the text list.

The text output is one line per candidate, `corp_code  ticker  name`, best match first
(listed companies before unlisted, then shorter names). An unlisted company shows
`------` for the ticker.

## Procedure

1. **Get the query.** Find a company handle in the user's message. If there is none, ask.
2. **Run.** Call the CLI; add `--json` when the user wants machine-readable rows.
   ```bash
   opendart resolve "삼성전자"
   ```
3. **Relay the result.** Show the CLI's stdout. When several candidates come back, the
   first line is the best match; mention that the others are alternatives.
4. **Error handling.** When the CLI exits non-zero, relay the one-line `error: <message>`
   from stderr as-is. Common ones:
   - `command not found: opendart` -> the package is not installed; point the user at
     `pipx install opendart-client`.
   - `OpenDART API key required: ...` -> no key found; point the user at the config file
     above (or the `OPENDART_API_KEY` env var).
   - `no company matches '...'` -> nothing resolved; ask for a clearer name or ticker.

## What this skill does not do

- It does not re-implement the resolver (the package does); it always calls the CLI.
- It only finds the corp_code -- for filings use `search`, for the profile use `company`,
  for financials use `finance`.
