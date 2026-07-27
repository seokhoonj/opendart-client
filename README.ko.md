# opendart-client

[![check](https://github.com/seokhoonj/opendart-client/actions/workflows/check.yml/badge.svg)](https://github.com/seokhoonj/opendart-client/actions/workflows/check.yml)
[![PyPI](https://img.shields.io/pypi/v/opendart-client)](https://pypi.org/project/opendart-client/)
[![Python](https://img.shields.io/pypi/pyversions/opendart-client)](https://pypi.org/project/opendart-client/)
[![License](https://img.shields.io/pypi/l/opendart-client)](https://github.com/seokhoonj/opendart-client/blob/main/LICENSE)

[English](https://github.com/seokhoonj/opendart-client/blob/main/README.md) | **한국어**

한국 **OpenDART**(금융감독원 전자공시시스템) API를 위한 깔끔한 타입드 파이썬 클라이언트.
미국 SEC EDGAR에 해당하는 그 전자공시죠.

의존성 0개, 동기(sync), `dict` / `list[dict]` 그대로 반환 — DataFrame은 원하는 대로.

## 설치

```bash
pip install opendart-client
```

무료 API 키(40자리)는 <https://opendart.fss.or.kr> 에서 발급.

## 빠른 시작

```python
from opendartclient import OpenDart

dart = OpenDart(api_key="...")          # 또는 환경변수 OPENDART_API_KEY

# 이름 / 티커 / 초성 / 오타 -> corp_code
code = dart.resolver().resolve("삼성전자")          # "00126380"

# 기간 내 공시 목록
rows = dart.disclosure.search(
    corp_code=code, begin_date="20260101", end_date="20260131",
)

# 재무제표, 그리고 모든 주요사항(이벤트)
dart.finance.single_accounts(code, fiscal_year=2025)
dart.event.paid_in_capital_increase(
    corp_code=code, begin_date="20260101", end_date="20260131",
)

# DataFrame이 필요하면 — 반환이 list[dict]이라 생성자에 그대로 넣으면 됩니다
import pandas as pd
pd.DataFrame(rows)
# 또는
import polars as pl
pl.DataFrame(rows)
```

## 특징

- **OpenDART 85개 엔드포인트 전부** — 공시정보 · 정기보고서 · 재무정보 · 지분공시 ·
  주요사항보고서 · 증권신고서 6그룹을, **읽히는 메서드명**으로
  (`dart.event.convertible_bond(...)`, `cvbdIsDecsn` 아님).
- **회사 리졸버** — 이름 / 티커 / 초성(`ㅅㅅㅈㅈ`) / 오타 → `corp_code`.
- **런타임 의존성 0개** — 표준 라이브러리만. 반환이 `list[dict]`이라 `pandas.DataFrame` ·
  `polars.DataFrame` 생성자에 바로 넣으면 됩니다(어댑터 불필요).
- **완전 타입드**, `py.typed` 동봉. 닫힌 어휘는 `Literal`이라 잘못된 코드는 API가
  아니라 타입체커가 잡음.
- **raw 반환** — `list[dict]`(flat) · `dict[str, list[dict]]`(grouped) · `bytes`(zip
  엔드포인트). `status 013`(데이터 없음)은 빈 결과, 그 외 에러는 타입드 `DartError`.

## API

최상위: `dart.corp_codes()` (전체 corp_code↔이름/티커), `dart.resolver()` →
`CorpResolver.resolve(query)` / `.search(query)`.

`report_code` 기본값 `"11011"`(사업보고서). 다른 값: `11012` 반기, `11013` 1분기,
`11014` 3분기.

### disclosure — 공시정보

| 메서드 | 설명 |
|---|---|
| `search(corp_code=…, begin_date=…, end_date=…, …)` | 공시검색: 기간·필터에 맞는 모든 공시 (자동 페이지네이션) |
| `company(corp_code)` | 기업개황 (상호·대표·주소·업종 등) |
| `document(rcept_no)` | 공시서류 원본파일 (zip `bytes`) |

### report — 정기보고서 주요정보

모두 `(corp_code, *, fiscal_year, report_code="11011")`.

| 메서드 | 설명 |
|---|---|
| `total_shares` | 주식의 총수 현황 |
| `treasury_shares` | 자기주식 취득 및 처분 현황 |
| `dividends` | 배당에 관한 사항 |
| `capital_changes` | 증자(감자) 현황 |
| `debt_securities_issued` | 채무증권 발행실적 |
| `commercial_paper_outstanding` | 기업어음증권 미상환 잔액 |
| `short_term_bond_outstanding` | 단기사채 미상환 잔액 |
| `corporate_bond_outstanding` | 회사채 미상환 잔액 |
| `hybrid_security_outstanding` | 신종자본증권 미상환 잔액 |
| `contingent_capital_outstanding` | 조건부 자본증권 미상환 잔액 |
| `public_offering_fund_usage` | 공모자금의 사용내역 |
| `private_placement_fund_usage` | 사모자금의 사용내역 |
| `audit_opinion` | 회계감사인의 명칭 및 감사의견 |
| `audit_service_contracts` | 감사용역체결현황 |
| `non_audit_service_contracts` | 회계감사인과의 비감사용역 계약체결 현황 |
| `outside_directors` | 독립(사외)이사 및 그 변동현황 |
| `largest_shareholders` | 최대주주 현황 |
| `largest_shareholder_changes` | 최대주주 변동현황 |
| `minority_shareholders` | 소액주주 현황 |
| `executives` | 임원 현황 |
| `employees` | 직원 현황 |
| `unregistered_executive_pay` | 미등기임원 보수현황 |
| `director_pay_approved` | 이사·감사 전체의 보수현황(주주총회 승인금액) |
| `director_pay_total` | 이사·감사 전체의 보수현황(보수지급금액 - 전체) |
| `director_pay_by_type` | 이사·감사 전체의 보수현황(유형별) |
| `individual_pay` | 이사·감사의 개인별 보수현황(5억원 이상) |
| `individual_pay_v2` | 개인별 보수현황(5억원 이상) Ver2.0 — 2026-05 이후 제출분, grouped |
| `top5_individual_pay` | 개인별 보수지급 금액(5억이상 상위5인) |
| `top5_individual_pay_v2` | 개인별 보수지급(상위5인) Ver2.0 — 2026-05 이후 제출분, grouped |
| `equity_investments` | 타법인 출자현황 |

### finance — 재무정보

| 메서드 | 설명 |
|---|---|
| `single_accounts(corp_code, *, fiscal_year, report_code)` | 단일회사 주요계정 |
| `multi_accounts(corp_codes, *, fiscal_year, report_code)` | 다중회사 주요계정 (여러 회사 동시) |
| `full_statements(corp_code, *, fiscal_year, statement_div, report_code)` | 단일회사 전체 재무제표 (BS/IS/CIS/CF 전 항목) |
| `single_indicators(corp_code, *, fiscal_year, index_class, report_code)` | 단일회사 주요 재무지표 |
| `multi_indicators(corp_codes, *, fiscal_year, index_class, report_code)` | 다중회사 주요 재무지표 |
| `xbrl_document(rcept_no, *, report_code)` | 재무제표 원본파일(XBRL) — zip `bytes` |
| `xbrl_taxonomy(*, statement_kind)` | XBRL 택사노미 재무제표 양식 |

### ownership — 지분공시

| 메서드 | 설명 |
|---|---|
| `insider_holdings(corp_code)` | 임원·주요주주 소유보고 |
| `five_percent_holdings(corp_code)` | 대량보유 상황보고 (5%룰) |

### event — 주요사항보고서

모두 `(corp_code, *, begin_date, end_date)`.

| 메서드 | 설명 |
|---|---|
| `default_occurrence` | 부도발생 |
| `business_suspension` | 영업정지 |
| `rehabilitation_filing` | 회생절차 개시신청 |
| `dissolution_cause` | 해산사유 발생 |
| `paid_in_capital_increase` | 유상증자 결정 |
| `bonus_issue` | 무상증자 결정 |
| `combined_capital_increase` | 유무상증자 결정 |
| `capital_reduction` | 감자 결정 |
| `creditor_management_start` | 채권은행 등의 관리절차 개시 |
| `creditor_management_stop` | 채권은행 등의 관리절차 중단 |
| `litigation` | 소송 등의 제기 |
| `overseas_listing_decision` | 해외 증권시장 주권등 상장 결정 |
| `overseas_delisting_decision` | 해외 증권시장 주권등 상장폐지 결정 |
| `overseas_listing` | 해외 증권시장 주권등 상장 |
| `overseas_delisting` | 해외 증권시장 주권등 상장폐지 |
| `convertible_bond` | 전환사채권(CB) 발행결정 |
| `bond_with_warrant` | 신주인수권부사채권(BW) 발행결정 |
| `exchangeable_bond` | 교환사채권(EB) 발행결정 |
| `contingent_convertible_bond` | 상각형 조건부자본증권 발행결정 |
| `treasury_acquisition` | 자기주식 취득 결정 |
| `treasury_disposal` | 자기주식 처분 결정 |
| `treasury_trust_contract` | 자기주식취득 신탁계약 체결 결정 |
| `treasury_trust_termination` | 자기주식취득 신탁계약 해지 결정 |
| `asset_transaction` | 자산양수도(기타), 풋백옵션 |
| `business_acquisition` | 영업양수 결정 |
| `business_transfer` | 영업양도 결정 |
| `tangible_asset_acquisition` | 유형자산 양수 결정 |
| `tangible_asset_transfer` | 유형자산 양도 결정 |
| `equity_stake_acquisition` | 타법인 주식 및 출자증권 양수결정 |
| `equity_stake_transfer` | 타법인 주식 및 출자증권 양도결정 |
| `equity_bond_acquisition` | 주권 관련 사채권 양수 결정 |
| `equity_bond_transfer` | 주권 관련 사채권 양도 결정 |
| `merger` | 회사합병 결정 |
| `spinoff` | 회사분할 결정 |
| `split_merger` | 회사분할합병 결정 |
| `stock_exchange` | 주식교환·이전 결정 |

### registration — 증권신고서

모두 `(corp_code, *, begin_date, end_date)`.

| 메서드 | 설명 |
|---|---|
| `equity_securities` | 지분증권 |
| `debt_securities` | 채무증권 |
| `depositary_receipts` | 증권예탁증권 |
| `merger` | 합병 |
| `stock_exchange` | 주식의 포괄적 교환·이전 |
| `division` | 분할 |

## 라이선스

MIT © Seokhoon Joo
