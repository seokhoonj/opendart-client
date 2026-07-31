"""Command-line access to company, disclosure, and finance data."""

from __future__ import annotations

import argparse
import datetime
import json
import sys
import unicodedata
from collections.abc import Callable
from typing import Any

from .client import OpenDart
from .errors import DartError

Row = dict[str, Any]
_KEY_ACCOUNTS = ("매출액", "영업이익", "당기순이익", "자산총계", "부채총계", "자본총계")
_REPORT_NAMES = {
    "11011": "사업보고서",
    "11012": "반기보고서",
    "11013": "1분기보고서",
    "11014": "3분기보고서",
}
_COMPANY_FIELDS = (
    "corp_name",
    "corp_cls",
    "ceo_nm",
    "stock_code",
    "est_dt",
    "adres",
    "induty_code",
    "hm_url",
)


def _resolve(dart: OpenDart, company: str) -> str:
    if len(company) == 8 and company.isdigit():
        return company
    return dart.resolver().resolve(company)


def _company_name(dart: OpenDart, corp_code: str) -> str:
    """The corp_name for a corp_code, from the in-memory resolver (search short-circuits
    on an exact corp_code). Empty string if the code is unknown."""
    rows = dart.resolver().search(corp_code)
    return str(rows[0].get("corp_name", "")) if rows else ""


def _dump_json(value: object) -> None:
    print(json.dumps(value, ensure_ascii=False, indent=2))


def _run_resolve(dart: OpenDart, args: argparse.Namespace) -> int:
    rows = dart.resolver().search(args.query)
    if not rows:
        print(f"no company matches {args.query!r}", file=sys.stderr)
        return 1
    if args.json:
        _dump_json(rows)
        return 0
    for row in rows:
        ticker = row["stock_code"] or "------"
        print(f"{row['corp_code']:<8}  {ticker:<6}  {row['corp_name']}")
    return 0


def _run_search(dart: OpenDart, args: argparse.Namespace) -> int:
    corp_code = _resolve(dart, args.company)
    rows = dart.disclosure.search(
        corp_code=corp_code,
        begin_date=args.begin,
        end_date=args.end,
        max_pages=None if args.all else 1,
    )
    if args.json:
        _dump_json(rows)
        return 0
    shown = rows[: max(0, args.limit)]   # a negative --limit must not slice from the end
    print(f"{corp_code}  {len(rows)} filings")
    for row in shown:
        report = str(row.get("report_nm", "")).strip()
        print(f"{row.get('rcept_dt', '')}  {row.get('rcept_no', '')}  {report}")
    return 0


def _run_company(dart: OpenDart, args: argparse.Namespace) -> int:
    corp_code = _resolve(dart, args.company)
    company = dart.disclosure.company(corp_code)
    if args.json:
        _dump_json(company)
        return 0
    for field_name in _COMPANY_FIELDS:
        field_value = company.get(field_name)
        if field_value:
            print(f"{field_name:<12} {field_value}")
    return 0


def _format_amount(value: object) -> str:
    raw = str(value)
    try:
        return f"{int(raw.replace(',', '')):,}"
    except ValueError:
        return raw


def _display_width(text: str) -> int:
    """Terminal cell width: East-Asian Wide/Fullwidth glyphs (Hangul, ...) take two
    cells, so padding by ``len`` misaligns a column of mixed Korean labels."""
    return sum(2 if unicodedata.east_asian_width(c) in ("W", "F") else 1 for c in text)


def _pad(text: str, width: int) -> str:
    """Left-justify ``text`` to ``width`` terminal cells (wide glyphs counted as two)."""
    return text + " " * max(0, width - _display_width(text))


def _canonical_account(name: str) -> str:
    """Normalize a DART account label for key-account matching. DART writes 당기순이익 as
    '당기순이익(손실)' and uses an inner space in '법인세차감전 순이익', so an exact-string
    match would silently drop those; strip the parenthetical qualifier and spaces."""
    return name.split("(")[0].replace(" ", "").strip()


def _run_finance(dart: OpenDart, args: argparse.Namespace) -> int:
    corp_code = _resolve(dart, args.company)
    rows = dart.finance.single_accounts(
        corp_code,
        fiscal_year=args.year,
        report_code=args.report,
    )
    if not rows:
        print("no data", file=sys.stderr)
        return 1
    if args.json:
        _dump_json(rows)
        return 0
    statement_div = "OFS" if args.separate else "CFS"
    row_by_account: dict[str, Row] = {}
    for row in rows:
        if row.get("fs_div") != statement_div:
            continue
        account_name = _canonical_account(str(row.get("account_nm", "")))
        if account_name in _KEY_ACCOUNTS and account_name not in row_by_account:
            row_by_account[account_name] = row   # DART repeats some lines; keep the first
    if not row_by_account:   # the requested statement (CFS/OFS) has no key accounts
        print(f"no {statement_div} data", file=sys.stderr)
        return 1
    label = "OFS 별도" if args.separate else "CFS 연결"
    company_name = _company_name(dart, corp_code)
    who = f"{company_name} ({corp_code})" if company_name else corp_code
    report_name = _REPORT_NAMES.get(args.report, args.report)
    print(f"{who}  {args.year} {report_name}  ({label})")
    lines = [
        (account_name, _format_amount(row_by_account[account_name].get("thstrm_amount", "")))
        for account_name in _KEY_ACCOUNTS
        if account_name in row_by_account
    ]
    amount_w = max((len(amount) for _, amount in lines), default=0)
    for account_name, amount in lines:
        print(f"{_pad(account_name, 12)} {amount:>{amount_w}}")
    return 0


def _default_year() -> int:
    """Most recent fiscal year likely to have a filed annual report: last year, except in
    Q1 (before annual reports are filed) fall back one more year."""
    today = datetime.date.today()
    return today.year - (2 if today.month < 4 else 1)


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="opendart")
    parser.add_argument("--api-key")
    parser.add_argument("--timeout", type=float, default=30.0)
    subparsers = parser.add_subparsers()

    resolve = subparsers.add_parser("resolve")
    resolve.add_argument("query")
    resolve.add_argument("--json", action="store_true")
    resolve.set_defaults(handler=_run_resolve)

    search = subparsers.add_parser("search")
    search.add_argument("company")
    search.add_argument("--begin")
    search.add_argument("--end")
    search.add_argument("--limit", type=int, default=20)
    search.add_argument("--all", action="store_true")
    search.add_argument("--json", action="store_true")
    search.set_defaults(handler=_run_search)

    company = subparsers.add_parser("company")
    company.add_argument("company")
    company.add_argument("--json", action="store_true")
    company.set_defaults(handler=_run_company)

    finance = subparsers.add_parser("finance")
    finance.add_argument("company")
    finance.add_argument("--year", type=int, default=_default_year())
    finance.add_argument("--report", choices=tuple(_REPORT_NAMES), default="11011")
    finance.add_argument("--separate", action="store_true")
    finance.add_argument("--json", action="store_true")
    finance.set_defaults(handler=_run_finance)
    return parser


def main(argv: list[str] | None = None) -> int:
    """Run the CLI on ``argv`` (or ``sys.argv`` when None); return the process exit code."""
    parser = _parser()
    args = parser.parse_args(argv)
    handler: Callable[[OpenDart, argparse.Namespace], int] | None = getattr(
        args, "handler", None
    )
    if handler is None:   # no subcommand given
        parser.print_help()
        return 2
    try:
        dart = OpenDart(api_key=args.api_key, timeout=args.timeout)
        return handler(dart, args)
    except (ValueError, DartError) as err:
        print(f"error: {err}", file=sys.stderr)
        return 1
