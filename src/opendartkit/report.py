"""정기보고서 주요정보 (DS002) -- the non-financial items of a periodic report.

The other half of a 정기보고서 (the financial half is DS003 ``finance``): dividends,
share totals, capital changes, largest/minority shareholders, executives, employees,
remuneration, audit opinions, equity investments. Every endpoint is keyed by
``corp_code`` + ``bsns_year`` + ``report_code``. Two remuneration endpoints (Ver2.0,
2026-05 onward) return a grouped body and so return ``dict[str, list[dict]]``.
"""

from __future__ import annotations

from typing import Any

from ._endpoint import DartEndpoint
from .session import DartSession
from .types import ReportCode

Rows = list[dict[str, Any]]
Groups = dict[str, list[dict[str, Any]]]

_R = ("corp_code", "bsns_year", "reprt_code")


def _ep(operation: str, api_id: str, *, grouped: bool = False) -> DartEndpoint:
    return DartEndpoint(
        operation, "DS002", api_id, required=_R,
        response_shape="grouped" if grouped else "flat",
    )


SHARE_TOTAL = _ep("stockTotqySttus", "2020002")
TREASURY_SHARES = _ep("tesstkAcqsDspsSttus", "2019006")
DIVIDENDS = _ep("alotMatter", "2019005")
CAPITAL_CHANGES = _ep("irdsSttus", "2019004")
DEBT_SECURITIES_ISSUED = _ep("detScritsIsuAcmslt", "2020003")
COMMERCIAL_PAPER_OUTSTANDING = _ep("entrprsBilScritsNrdmpBlce", "2020004")
SHORT_TERM_BOND_OUTSTANDING = _ep("srtpdPsndbtNrdmpBlce", "2020005")
CORPORATE_BOND_OUTSTANDING = _ep("cprndNrdmpBlce", "2020006")
HYBRID_SECURITY_OUTSTANDING = _ep("newCaplScritsNrdmpBlce", "2020007")
CONTINGENT_CAPITAL_OUTSTANDING = _ep("cndlCaplScritsNrdmpBlce", "2020008")
PUBLIC_OFFERING_FUND_USAGE = _ep("pssrpCptalUseDtls", "2020016")
PRIVATE_PLACEMENT_FUND_USAGE = _ep("prvsrpCptalUseDtls", "2020017")
AUDIT_OPINION = _ep("accnutAdtorNmNdAdtOpinion", "2020009")
AUDIT_SERVICE_CONTRACTS = _ep("adtServcCnclsSttus", "2020010")
NON_AUDIT_SERVICE_CONTRACTS = _ep("accnutAdtorNonAdtServcCnclsSttus", "2020011")
OUTSIDE_DIRECTORS = _ep("outcmpnyDrctrNdChangeSttus", "2020012")
LARGEST_SHAREHOLDERS = _ep("hyslrSttus", "2019007")
LARGEST_SHAREHOLDER_CHANGES = _ep("hyslrChgSttus", "2019008")
MINORITY_SHAREHOLDERS = _ep("mrhlSttus", "2019009")
EXECUTIVES = _ep("exctvSttus", "2019010")
EMPLOYEES = _ep("empSttus", "2019011")
UNREGISTERED_EXECUTIVE_PAY = _ep("unrstExctvMendngSttus", "2020013")
DIRECTOR_PAY_APPROVED = _ep("drctrAdtAllMendngSttusGmtsckConfmAmount", "2020014")
DIRECTOR_PAY_TOTAL = _ep("hmvAuditAllSttus", "2019013")
DIRECTOR_PAY_BY_TYPE = _ep("drctrAdtAllMendngSttusMendngPymntamtTyCl", "2020015")
INDIVIDUAL_PAY = _ep("hmvAuditIndvdlBySttus", "2019012")
INDIVIDUAL_PAY_V2 = _ep("hmvAuditIndvdlBySttusV2", "2026001", grouped=True)
TOP5_INDIVIDUAL_PAY = _ep("indvdlByPay", "2019014")
TOP5_INDIVIDUAL_PAY_V2 = _ep("indvdlByPayV2", "2026002", grouped=True)
EQUITY_INVESTMENTS = _ep("otrCprInvstmntSttus", "2019015")


class Report:
    """정기보고서 주요정보 (DS002). Reach it as ``DartClient.report``.

    Every method takes ``corp_code`` + ``fiscal_year`` + ``report_code`` (사업/반기/
    1분기/3분기, default 사업보고서) and returns the matching rows.
    """

    def __init__(self, session: DartSession) -> None:
        self._session = session

    def _report(
        self, endpoint: DartEndpoint, corp_code: str, fiscal_year: int, report_code: ReportCode
    ) -> Rows:
        return self._session.fetch_list(
            endpoint, corp_code=corp_code, bsns_year=str(fiscal_year), reprt_code=report_code
        )

    def _report_groups(
        self, endpoint: DartEndpoint, corp_code: str, fiscal_year: int, report_code: ReportCode
    ) -> Groups:
        return self._session.fetch_groups(
            endpoint, corp_code=corp_code, bsns_year=str(fiscal_year), reprt_code=report_code
        )

    def share_total(
        self, corp_code: str, *, fiscal_year: int, report_code: ReportCode = "11011"
    ) -> Rows:
        """주식의 총수 현황 (2020002)."""
        return self._report(SHARE_TOTAL, corp_code, fiscal_year, report_code)

    def treasury_shares(
        self, corp_code: str, *, fiscal_year: int, report_code: ReportCode = "11011"
    ) -> Rows:
        """자기주식 취득 및 처분 현황 (2019006)."""
        return self._report(TREASURY_SHARES, corp_code, fiscal_year, report_code)

    def dividends(
        self, corp_code: str, *, fiscal_year: int, report_code: ReportCode = "11011"
    ) -> Rows:
        """배당에 관한 사항 (2019005)."""
        return self._report(DIVIDENDS, corp_code, fiscal_year, report_code)

    def capital_changes(
        self, corp_code: str, *, fiscal_year: int, report_code: ReportCode = "11011"
    ) -> Rows:
        """증자(감자) 현황 (2019004)."""
        return self._report(CAPITAL_CHANGES, corp_code, fiscal_year, report_code)

    def debt_securities_issued(
        self, corp_code: str, *, fiscal_year: int, report_code: ReportCode = "11011"
    ) -> Rows:
        """채무증권 발행실적 (2020003)."""
        return self._report(DEBT_SECURITIES_ISSUED, corp_code, fiscal_year, report_code)

    def commercial_paper_outstanding(
        self, corp_code: str, *, fiscal_year: int, report_code: ReportCode = "11011"
    ) -> Rows:
        """기업어음증권 미상환 잔액 (2020004)."""
        return self._report(COMMERCIAL_PAPER_OUTSTANDING, corp_code, fiscal_year, report_code)

    def short_term_bond_outstanding(
        self, corp_code: str, *, fiscal_year: int, report_code: ReportCode = "11011"
    ) -> Rows:
        """단기사채 미상환 잔액 (2020005)."""
        return self._report(SHORT_TERM_BOND_OUTSTANDING, corp_code, fiscal_year, report_code)

    def corporate_bond_outstanding(
        self, corp_code: str, *, fiscal_year: int, report_code: ReportCode = "11011"
    ) -> Rows:
        """회사채 미상환 잔액 (2020006)."""
        return self._report(CORPORATE_BOND_OUTSTANDING, corp_code, fiscal_year, report_code)

    def hybrid_security_outstanding(
        self, corp_code: str, *, fiscal_year: int, report_code: ReportCode = "11011"
    ) -> Rows:
        """신종자본증권 미상환 잔액 (2020007)."""
        return self._report(HYBRID_SECURITY_OUTSTANDING, corp_code, fiscal_year, report_code)

    def contingent_capital_outstanding(
        self, corp_code: str, *, fiscal_year: int, report_code: ReportCode = "11011"
    ) -> Rows:
        """조건부 자본증권 미상환 잔액 (2020008)."""
        return self._report(CONTINGENT_CAPITAL_OUTSTANDING, corp_code, fiscal_year, report_code)

    def public_offering_fund_usage(
        self, corp_code: str, *, fiscal_year: int, report_code: ReportCode = "11011"
    ) -> Rows:
        """공모자금의 사용내역 (2020016)."""
        return self._report(PUBLIC_OFFERING_FUND_USAGE, corp_code, fiscal_year, report_code)

    def private_placement_fund_usage(
        self, corp_code: str, *, fiscal_year: int, report_code: ReportCode = "11011"
    ) -> Rows:
        """사모자금의 사용내역 (2020017)."""
        return self._report(PRIVATE_PLACEMENT_FUND_USAGE, corp_code, fiscal_year, report_code)

    def audit_opinion(
        self, corp_code: str, *, fiscal_year: int, report_code: ReportCode = "11011"
    ) -> Rows:
        """회계감사인의 명칭 및 감사의견 (2020009)."""
        return self._report(AUDIT_OPINION, corp_code, fiscal_year, report_code)

    def audit_service_contracts(
        self, corp_code: str, *, fiscal_year: int, report_code: ReportCode = "11011"
    ) -> Rows:
        """감사용역체결현황 (2020010)."""
        return self._report(AUDIT_SERVICE_CONTRACTS, corp_code, fiscal_year, report_code)

    def non_audit_service_contracts(
        self, corp_code: str, *, fiscal_year: int, report_code: ReportCode = "11011"
    ) -> Rows:
        """회계감사인과의 비감사용역 계약체결 현황 (2020011)."""
        return self._report(NON_AUDIT_SERVICE_CONTRACTS, corp_code, fiscal_year, report_code)

    def outside_directors(
        self, corp_code: str, *, fiscal_year: int, report_code: ReportCode = "11011"
    ) -> Rows:
        """독립(사외)이사 및 그 변동현황 (2020012)."""
        return self._report(OUTSIDE_DIRECTORS, corp_code, fiscal_year, report_code)

    def largest_shareholders(
        self, corp_code: str, *, fiscal_year: int, report_code: ReportCode = "11011"
    ) -> Rows:
        """최대주주 현황 (2019007)."""
        return self._report(LARGEST_SHAREHOLDERS, corp_code, fiscal_year, report_code)

    def largest_shareholder_changes(
        self, corp_code: str, *, fiscal_year: int, report_code: ReportCode = "11011"
    ) -> Rows:
        """최대주주 변동현황 (2019008)."""
        return self._report(LARGEST_SHAREHOLDER_CHANGES, corp_code, fiscal_year, report_code)

    def minority_shareholders(
        self, corp_code: str, *, fiscal_year: int, report_code: ReportCode = "11011"
    ) -> Rows:
        """소액주주 현황 (2019009)."""
        return self._report(MINORITY_SHAREHOLDERS, corp_code, fiscal_year, report_code)

    def executives(
        self, corp_code: str, *, fiscal_year: int, report_code: ReportCode = "11011"
    ) -> Rows:
        """임원 현황 (2019010)."""
        return self._report(EXECUTIVES, corp_code, fiscal_year, report_code)

    def employees(
        self, corp_code: str, *, fiscal_year: int, report_code: ReportCode = "11011"
    ) -> Rows:
        """직원 현황 (2019011)."""
        return self._report(EMPLOYEES, corp_code, fiscal_year, report_code)

    def unregistered_executive_pay(
        self, corp_code: str, *, fiscal_year: int, report_code: ReportCode = "11011"
    ) -> Rows:
        """미등기임원 보수현황 (2020013)."""
        return self._report(UNREGISTERED_EXECUTIVE_PAY, corp_code, fiscal_year, report_code)

    def director_pay_approved(
        self, corp_code: str, *, fiscal_year: int, report_code: ReportCode = "11011"
    ) -> Rows:
        """이사·감사 전체의 보수현황(주주총회 승인금액) (2020014)."""
        return self._report(DIRECTOR_PAY_APPROVED, corp_code, fiscal_year, report_code)

    def director_pay_total(
        self, corp_code: str, *, fiscal_year: int, report_code: ReportCode = "11011"
    ) -> Rows:
        """이사·감사 전체의 보수현황(보수지급금액 - 전체) (2019013)."""
        return self._report(DIRECTOR_PAY_TOTAL, corp_code, fiscal_year, report_code)

    def director_pay_by_type(
        self, corp_code: str, *, fiscal_year: int, report_code: ReportCode = "11011"
    ) -> Rows:
        """이사·감사 전체의 보수현황(유형별) (2020015)."""
        return self._report(DIRECTOR_PAY_BY_TYPE, corp_code, fiscal_year, report_code)

    def individual_pay(
        self, corp_code: str, *, fiscal_year: int, report_code: ReportCode = "11011"
    ) -> Rows:
        """이사·감사의 개인별 보수현황(5억원 이상) (2019012)."""
        return self._report(INDIVIDUAL_PAY, corp_code, fiscal_year, report_code)

    def individual_pay_v2(
        self, corp_code: str, *, fiscal_year: int, report_code: ReportCode = "11011"
    ) -> Groups:
        """개인별 보수현황(5억원 이상) Ver2.0 (2026001). 2026-05 이후 제출분; grouped."""
        return self._report_groups(INDIVIDUAL_PAY_V2, corp_code, fiscal_year, report_code)

    def top5_individual_pay(
        self, corp_code: str, *, fiscal_year: int, report_code: ReportCode = "11011"
    ) -> Rows:
        """개인별 보수지급 금액(5억이상 상위5인) (2019014)."""
        return self._report(TOP5_INDIVIDUAL_PAY, corp_code, fiscal_year, report_code)

    def top5_individual_pay_v2(
        self, corp_code: str, *, fiscal_year: int, report_code: ReportCode = "11011"
    ) -> Groups:
        """개인별 보수지급(상위5인) Ver2.0 (2026002). 2026-05 이후 제출분; grouped."""
        return self._report_groups(TOP5_INDIVIDUAL_PAY_V2, corp_code, fiscal_year, report_code)

    def equity_investments(
        self, corp_code: str, *, fiscal_year: int, report_code: ReportCode = "11011"
    ) -> Rows:
        """타법인 출자현황 (2019015)."""
        return self._report(EQUITY_INVESTMENTS, corp_code, fiscal_year, report_code)
