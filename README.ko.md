# opendart-client

[![check](https://github.com/seokhoonj/opendart-client/actions/workflows/check.yml/badge.svg)](https://github.com/seokhoonj/opendart-client/actions/workflows/check.yml)
[![PyPI](https://img.shields.io/pypi/v/opendart-client)](https://pypi.org/project/opendart-client/)
[![Python](https://img.shields.io/pypi/pyversions/opendart-client)](https://pypi.org/project/opendart-client/)
[![License](https://img.shields.io/pypi/l/opendart-client)](https://github.com/seokhoonj/opendart-client/blob/main/LICENSE)

[English](https://github.com/seokhoonj/opendart-client/blob/main/README.md) | **한국어**

한국 **OpenDART**(금융감독원 전자공시시스템)의 공시 데이터를 읽어옵니다.

기업개황과 기간별 공시 목록, 재무제표와 주요 재무지표, 배당·증자·감자, 최대주주·소액주주·
임원·직원 현황과 임원 보수, 합병·분할·영업양수도·자기주식 취득 같은 주요 결정, 지분공시(5%룰),
증권신고서까지 다룹니다.

## 1. 설치

```bash
pip install opendart-client
```

무료 API 키(40자리)는 <https://opendart.fss.or.kr> 에서 발급받으실 수 있습니다. 키는
`OpenDart(api_key=...)`, 환경변수 `OPENDART_API_KEY`, config 파일 순으로 찾습니다.

**config 파일 (모든 OS 공통, 권장)** — `~/.config/opendart-client/credentials.json` 파일을
만들고 아래를 넣으세요.

```json
{ "api_key": "..." }
```

**환경변수** — 셸에 따라 다릅니다. macOS·Linux(bash/zsh):

```sh
export OPENDART_API_KEY=...
```

Windows PowerShell은 `setx OPENDART_API_KEY "..."`(영구) 또는
`$env:OPENDART_API_KEY = "..."`(현재 세션)를 씁니다.

## 2. 빠른 시작

```python
from opendart_client import OpenDart

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
```

회사코드(`corp_code`)는 정식 이름·티커·초성(`ㅅㅅㅈㅈ`)·오타 어느 것으로도 찾을 수 있습니다
(`dart.resolver().resolve(...)`). 해당 자료가 없는 조회는 빈 결과로 옵니다.

반환은 `list[dict]`이라 pandas·polars 표(DataFrame)로 바로 만들 수 있습니다.

```python
import pandas as pd
import polars as pl

pd.DataFrame(rows)   # 또는 pl.DataFrame(rows)
```

## 3. API

**최상위 도우미** — 회사코드를 찾거나 전체 목록을 받습니다.

| 호출 | 하는 일 |
|---|---|
| `dart.corp_codes()` | 전체 회사의 회사코드 ↔ 이름/티커 목록 |
| `dart.resolver().resolve(query)` | 이름·티커·초성·오타로 회사 하나를 회사코드로 |
| `dart.resolver().search(query)` | 같은 조건으로 후보 목록 |

**`report_code`** — 정기보고서·재무정보 메서드가 공통으로 받는 기간 코드(기본값 `11011`).

| 코드 | 보고서 |
|---|---|
| `11011` | 사업보고서 (기본값) |
| `11012` | 반기보고서 |
| `11013` | 1분기보고서 |
| `11014` | 3분기보고서 |

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

## 4. 터미널

설치하면 `opendart` 명령이 등록됩니다(`python -m opendart_client`로도 실행). 키는 위
세 곳(인자·환경변수·config 파일) 중 하나에서 읽습니다.

```sh
opendart resolve 삼성전자                    # 이름·티커·초성·오타 -> 회사코드 (+후보)
opendart search  삼성전자 --begin 20260101   # 기간 내 공시 목록
opendart company 삼성전자                    # 기업개황
opendart finance 삼성전자 --year 2024        # 주요계정 요약 (매출·영업이익·순이익·자산/부채/자본)
```

주요 옵션:

| 옵션 | 적용 명령 | 설명 |
|---|---|---|
| `--api-key KEY` | 전체 | 키 직접 지정 (생략 시 환경변수·config 파일) |
| `--timeout SEC` | 전체 | 요청 제한 시간(초), 기본 `30` |
| `--json` | 전체 | 읽기 좋은 요약 대신 전체 결과를 JSON으로 |
| `--begin YYYYMMDD` / `--end YYYYMMDD` | `search` | 공시 접수일 구간 |
| `--limit N` | `search` | 표시 줄 수, 기본 `20` |
| `--all` | `search` | 첫 페이지만이 아니라 전체 페이지 조회 |
| `--year N` | `finance` | 사업연도, 기본은 최근 제출된 사업연도 |
| `--report CODE` | `finance` | `11011` 사업 · `11012` 반기 · `11013` 1분기 · `11014` 3분기 (기본 `11011`) |
| `--separate` | `finance` | 별도재무제표(OFS), 기본은 연결(CFS) |

`<회사>` 자리엔 이름·티커·초성·오타·8자리 회사코드 아무거나 넣으면 내부에서 회사코드로
바꿔 조회합니다. 각 명령은 기본이 읽기 좋은 요약이고, `--json`은 전체 결과를 냅니다.
전체 옵션은 `--help`로 확인하세요.

`resolve`는 회사코드·티커·이름 순으로 정렬해 보여주며, 비상장사는 티커 자리가 `------`입니다.

```
$ opendart resolve 삼성전자
00126380  005930  삼성전자
00252074  ------  삼성전자판매
00366997  ------  삼성전자로지텍
```

`finance`는 회사명·보고서와 함께 주요계정을 정렬해 보여줍니다(`--separate`로 별도재무제표).

```
$ opendart finance 삼성전자 --year 2024
삼성전자 (00126380)  2024 사업보고서  (CFS 연결)
매출액       300,870,903,000,000
영업이익      32,725,961,000,000
당기순이익    34,451,351,000,000
자산총계     514,531,948,000,000
부채총계     112,339,878,000,000
자본총계     402,192,070,000,000
```

## 5. AI 코딩 에이전트에서 사용

이 저장소는 Claude Code·Codex용 플러그인 마켓플레이스도 겸합니다 — `resolve`·`search`·
`company`·`finance`를 `opendart` 명령을 호출하는 스킬로 제공합니다. 먼저 위에서 패키지를
설치하고 API 키를 설정하세요.

### 5.1. Claude Code

```
/plugin marketplace add seokhoonj/opendart-client
/plugin install opendart@opendart-client
```

그런 다음 평범하게 물어보거나("삼성전자 회사코드 찾아줘", "삼성전자 최근 공시 보여줘"),
스킬을 직접 호출하세요 — `/opendart:resolve 삼성전자`, `/opendart:finance 삼성전자 --year 2024`.

### 5.2. Codex

```
codex plugin marketplace add seokhoonj/opendart-client
codex plugin add opendart@opendart-client
```

`resolve`·`search`·`company`·`finance` 스킬은 회사 이름·티커에 반응하며, `opendart <명령>
<회사>`로 직접 실행해도 됩니다.

플러그인 없이 쓰려면? 스킬을 스킬 디렉터리에 symlink해 bare 형식(`/resolve`)으로 부르세요:

```sh
ln -s "$PWD/plugins/opendart/skills/resolve" ~/.claude/skills/resolve
```

## 6. 라이선스

MIT © Seokhoon Joo
