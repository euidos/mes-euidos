---
id: decision-master-list
type: decision
title: 마스터 13개 확정 (금형 복원)
status: decided
created: 2026-07-27T01:44:21+00:00
updated: 2026-07-27T01:44:21+00:00
---

| # | 마스터 | DocType | MES 관리 | 비고 |
|---|---|---|---|---|
| 1 | 품목 | Item | 관리 | |
| 2 | BOM | BOM | 관리 | 다층 |
| 3 | 공정 | Operation | 관리 | |
| 4 | 라우팅 | Routing | 관리 | 템플릿 |
| 5 | 창고·위치 | Warehouse | 관리 | |
| 6 | 설비 | Workstation | 관리 +확장 | 호기 |
| 7 | 작업자 | Employee | 관리 +확장 | |
| 8 | 품질 검사기준 | Quality Inspection Template | 관리 +SPC | |
| 9 | 거래처 | Customer / Supplier | 참조 | Q3 여파 |
| 10 | 문서 | **MES Document** 신규 | 관리 | 도면·작업표준 |
| 11 | LOT 코드규칙 | 설정 / Batch series | 관리 | |
| 12 | 근무조 | Shift Type | 관리 | LOT 분기축 |
| 13 | **금형** | **MES Mold** 신규 | 관리 | 캐비티·타수·수명·호기매칭·소유 |

**13개 확정.** 제외: 공구(금형 외) — 요구 생기면 추가.

## Why

금형은 하네스 기준으로 한 번 제외했다가 사출·프레스를 검토하며 복원.
캐비티 수가 생산량·표준시간의 기준이고, 금형 교체가 품질·LOT 분기점이라
금형 축이 없으면 "왜 이 로트만 불량률이 높은가"를 분해할 수 없음.

## History

- 2026-07-25 12개 확정, 공구·금형 제외 (하네스 기준, 범용성 없다고 판단) — `superseded`
- 2026-07-27 사출·프레스 검토 중 금형 복원, 13개
- 2026-07-28 적용 업종 정정: 범용 MES, 우선 검증은 하네스. 금형은 하네스에서도 유효
  (압착기 애플리케이터 = 금형, 타수 수명 관리 대상)

## Memory

MES Mold 필드 요구 (미설계):
- `cavity_count` — 1 shot 산출 수. BOM Operation `batch_size` 와 연결됨
- `shot_count` 누적 + `shot_life` — 수명·보전 주기·교체 예고
- 호기 매칭 (톤수 제약) — Workstation link 또는 workstation_type
- 소유 구분 — 고객 지급 금형이 흔해 자산/지급 구분 필요

근무조(Shift Type)도 한 번 뺐다가 복원됨(2026-07-25): ERPNext 기본 제공이라 비용 0.
이후 `[[decision-lot-rule]]` 에서 LOT 코드의 조 세그먼트 근거가 되어 필수로 승격.
