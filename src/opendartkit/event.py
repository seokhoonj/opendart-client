"""주요사항보고서 (DS005) -- ad-hoc corporate-event decisions.

The event feed for a disclosure->price study: each method is one kind of decision
(유상증자, 전환사채 발행, 자기주식 취득, 합병, ...) filed in a date window. Every
endpoint shares the same shape -- ``corp_code`` + a receipt-date range -- so they all
route through ``_event``. Data is available from 2015 onward.
"""

from __future__ import annotations

from typing import Any

from ._endpoint import DartEndpoint
from .session import DartSession

Rows = list[dict[str, Any]]

_R = ("corp_code", "bgn_de", "end_de")


def _ep(operation: str, api_id: str) -> DartEndpoint:
    return DartEndpoint(operation, "DS005", api_id, required=_R)


DEFAULT_OCCURRENCE = _ep("dfOcr", "2020019")
BUSINESS_SUSPENSION = _ep("bsnSp", "2020020")
REHABILITATION_FILING = _ep("ctrcvsBgrq", "2020021")
DISSOLUTION_CAUSE = _ep("dsRsOcr", "2020022")
PAID_IN_CAPITAL_INCREASE = _ep("piicDecsn", "2020023")
BONUS_ISSUE = _ep("fricDecsn", "2020024")
COMBINED_CAPITAL_INCREASE = _ep("pifricDecsn", "2020025")
CAPITAL_REDUCTION = _ep("crDecsn", "2020026")
CREDITOR_MANAGEMENT_START = _ep("bnkMngtPcbg", "2020027")
CREDITOR_MANAGEMENT_STOP = _ep("bnkMngtPcsp", "2020036")
LITIGATION = _ep("lwstLg", "2020028")
OVERSEAS_LISTING_DECISION = _ep("ovLstDecsn", "2020029")
OVERSEAS_DELISTING_DECISION = _ep("ovDlstDecsn", "2020030")
OVERSEAS_LISTING = _ep("ovLst", "2020031")
OVERSEAS_DELISTING = _ep("ovDlst", "2020032")
CONVERTIBLE_BOND = _ep("cvbdIsDecsn", "2020033")
BOND_WITH_WARRANT = _ep("bdwtIsDecsn", "2020034")
EXCHANGEABLE_BOND = _ep("exbdIsDecsn", "2020035")
CONTINGENT_CONVERTIBLE_BOND = _ep("wdCocobdIsDecsn", "2020037")
TREASURY_ACQUISITION = _ep("tsstkAqDecsn", "2020038")
TREASURY_DISPOSAL = _ep("tsstkDpDecsn", "2020039")
TREASURY_TRUST_CONTRACT = _ep("tsstkAqTrctrCnsDecsn", "2020040")
TREASURY_TRUST_TERMINATION = _ep("tsstkAqTrctrCcDecsn", "2020041")
ASSET_TRANSFER = _ep("astInhtrfEtcPtbkOpt", "2020018")
BUSINESS_ACQUISITION = _ep("bsnInhDecsn", "2020042")
BUSINESS_TRANSFER = _ep("bsnTrfDecsn", "2020043")
TANGIBLE_ASSET_ACQUISITION = _ep("tgastInhDecsn", "2020044")
TANGIBLE_ASSET_TRANSFER = _ep("tgastTrfDecsn", "2020045")
EQUITY_STAKE_ACQUISITION = _ep("otcprStkInvscrInhDecsn", "2020046")
EQUITY_STAKE_TRANSFER = _ep("otcprStkInvscrTrfDecsn", "2020047")
EQUITY_BOND_ACQUISITION = _ep("stkrtbdInhDecsn", "2020048")
EQUITY_BOND_TRANSFER = _ep("stkrtbdTrfDecsn", "2020049")
MERGER = _ep("cmpMgDecsn", "2020050")
SPINOFF = _ep("cmpDvDecsn", "2020051")
SPLIT_MERGER = _ep("cmpDvmgDecsn", "2020052")
STOCK_EXCHANGE = _ep("stkExtrDecsn", "2020053")


class Event:
    """주요사항보고서 (DS005). Reach it as ``DartClient.event``.

    Every method takes ``corp_code`` and a ``begin_date`` / ``end_date`` (YYYYMMDD)
    receipt-date window, and returns the matching decisions as ``list[dict]``.
    """

    def __init__(self, session: DartSession) -> None:
        self._session = session

    def _event(
        self, endpoint: DartEndpoint, corp_code: str, begin_date: str, end_date: str
    ) -> Rows:
        return self._session.fetch_list(
            endpoint, corp_code=corp_code, bgn_de=begin_date, end_de=end_date
        )

    def default_occurrence(
        self, *, corp_code: str, begin_date: str, end_date: str
    ) -> Rows:
        """부도발생 (2020019)."""
        return self._event(DEFAULT_OCCURRENCE, corp_code, begin_date, end_date)

    def business_suspension(
        self, *, corp_code: str, begin_date: str, end_date: str
    ) -> Rows:
        """영업정지 (2020020)."""
        return self._event(BUSINESS_SUSPENSION, corp_code, begin_date, end_date)

    def rehabilitation_filing(
        self, *, corp_code: str, begin_date: str, end_date: str
    ) -> Rows:
        """회생절차 개시신청 (2020021)."""
        return self._event(REHABILITATION_FILING, corp_code, begin_date, end_date)

    def dissolution_cause(
        self, *, corp_code: str, begin_date: str, end_date: str
    ) -> Rows:
        """해산사유 발생 (2020022)."""
        return self._event(DISSOLUTION_CAUSE, corp_code, begin_date, end_date)

    def paid_in_capital_increase(
        self, *, corp_code: str, begin_date: str, end_date: str
    ) -> Rows:
        """유상증자 결정 (2020023)."""
        return self._event(PAID_IN_CAPITAL_INCREASE, corp_code, begin_date, end_date)

    def bonus_issue(
        self, *, corp_code: str, begin_date: str, end_date: str
    ) -> Rows:
        """무상증자 결정 (2020024)."""
        return self._event(BONUS_ISSUE, corp_code, begin_date, end_date)

    def combined_capital_increase(
        self, *, corp_code: str, begin_date: str, end_date: str
    ) -> Rows:
        """유무상증자 결정 (2020025)."""
        return self._event(COMBINED_CAPITAL_INCREASE, corp_code, begin_date, end_date)

    def capital_reduction(
        self, *, corp_code: str, begin_date: str, end_date: str
    ) -> Rows:
        """감자 결정 (2020026)."""
        return self._event(CAPITAL_REDUCTION, corp_code, begin_date, end_date)

    def creditor_management_start(
        self, *, corp_code: str, begin_date: str, end_date: str
    ) -> Rows:
        """채권은행 등의 관리절차 개시 (2020027)."""
        return self._event(CREDITOR_MANAGEMENT_START, corp_code, begin_date, end_date)

    def creditor_management_stop(
        self, *, corp_code: str, begin_date: str, end_date: str
    ) -> Rows:
        """채권은행 등의 관리절차 중단 (2020036)."""
        return self._event(CREDITOR_MANAGEMENT_STOP, corp_code, begin_date, end_date)

    def litigation(
        self, *, corp_code: str, begin_date: str, end_date: str
    ) -> Rows:
        """소송 등의 제기 (2020028)."""
        return self._event(LITIGATION, corp_code, begin_date, end_date)

    def overseas_listing_decision(
        self, *, corp_code: str, begin_date: str, end_date: str
    ) -> Rows:
        """해외 증권시장 주권등 상장 결정 (2020029)."""
        return self._event(OVERSEAS_LISTING_DECISION, corp_code, begin_date, end_date)

    def overseas_delisting_decision(
        self, *, corp_code: str, begin_date: str, end_date: str
    ) -> Rows:
        """해외 증권시장 주권등 상장폐지 결정 (2020030)."""
        return self._event(OVERSEAS_DELISTING_DECISION, corp_code, begin_date, end_date)

    def overseas_listing(
        self, *, corp_code: str, begin_date: str, end_date: str
    ) -> Rows:
        """해외 증권시장 주권등 상장 (2020031)."""
        return self._event(OVERSEAS_LISTING, corp_code, begin_date, end_date)

    def overseas_delisting(
        self, *, corp_code: str, begin_date: str, end_date: str
    ) -> Rows:
        """해외 증권시장 주권등 상장폐지 (2020032)."""
        return self._event(OVERSEAS_DELISTING, corp_code, begin_date, end_date)

    def convertible_bond(
        self, *, corp_code: str, begin_date: str, end_date: str
    ) -> Rows:
        """전환사채권(CB) 발행결정 (2020033)."""
        return self._event(CONVERTIBLE_BOND, corp_code, begin_date, end_date)

    def bond_with_warrant(
        self, *, corp_code: str, begin_date: str, end_date: str
    ) -> Rows:
        """신주인수권부사채권(BW) 발행결정 (2020034)."""
        return self._event(BOND_WITH_WARRANT, corp_code, begin_date, end_date)

    def exchangeable_bond(
        self, *, corp_code: str, begin_date: str, end_date: str
    ) -> Rows:
        """교환사채권(EB) 발행결정 (2020035)."""
        return self._event(EXCHANGEABLE_BOND, corp_code, begin_date, end_date)

    def contingent_convertible_bond(
        self, *, corp_code: str, begin_date: str, end_date: str
    ) -> Rows:
        """상각형 조건부자본증권 발행결정 (2020037)."""
        return self._event(CONTINGENT_CONVERTIBLE_BOND, corp_code, begin_date, end_date)

    def treasury_acquisition(
        self, *, corp_code: str, begin_date: str, end_date: str
    ) -> Rows:
        """자기주식 취득 결정 (2020038)."""
        return self._event(TREASURY_ACQUISITION, corp_code, begin_date, end_date)

    def treasury_disposal(
        self, *, corp_code: str, begin_date: str, end_date: str
    ) -> Rows:
        """자기주식 처분 결정 (2020039)."""
        return self._event(TREASURY_DISPOSAL, corp_code, begin_date, end_date)

    def treasury_trust_contract(
        self, *, corp_code: str, begin_date: str, end_date: str
    ) -> Rows:
        """자기주식취득 신탁계약 체결 결정 (2020040)."""
        return self._event(TREASURY_TRUST_CONTRACT, corp_code, begin_date, end_date)

    def treasury_trust_termination(
        self, *, corp_code: str, begin_date: str, end_date: str
    ) -> Rows:
        """자기주식취득 신탁계약 해지 결정 (2020041)."""
        return self._event(TREASURY_TRUST_TERMINATION, corp_code, begin_date, end_date)

    def asset_transfer(
        self, *, corp_code: str, begin_date: str, end_date: str
    ) -> Rows:
        """자산양수도(기타), 풋백옵션 (2020018)."""
        return self._event(ASSET_TRANSFER, corp_code, begin_date, end_date)

    def business_acquisition(
        self, *, corp_code: str, begin_date: str, end_date: str
    ) -> Rows:
        """영업양수 결정 (2020042)."""
        return self._event(BUSINESS_ACQUISITION, corp_code, begin_date, end_date)

    def business_transfer(
        self, *, corp_code: str, begin_date: str, end_date: str
    ) -> Rows:
        """영업양도 결정 (2020043)."""
        return self._event(BUSINESS_TRANSFER, corp_code, begin_date, end_date)

    def tangible_asset_acquisition(
        self, *, corp_code: str, begin_date: str, end_date: str
    ) -> Rows:
        """유형자산 양수 결정 (2020044)."""
        return self._event(TANGIBLE_ASSET_ACQUISITION, corp_code, begin_date, end_date)

    def tangible_asset_transfer(
        self, *, corp_code: str, begin_date: str, end_date: str
    ) -> Rows:
        """유형자산 양도 결정 (2020045)."""
        return self._event(TANGIBLE_ASSET_TRANSFER, corp_code, begin_date, end_date)

    def equity_stake_acquisition(
        self, *, corp_code: str, begin_date: str, end_date: str
    ) -> Rows:
        """타법인 주식 및 출자증권 양수결정 (2020046)."""
        return self._event(EQUITY_STAKE_ACQUISITION, corp_code, begin_date, end_date)

    def equity_stake_transfer(
        self, *, corp_code: str, begin_date: str, end_date: str
    ) -> Rows:
        """타법인 주식 및 출자증권 양도결정 (2020047)."""
        return self._event(EQUITY_STAKE_TRANSFER, corp_code, begin_date, end_date)

    def equity_bond_acquisition(
        self, *, corp_code: str, begin_date: str, end_date: str
    ) -> Rows:
        """주권 관련 사채권 양수 결정 (2020048)."""
        return self._event(EQUITY_BOND_ACQUISITION, corp_code, begin_date, end_date)

    def equity_bond_transfer(
        self, *, corp_code: str, begin_date: str, end_date: str
    ) -> Rows:
        """주권 관련 사채권 양도 결정 (2020049)."""
        return self._event(EQUITY_BOND_TRANSFER, corp_code, begin_date, end_date)

    def merger(
        self, *, corp_code: str, begin_date: str, end_date: str
    ) -> Rows:
        """회사합병 결정 (2020050)."""
        return self._event(MERGER, corp_code, begin_date, end_date)

    def spinoff(
        self, *, corp_code: str, begin_date: str, end_date: str
    ) -> Rows:
        """회사분할 결정 (2020051)."""
        return self._event(SPINOFF, corp_code, begin_date, end_date)

    def split_merger(
        self, *, corp_code: str, begin_date: str, end_date: str
    ) -> Rows:
        """회사분할합병 결정 (2020052)."""
        return self._event(SPLIT_MERGER, corp_code, begin_date, end_date)

    def stock_exchange(
        self, *, corp_code: str, begin_date: str, end_date: str
    ) -> Rows:
        """주식교환·이전 결정 (2020053)."""
        return self._event(STOCK_EXCHANGE, corp_code, begin_date, end_date)
