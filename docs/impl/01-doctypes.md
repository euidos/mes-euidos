# DocType 명세

신규 3 + 기존 DocType custom field. 필드명은 전부 `mes_` 접두(custom field) 또는 신규 DocType 내 원명.

## 신규 1 — MES Settings (settings/, Single DocType)

| 필드 | 타입 | 기본 | 근거 카드 |
|---|---|---|---|
| `use_mold` | Check | **0** | decision-mold-usage-switch |
| `lot_split_on_mold_change` | Check | 1 | decision-lot-rule |
| `lot_split_on_material_batch` | Check | 1 | " |
| `lot_split_on_param_change` | Check | 1 | " |
| `lot_split_on_workstation` | Check | 1 | " |
| `lot_split_on_date` | Check | **0** | " |
| `lot_split_on_shift` | Check | **0** | " |
| `mold_life_action` | Select: 경고만\n차단 | 경고만 | decision-mold-shot-count |

주: `use_mold=0`이면 `lot_split_on_mold_change`는 무시됨 (읽는 쪽에서 `use_mold and flag`).

## 신규 2 — MES Defect Code / MES Defect Cause (quality/)

```
MES Defect Code:
  code        Data, unique, reqd     예: DF-01
  defect_name Data, reqd             예: 치수이탈
  category    Select: 치수\n외관\n기능\n조립\n기타
  is_standard Check (기본 제공분 표시)
  disabled    Check

MES Defect Cause:
  code        Data, unique, reqd     예: CS-01
  cause_name  Data, reqd             예: 금형 마모
  disabled    Check
```

시드(fixtures, is_standard=1): 치수이탈 / 표면 흠집 / 오염 / 변색 / 오조립 / 누락 / 파손 / 기타.
원인 시드: 금형 마모 / 조건 이탈 / 자재 불량 / 작업 실수 / 기타.
공정별 필터 없음 — 전체 목록 (decision-defect-codes, 문진 17-1 보류).

## 신규 3 — MES Document (documents/)

| 필드 | 타입 | 비고 |
|---|---|---|
| `doc_no` | Data, reqd | 문서번호. 같은 번호 + 새 개정 = 신규 레코드 |
| `doc_name` | Data, reqd | |
| `doc_type` | Select: 도면\n작업표준\n검사기준\n성형조건표\n포장사양 | |
| `item` | Link Item | 품목별 문서일 때 |
| `mold` | Link MES Mold | use_mold 켜짐일 때만 표시 |
| `revision` | Data, reqd | Rev.3 |
| `status` | Select: 유효\n폐기 | |
| `effective_date` | Date | |
| `file` | Attach | |

훅: 같은 `doc_no`로 새 레코드 저장 시 이전 유효본 자동 `폐기` (02-hooks.md #5).
1차: DocType + 훅만. 화면은 2차, 등록은 뒷문 (decision-mes-document).

## 신규 4 — MES Mold (1차 제외, 스키마만 예약)

decision-mold-doctype 참조. `use_mold` 켜는 고객 나올 때 구현.

## Custom Fields (fixtures로 배포)

### Batch — 조회 축 5개 (decision-lot-rule). 플래그와 무관하게 항상 기록

| 필드 | 타입 |
|---|---|
| `mes_production_date` | Date |
| `mes_workstation` | Link Workstation |
| `mes_shift` | Link Shift Type |
| `mes_mold` | Link MES Mold (1차: 필드만 만들고 빈 값) |
| `mes_work_order` | Link Work Order |
| `mes_origin_batch` | Link Batch — 유상사급 원 출고 배치 (decision-outsourcing-traceability) |
| `mes_origin_doc` | Data — 원 출고 문서 |
| `mes_supplier_lot` | Data — 도급 협력사 LOT (입고 시 수기) |
| `mes_concession` | Check — 특채 표시 (decision-disposition) |

### Workstation — 3개 (decision-workstation)

| 필드 | 타입 |
|---|---|
| `mes_machine_code` | Data, unique — 호기 `IJ03`. LOT 코드 세그먼트 |
| `mes_machine_type` | Select: 압착기\n사출\n프레스\n조립대\n검사기\n기타 — LOT 접두 결정 |
| `mes_tonnage` | Int |

LOT 접두 매핑은 lot/ 슬라이스 상수: 압착기→AP, 사출→IJ, 프레스→PR, 조립대→AS, 검사기→QC, 기타→ET.
(machine_type 값 추가 시 접두 상수도 같이 — decision-workstation Memory)

### Quality Inspection — 1개 (decision-inspection)

| 필드 | 타입 |
|---|---|
| `mes_inspection_point` | Select: 초물\n중물\n종물\n순회 — In Process일 때만 표시. 옵션은 사이트별 Customize 교체 허용 |

### Work Order — 1개 (use_mold 켜짐 전용)

| 필드 | 타입 |
|---|---|
| `mes_mold` | Link MES Mold — use_mold=0이면 미표시 |

### Job Card / Stock Entry Detail — 불량 기록

| DocType | 필드 | 타입 |
|---|---|---|
| Job Card | `mes_defect_rows` | Table (자식: MES Job Card Defect — defect_code Link, qty Float, cause Link nullable) |

## 창고 시드 (설치 시 생성, decision-warehouse-structure + stock-tail)

원자재 / 재공(WIP) / 완제품 / 불량 / 재생재 / 외주처(그룹) — 6종.
Company 기본값: default_wip_warehouse=재공, default_fg_warehouse=완제품, default_scrap_warehouse=재생재.

## Manufacturing Settings 설정값 (설치 시)

| 설정 | 값 | 근거 |
|---|---|---|
| `disable_capacity_planning` | 0 (켬) | decision-production-planning |
| `capacity_planning_for_days` | 90 | " |
| `allow_overtime` | 0 | spec-screen-workstation |
| `allow_production_on_holidays` | 0 | " |
| `allow_editing_of_items_and_quantities_in_work_order` | 0 | spec-screen-work-order |
