---
id: decision-bom-structure
type: decision
title: 반제품 추적 = 다층 BOM
status: decided
created: 2026-07-27T01:44:21+00:00
updated: 2026-07-27T01:44:21+00:00
---

| 기준 | A. 단일 레벨 | **B. 다층 BOM** | C. v16 track_semi_finished_goods |
|---|---|---|---|
| 반제품 Item | 불필요 | 필요 | **필요** (operation의 `finished_good`) |
| 반제품 BOM | 없음 | 있음 | 없음 |
| 공정별 실적 추적 | 불가 | 가능 | 가능 |
| 반제품 재고 | 없음 | **건별 선택** | 생산건 내부 |
| 지시서 수 | 1장 | **건별 선택** | 1장 |
| 공정별 창고 체인 | 없음 | 없음 | 있음 |
| 검증 부담 | — | 10년 검증 | v16 신기능 |
| 외부 ERP 매핑 | — | 표준 개념 | ERPNext 고유 |

**채택: B.** A는 공정 단위 불량·재고를 못 봐서 탈락. C는 보류.

Work Order `use_multi_level_bom` 체크박스가 **생산 건마다** 실행 방식을 전환:

| 체크 | 자재 | 공정 | 지시서 | 반제품 재고 |
|---|---|---|---|---|
| OFF | 반제품을 재고에서 소비 | 상위 BOM 공정만 | 하위 WO 별도 | 잡힘 |
| ON | 하위 원자재까지 폭발 | 하위 BOM 공정까지 Job Card | 1장 | 안 잡힘 |

## Why

B가 상위집합. 구조는 한 번 잡고 "미리 쌓아두기 / 주문 단위 연속 생산"은 건별 선택이 됨.
C 전용 이점은 공정별 창고 체인뿐인데 현재 요구 없음.

## History

- 최초 제안은 "C 기본 + 공용 반제품만 B" 였고 근거는 "지시서 1장 + 공정 추적은 C만 된다" 였음.
  소스 확인 결과 **B + `use_multi_level_bom` 이 동일하게 가능** → 근거 소멸, B 단독으로 정정.

## Memory

```python
# work_order/services/operations.py:196 — 하위 BOM 공정까지 수집
def _collect_bom_operations(self):
    groups = []
    if self.doc.use_multi_level_bom:
        bom_tree = frappe.get_doc("BOM", self.doc.bom_no).get_tree_representation()
        for node in reversed(bom_tree.level_order_traversal()):
            if node.is_bom:
                groups.append((self._bom_operations(node.name), qty, True))
    groups.append((self._bom_operations(self.doc.bom_no), bom_qty, False))

# work_order/services/required_items.py:82 — 자재 폭발도 같은 플래그
item_dict = get_bom_items_as_dict(..., fetch_exploded=self.doc.use_multi_level_bom)
```

C 재검토 조건: 공정별 창고 분리(`set_operation_warehouses` — source/wip/fg 자동 체인) 요구 발생 시.
C 제약: `validate_semi_finished_goods()` 가 `is_final_finished_good` 을 **정확히 1행**으로 강제.

사출 기준 보충: 대개 원료→완제품 단일 레벨이라 다층이 항상 필요하진 않음. 인서트 사출·2차 가공
(도장·조립)이나 프레스 단발형 다공정에서 반제품 단계가 생김 — 그때 B 구조가 이미 있어야 함.
