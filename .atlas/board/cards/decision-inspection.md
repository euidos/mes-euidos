---
id: decision-inspection
type: decision
title: 검사 = 3유형 + 시점 필드, LOT 기준, 품목별 강제
status: decided
created: 2026-07-28T06:10:50+00:00
updated: 2026-07-28T06:10:50+00:00
---

| 항목 | 결정 |
|---|---|
| 검사 유형 | ERPNext 기본 3종 — `Incoming`(수입) · `In Process`(공정) · `Outgoing`(출하) |
| 검사 시점 세분 | **custom field `검사 시점`** (Select) — 기본값 초물·중물·종물·순회 |
| 검사 강제 | **품목별** `inspection_required_before_purchase` / `_before_delivery` |
| 공정검사 대상 | **LOT(배치) 기준** + 작업표 참조도 함께 기록 |

### 실무 용어 ↔ ERPNext 매핑

| 실무 | 뜻 | ERPNext |
|---|---|---|
| 수입검사 | 입고 자재 확인 | `Incoming` |
| **초물검사** | 조건 세팅 후 첫 제품 | `In Process` + 시점=초물 |
| 중물·순회검사 | 생산 중 주기 확인 | `In Process` + 시점=중물/순회 |
| 종물검사 | 그 작업 마지막 제품 | `In Process` + 시점=종물 |
| 출하검사 | 납품 전 최종 | `Outgoing` |

## Why

**초물검사가 ERPNext에 자리가 없음** — 조건을 잡고 첫 개를 확인해야 그 뒤 수백~수만 개를 정상으로
판단할 수 있고, 초물 불합격이면 그 조건으로 만든 것이 전부 의심 대상이 됨. 필드 하나로 실무 용어를
담고 "초물 불합격률" 같은 지표를 뽑을 수 있게 함. 초물은 LOT 분기와도 맞물림(조건 변경 후 첫 검사).

**검사 강제는 품목별이 상위집합** — 전 품목에 켜면 전면 강제, 아무것도 안 켜면 강제 없음.
별개 안이 아니라 설정값 하나로 셋 다 표현됨. 초기 도입에서 전면 강제는 현장 반발이 큼.

**LOT 기준으로 붙이는 이유** — 추적 화면이 LOT 중심이라 검사 결과가 LOT에 붙어야
"이 LOT은 초물 합격, 중물 합격"이 한눈에 보임. `Quality Inspection.batch_no` 가 이미 있어 비용 0.

## Memory

`Quality Inspection` 구조 (확인): `inspection_type`(3종 고정) · `reference_type`
(Purchase Receipt · Subcontracting Receipt · Delivery Note · Stock Entry · **Job Card** 등) ·
`batch_no` · `sample_size` · `readings`(항목별 규격·측정치) · `status`(Accepted/Rejected/Cancelled) ·
`quality_inspection_template`. 제출 문서(`is_submittable: 1`).

**용어는 업종마다 다름** — 초물·중물·종물은 금속가공·사출에서 흔하지만, 전자 조립은 "초품/양산품",
다른 곳은 "첫 검사/정기 검사". 그래서 Select 옵션을 **Customize Form에서 사이트별로 교체** 가능하게
두고 도입 시 그 업체 용어로 갈아끼움 (코드 수정 없음).

**샘플링 계획은 ERPNext에 없음** — `sample_size` 숫자 필드만 있고 AQL 같은 계획 기능은 없음.
전수/샘플 여부와 샘플 수 결정은 업체 절차에 따름.

미결(문진): 검사 프로세스와 용어, 검사 단위(LOT/개별/작업표/시간 주기), 강제 대상 품목.
