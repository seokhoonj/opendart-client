"""Command-line access to company, disclosure, and finance data."""

from __future__ import annotations

import argparse
import datetime
import json
import sys
from typing import Any

from .client import OpenDart
from .errors import DartError

Row = dict[str, Any]
_KEY_ACCOUNTS = ("매출액", "영업이익", "당기순이익", "자산총계", "부채총계", "자본총계")
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
    shown = rows[: args.limit]
    print(f"{corp_code}  {len(rows)} filings")
    for row in shown:
        print(
            f"{row.get('rcept_dt', '')}  {row.get('rcept_no', '')}  "
            f"{row.get('report_nm', '')}"
        )
    return 0


def _run_company(dart: OpenDart, args: argparse.Namespace) -> int:
    corp_code = _resolve(dart, args.company)
    company = dart.disclosure.company(corp_code)
    if args.json:
        _dump_json(company)
        return 0
    for label in _COMPANY_FIELDS:
        value = company.get(label)
        if value:
            print(f"{label:<12} {value}")
    return 0


def _format_amount(value: object) -> str:
    raw = str(value)
    try:
        return f"{int(raw.replace(',', '')):,}"
    except ValueError:
        return raw


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
    label = "OFS 별도" if args.separate else "CFS 연결"
    print(f"{corp_code}  {args.year} report {args.report}  ({label})")
    by_name = {
        row.get("account_nm"): row
        for row in rows
        if row.get("fs_div") == statement_div
    }
    for account_name in _KEY_ACCOUNTS:
        row = by_name.get(account_name)
        if row is not None:
            print(f"{account_name:<10} {_format_amount(row.get('thstrm_amount', ''))}")
    return 0


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="opendart")
    parser.add_argument("--api-key")
    parser.add_argument("--timeout", type=float, default=30.0)
    subparsers = parser.add_subparsers(dest="command")

    resolve = subparsers.add_parser("resolve")
    resolve.add_argument("query")
    resolve.add_argument("--json", action="store_true")

    search = subparsers.add_parser("search")
    search.add_argument("company")
    search.add_argument("--begin")
    search.add_argument("--end")
    search.add_argument("--limit", type=int, default=20)
    search.add_argument("--all", action="store_true")
    search.add_argument("--json", action="store_true")

    company = subparsers.add_parser("company")
    company.add_argument("company")
    company.add_argument("--json", action="store_true")

    finance = subparsers.add_parser("finance")
    finance.add_argument("company")
    finance.add_argument("--year", type=int, default=datetime.date.today().year - 1)
    finance.add_argument("--report", default="11011")
    finance.add_argument("--separate", action="store_true")
    finance.add_argument("--json", action="store_true")
    return parser


def _dispatch(dart: OpenDart, args: argparse.Namespace) -> int:
    if args.command == "resolve":
        return _run_resolve(dart, args)
    if args.command == "search":
        return _run_search(dart, args)
    if args.command == "company":
        return _run_company(dart, args)
    if args.command == "finance":
        return _run_finance(dart, args)
    raise ValueError(f"unknown command: {args.command}")


def main(argv: list[str] | None = None) -> int:
    """Run the OpenDART command-line client."""
    parser = _parser()
    args = parser.parse_args(argv)
    if args.command is None:
        parser.print_help()
        return 2
    try:
        dart = OpenDart(api_key=args.api_key, timeout=args.timeout)
        return _dispatch(dart, args)
    except (ValueError, DartError) as err:
        print(f"error: {err}", file=sys.stderr)
        return 1
