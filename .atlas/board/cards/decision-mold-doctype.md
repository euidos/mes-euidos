---
id: decision-mold-doctype
type: decision
title: 금형 = 신규 MES Mold DocType + 필드
status: decided
created: 2026-07-27T03:47:48+00:00
updated: 2026-07-27T03:47:48+00:00
---

| 기준 | **A. 신규 `MES Mold`** | B. `Asset` 재사용 | C. `Workstation` 하위 |
|---|---|---|---|
| 고객 지급 금형 | 자연스러움 | **재무제표 왜곡** | 부자연 |
| 회계 결합 | 필요할 때만 링크 | 항상 강제 (감가상각·전표) | 없음 |
| 설비×금형 조합 기록 | 가능 | 가능 | **불가** (Job Card는 Workstation 1개) |
| 보전 기능 | 직접 설계 | Asset Maintenance 재사용 | — |
| 새 DocType | +1 | 0 | 0 |

**채택: A.**

### 필드

| 구분 | 필드 | 타입 | 용도 |
|---|---|---|---|
| 식별 | `mold_code` | Data | 금형번호. 수동 부여 |
| | `mold_name` | Data | |
| | `status` | Select | 사용중 / 보관 / 보전중 / 폐기 |
| 생산 계수 | `items` | Table | 행마다 `item` + `cavity` (패밀리 금형 대응) |
| | `total_cavity` | Int (계산) | `items` 캐비티 합계 = 1 shot 산출 수 |
| | `required_tonnage` | Int | 호기 매칭 제약 |
| 수명·보전 | `total_shots` | Int (읽기전용) | 누적 타수 |
| | `life_shots` | Int | 수명 타수 |
| | `maintenance_interval_shots` | Int | 보전 주기 타수 |
| | `last_maintenance_shots` | Int | 마지막 보전 시점 누적 타수 |
| 위치·소유 | `current_workstation` | Link → Workstation | 비면 보관 상태 |
| | `ownership` | Select | 자사 / 고객지급 |
| | `customer` | Link → Customer | 고객지급일 때 필수 |
| | `asset` | Link → Asset | **자사 + 감가상각 필요할 때만** |

## Why

`Asset`은 회계 자산 개념 — 등록하면 감가상각 스케줄·회계 전표·자산계정이 따라붙음.
사출 업계는 고객 지급 금형이 다수인데, 우리 돈으로 산 물건이 아니므로 자산 등록 자체가 틀린 표현.
B의 유일한 이점(Asset Maintenance 재사용)은 보전 요구가 나올 때 별도로 붙일 수 있지만,
B의 회계 결합은 나중에 떼어낼 수 없음 — 되돌릴 수 없는 쪽을 피함.

C는 Job Card가 Workstation을 하나만 가리키므로 "3호기에 A금형" 조합을 기록할 수 없음.
`품목 × 설비 × 금형` 세 축이 두 축으로 뭉개짐.

## Memory

**Asset 링크 방향 주의** (오해하기 쉬움):
- 자사 금형 + 감가상각 필요 → Asset 등록 후 링크
- **고객 지급(외부) 금형 → Asset 등록하지 않음.** `customer` 링크로 소유자만 기록

품목을 자식 테이블로 둔 이유: 패밀리 금형(한 금형에서 서로 다른 품목 동시 생산)이 사출·프레스에 실재.
1:1 금형은 행 1개일 뿐이라 단순한 경우에 손해 없음.

**뺀 것과 이유:**
- 이동 이력 테이블 — Job Card에 금형+호기가 매번 찍히므로 이력이 거기서 나옴. 중복 저장 회피
- 보전 이력 테이블 — 요구 발생 시 별도 DocType. 지금은 `last_maintenance_shots` 한 줄로 충분
- 제작처·제작일·제작비·치수·중량 — 어느 결정에도 안 쓰임. 단 **고객이 보관을 원할 수 있어
  업체 선택 항목으로 승격** (`[[table-tenant-options]]` 16번)
- 도면번호 — `MES Document` 마스터에서 다룸 (중복 방지)

금형이 마스터인 근거: `품목 × 설비 × 금형` 은 서로 독립적으로 바뀌는 세 축이고, 금형 축이 없으면
"같은 호기·같은 품목인데 이 기간만 불량률이 높다"(= 금형 마모)를 분해할 수 없음.
또 금형은 자재가 아니라 **자원** — 소모되지 않고 타수로 닳으며, 설비 사이를 옮겨 다님.
캐비티 수는 생산량·표준시간 계산의 계수로, 다른 마스터가 대신 공급할 수 없음.

후속: 타수 카운트 지점과 수명 도달 시 동작은 `[[decision-mold-shot-count]]`.
