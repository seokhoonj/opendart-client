"""The 85-endpoint contract guard.

An INDEPENDENT, hand-maintained table of every endpoint's (api_id, operation stem,
api_group, response_shape). The source declares the same 85 as module constants; this
asserts the two agree exactly -- so a typo in any hand-written stem or api_id (there are
68 hand-coded event/report methods) fails the suite instead of silently hitting the
wrong DART endpoint. The table is copied from the OpenDART guide, not from the source,
on purpose: it is the second witness.
"""

from opendartkit._endpoint import DartEndpoint

# (api_id, operation, api_group, response_shape)
AUTHORITATIVE: set[tuple[str, str, str, str]] = {
    # DS001 공시정보
    ("2019001", "list", "DS001", "flat"),
    ("2019002", "company", "DS001", "flat"),
    ("2019003", "document", "DS001", "flat"),
    ("2019018", "corpCode", "DS001", "flat"),
    # DS002 정기보고서 주요정보
    ("2020002", "stockTotqySttus", "DS002", "flat"),
    ("2019006", "tesstkAcqsDspsSttus", "DS002", "flat"),
    ("2019005", "alotMatter", "DS002", "flat"),
    ("2019004", "irdsSttus", "DS002", "flat"),
    ("2020003", "detScritsIsuAcmslt", "DS002", "flat"),
    ("2020004", "entrprsBilScritsNrdmpBlce", "DS002", "flat"),
    ("2020005", "srtpdPsndbtNrdmpBlce", "DS002", "flat"),
    ("2020006", "cprndNrdmpBlce", "DS002", "flat"),
    ("2020007", "newCaplScritsNrdmpBlce", "DS002", "flat"),
    ("2020008", "cndlCaplScritsNrdmpBlce", "DS002", "flat"),
    ("2020016", "pssrpCptalUseDtls", "DS002", "flat"),
    ("2020017", "prvsrpCptalUseDtls", "DS002", "flat"),
    ("2020009", "accnutAdtorNmNdAdtOpinion", "DS002", "flat"),
    ("2020010", "adtServcCnclsSttus", "DS002", "flat"),
    ("2020011", "accnutAdtorNonAdtServcCnclsSttus", "DS002", "flat"),
    ("2020012", "outcmpnyDrctrNdChangeSttus", "DS002", "flat"),
    ("2019007", "hyslrSttus", "DS002", "flat"),
    ("2019008", "hyslrChgSttus", "DS002", "flat"),
    ("2019009", "mrhlSttus", "DS002", "flat"),
    ("2019010", "exctvSttus", "DS002", "flat"),
    ("2019011", "empSttus", "DS002", "flat"),
    ("2020013", "unrstExctvMendngSttus", "DS002", "flat"),
    ("2020014", "drctrAdtAllMendngSttusGmtsckConfmAmount", "DS002", "flat"),
    ("2019013", "hmvAuditAllSttus", "DS002", "flat"),
    ("2020015", "drctrAdtAllMendngSttusMendngPymntamtTyCl", "DS002", "flat"),
    ("2019012", "hmvAuditIndvdlBySttus", "DS002", "flat"),
    ("2026001", "hmvAuditIndvdlBySttusV2", "DS002", "grouped"),
    ("2019014", "indvdlByPay", "DS002", "flat"),
    ("2026002", "indvdlByPayV2", "DS002", "grouped"),
    ("2019015", "otrCprInvstmntSttus", "DS002", "flat"),
    # DS003 정기보고서 재무정보
    ("2019016", "fnlttSinglAcnt", "DS003", "flat"),
    ("2019017", "fnlttMultiAcnt", "DS003", "flat"),
    ("2019020", "fnlttSinglAcntAll", "DS003", "flat"),
    ("2022001", "fnlttSinglIndx", "DS003", "flat"),
    ("2022002", "fnlttCmpnyIndx", "DS003", "flat"),
    ("2019019", "fnlttXbrl", "DS003", "flat"),
    ("2020001", "xbrlTaxonomy", "DS003", "flat"),
    # DS004 지분공시
    ("2019022", "elestock", "DS004", "flat"),
    ("2019021", "majorstock", "DS004", "flat"),
    # DS005 주요사항보고서
    ("2020019", "dfOcr", "DS005", "flat"),
    ("2020020", "bsnSp", "DS005", "flat"),
    ("2020021", "ctrcvsBgrq", "DS005", "flat"),
    ("2020022", "dsRsOcr", "DS005", "flat"),
    ("2020023", "piicDecsn", "DS005", "flat"),
    ("2020024", "fricDecsn", "DS005", "flat"),
    ("2020025", "pifricDecsn", "DS005", "flat"),
    ("2020026", "crDecsn", "DS005", "flat"),
    ("2020027", "bnkMngtPcbg", "DS005", "flat"),
    ("2020036", "bnkMngtPcsp", "DS005", "flat"),
    ("2020028", "lwstLg", "DS005", "flat"),
    ("2020029", "ovLstDecsn", "DS005", "flat"),
    ("2020030", "ovDlstDecsn", "DS005", "flat"),
    ("2020031", "ovLst", "DS005", "flat"),
    ("2020032", "ovDlst", "DS005", "flat"),
    ("2020033", "cvbdIsDecsn", "DS005", "flat"),
    ("2020034", "bdwtIsDecsn", "DS005", "flat"),
    ("2020035", "exbdIsDecsn", "DS005", "flat"),
    ("2020037", "wdCocobdIsDecsn", "DS005", "flat"),
    ("2020038", "tsstkAqDecsn", "DS005", "flat"),
    ("2020039", "tsstkDpDecsn", "DS005", "flat"),
    ("2020040", "tsstkAqTrctrCnsDecsn", "DS005", "flat"),
    ("2020041", "tsstkAqTrctrCcDecsn", "DS005", "flat"),
    ("2020018", "astInhtrfEtcPtbkOpt", "DS005", "flat"),
    ("2020042", "bsnInhDecsn", "DS005", "flat"),
    ("2020043", "bsnTrfDecsn", "DS005", "flat"),
    ("2020044", "tgastInhDecsn", "DS005", "flat"),
    ("2020045", "tgastTrfDecsn", "DS005", "flat"),
    ("2020046", "otcprStkInvscrInhDecsn", "DS005", "flat"),
    ("2020047", "otcprStkInvscrTrfDecsn", "DS005", "flat"),
    ("2020048", "stkrtbdInhDecsn", "DS005", "flat"),
    ("2020049", "stkrtbdTrfDecsn", "DS005", "flat"),
    ("2020050", "cmpMgDecsn", "DS005", "flat"),
    ("2020051", "cmpDvDecsn", "DS005", "flat"),
    ("2020052", "cmpDvmgDecsn", "DS005", "flat"),
    ("2020053", "stkExtrDecsn", "DS005", "flat"),
    # DS006 증권신고서 (all grouped)
    ("2020054", "estkRs", "DS006", "grouped"),
    ("2020055", "bdRs", "DS006", "grouped"),
    ("2020056", "stkdpRs", "DS006", "grouped"),
    ("2020057", "mgRs", "DS006", "grouped"),
    ("2020058", "extrRs", "DS006", "grouped"),
    ("2020059", "dvRs", "DS006", "grouped"),
}


def _source_endpoints() -> set[tuple[str, str, str, str]]:
    from opendartkit import (
        client,
        disclosure,
        event,
        finance,
        ownership,
        registration,
        report,
    )
    found: dict[str, tuple[str, str, str, str]] = {}
    for module in (client, disclosure, report, finance, ownership, event, registration):
        for value in vars(module).values():
            if isinstance(value, DartEndpoint):
                found[value.api_id] = (
                    value.api_id, value.operation, value.api_group, value.response_shape
                )
    return set(found.values())


def test_source_endpoints_match_the_authoritative_table_exactly():
    source = _source_endpoints()
    assert source == AUTHORITATIVE, (
        f"only in source: {source - AUTHORITATIVE}\n"
        f"only in table:  {AUTHORITATIVE - source}"
    )


def test_authoritative_table_has_85_unique_endpoints():
    assert len(AUTHORITATIVE) == 85
    assert len({row[0] for row in AUTHORITATIVE}) == 85   # unique api_id
    assert len({row[1] for row in AUTHORITATIVE}) == 85   # unique operation stem
