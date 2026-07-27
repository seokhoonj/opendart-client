"""Closed OpenDART vocabularies, typed as ``Literal`` aliases.

Every value here is a fixed enumeration the API accepts; typing the params with these
aliases makes a typo fail the type checker instead of reaching OpenDART as a 100
(부적절한 값) error. Shared across sub-surfaces so one concept has one spelling.
"""

from __future__ import annotations

from typing import Literal

# 보고서 코드: 사업보고서 / 반기 / 1분기 / 3분기
ReportCode = Literal["11011", "11012", "11013", "11014"]

# 재무제표 구분: 연결 / 별도
StatementDiv = Literal["CFS", "OFS"]

# 법인구분: 유가 / 코스닥 / 코넥스 / 기타
CorpClass = Literal["Y", "K", "N", "E"]

# 공시유형 pblntf_ty. A정기 B주요사항 C발행 D지분 E기타
# F외부감사 G펀드 H자산유동화 I거래소 J공정위
DisclosureType = Literal["A", "B", "C", "D", "E", "F", "G", "H", "I", "J"]

# 공시검색 정렬 기준: 접수일자 / 회사명 / 보고서명
SortField = Literal["date", "crp", "rpt"]

# 정렬 방법: 오름차순 / 내림차순
SortOrder = Literal["asc", "desc"]

# 재무지표 분류: 수익성 / 안정성 / 성장성 / 활동성 (idx_cl_code)
IndexClass = Literal["M210000", "M220000", "M230000", "M240000"]

# XBRL 택사노미 재무제표 구분 (sj_div): 재무상태표(BS) / 손익계산서(IS) /
# 포괄손익계산서(CIS) / 별도포괄손익계산서(DCIS) / 현금흐름표(CF) / 자본변동표(SCE)
StatementKind = Literal[
    "BS1", "BS2", "BS3", "BS4",
    "IS1", "IS2", "IS3", "IS4",
    "CIS1", "CIS2", "CIS3", "CIS4",
    "DCIS1", "DCIS2", "DCIS3", "DCIS4", "DCIS5", "DCIS6", "DCIS7", "DCIS8",
    "CF1", "CF2", "CF3", "CF4",
    "SCE1", "SCE2",
]
