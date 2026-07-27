# OpenDartClient

[English](https://github.com/seokhoonj/opendartclient/blob/main/README.md)

한국 **OpenDART**(금융감독원 전자공시시스템) API를 위한 깔끔한 타입드 파이썬 클라이언트.
미국 SEC EDGAR에 해당하는 그 전자공시죠.

의존성 0개, 동기(sync), `dict` / `list[dict]` 그대로 반환 — DataFrame은 원하는 대로.

## 설치

```bash
pip install opendartclient
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

# DataFrame이 필요하면 (선택 extra)
from opendartclient import to_pandas
to_pandas(rows)
```

## 특징

- **OpenDART 85개 엔드포인트 전부** — 공시정보 · 정기보고서 · 재무정보 · 지분공시 ·
  주요사항보고서 · 증권신고서 6그룹을, **읽히는 메서드명**으로
  (`dart.event.convertible_bond(...)`, `cvbdIsDecsn` 아님).
- **회사 리졸버** — 이름 / 티커 / 초성(`ㅅㅅㅈㅈ`) / 오타 → `corp_code`.
- **런타임 의존성 0개** — 표준 라이브러리만. `pandas` · `polars`는 선택 extra
  (`pip install 'opendartclient[pandas]'`).
- **완전 타입드**, `py.typed` 동봉. 닫힌 어휘는 `Literal`이라 잘못된 코드는 API가
  아니라 타입체커가 잡음.
- **raw 반환** — `list[dict]`(flat) · `dict[str, list[dict]]`(grouped) · `bytes`(zip
  엔드포인트). `status 013`(데이터 없음)은 빈 결과, 그 외 에러는 타입드 `DartError`.

## 라이선스

MIT © Seokhoon Joo
