---
id: decision-workstation
type: decision
title: 설비 확장 + 금형 관계 + 사이클타임 위치
status: decided
created: 2026-07-27T04:01:22+00:00
updated: 2026-07-27T04:01:22+00:00
---

### Workstation 추가 필드 (custom field 3개)

| 필드 | 타입 | 용도 |
|---|---|---|
| `machine_code` | Data | 호기 번호 (`IJ03`). LOT 코드 세그먼트로 직접 사용 |
| `machine_type` | Select | 사출 / 프레스 / 후가공. LOT 접두(`IJ`/`PR`) 결정 |
| `tonnage` | Int | 형체력. 금형 `required_tonnage` 이상이어야 장착 가능 (검증) |

### 금형 ↔ 설비 관계를 어디에 저장하나

| 기준 | **A. 금형에만** | B. 설비에만 | C. 양쪽 |
|---|---|---|---|
| 저장 위치 | `MES Mold.current_workstation` | `Workstation.current_mold` | 둘 다 |
| 단일 출처 | O | O | **X — 어긋남 발생** |
| 1설비 = N금형 | 표현 가능 | 불가 | — |
| 역조회 | 설비→금형만 쿼리 필요 | 금형→설비만 쿼리 필요 | 불필요 |

**채택: A.** 이동하는 쪽(금형)이 관계를 소유. `Workstation.current_mold` 역방향 필드는 만들지 않음.

### 사이클타임을 어디에 두나

**BOM Operation.** Workstation에 두지 않음.

```
BOM (제품 A)
  operations
    1  사출  workstation: IJ03   time_in_mins: 0.42   batch_size: 4   fixed_time: 40
                                  └ 1 사이클 25초       └ 캐비티 수      └ 세팅시간
```

| 용어 | 뜻 | 저장 위치 |
|---|---|---|
| 사이클타임 | 1 shot 소요 시간 | BOM Operation `time_in_mins` |
| 개당 시간 | 사이클타임 ÷ 캐비티 | 계산값 |
| 세팅시간 | 금형 교체 시간 | BOM Operation `fixed_time` |
| 리드타임 | 주문→납품 총 소요 | 별개 개념. Item 구매 리드타임 |

## Why

사이클타임은 설비 속성이 아니라 **(제품 × 금형 × 설비) 조합의 속성** — 같은 3호기라도 A금형 25초,
B금형 40초. 설비 마스터에 값을 하나 두면 어느 제품 기준인지 말할 수 없게 됨.
BOM Operation 행 자체가 그 조합이라 여기 붙는 것이 정확하고, `batch_size` 가 캐비티 수 자리를
그대로 맡음(= `time_in_mins` 동안 `batch_size` 개 산출).

C(양방향 저장) 기각 이유는 `[[decision-lot-rule]]` 에서 원료 로트를 Batch에 복제하지 않은 것과 동일 —
같은 사실을 두 곳에 쓰면 어긋나는 날이 옴.

## Memory

**설비군(machine group)은 만들지 않음.** "300톤급 아무거나"로 배정하려면 ERPNext에 이미
`Workstation Type` 이 있고, `tonnage` 필드로 필터도 됨. 요구가 실제로 나오면 그때 `Workstation Type` 사용.

실제 사이클타임은 Job Card 실적에서 나오므로 표준 대비 편차 비교는 OEE 단계에서.
지금 별도 실측 필드를 두지 않음.

`machine_type` 이 LOT 접두를 결정하므로 값 추가 시 LOT 코드 규칙(`[[decision-lot-rule]]`)과 연동됨 —
새 유형을 넣을 때 접두 2자리를 함께 정해야 함.

관련: `[[decision-mold-doctype]]`(금형 필드), `[[decision-routing]]`(라우팅 템플릿이 operations를 공급).
