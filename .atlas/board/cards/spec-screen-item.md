---
id: spec-screen-item
type: note
title: 화면 설계 — 품목
status: decided
created: 2026-07-28T01:47:13+00:00
updated: 2026-07-28T01:47:13+00:00
---

`Item` 실측 필드 135개(입력 81개, 탭 7개) 중 **약 20개만 노출.**

### 목록

| 열 | 원본 |
|---|---|
| 품목코드 (정렬 기본) | `item_code` |
| 품목명 | `item_name` |
| 품목그룹 | `item_group` — 원자재/반제품/완제품/부자재 |
| 재고단위 | `stock_uom` |
| 현재고 (전 창고 합) | 집계 |
| 배치추적 ● / − | `has_batch_no` |
| 상태 사용/중지 | `disabled` |

**필터** — 품목그룹 · 검색어 · 배치추적 여부 · 중지 포함
**검색 범위** — 품목코드 · 품목명 · **고객 품번**(`customer_items.ref_code`)

### 상세 — 우측 드로어, 탭 4개

| 탭 | 필드 | 원본 |
|---|---|---|
| 기본 | 품목코드 · 품목명 · 품목그룹 · 재고단위 · 설명 · 사용여부 | `item_code` `item_name` `item_group` `stock_uom` `description` `disabled` |
| 재고·추적 | 재고품목 · **배치추적** · 배치 자동생성 · 안전재고 · 창고별 재주문점 · 평가방법 · **거점별 기본값** | `is_stock_item` `has_batch_no` `create_new_batch` `safety_stock` `reorder_levels` `valuation_method` `item_defaults` |
| 거래처 품번 | 고객별 품번 · 공급처별 품번 | `customer_items` `supplier_items` |
| 제조 | 기본 BOM(읽기전용) · 외주품 여부 · 검사 템플릿 | `default_bom` `is_sub_contracted_item` `quality_inspection_template` |

### 숨기는 것 (삭제 아님 — Desk 뒷문에서는 접근 가능)

변형(Variants) · 고정자산 · 이연수익/비용 · 세금 · 판매·구매 단가 · 최대 할인 ·
웹샵 · 드롭십 · 무역(원산지·관세) · **품목 이미지**

### 동작

| 버튼 | 결과 |
|---|---|
| `+ 등록` | 드로어 신규 |
| `복사` | 유사 품목 빠른 생성 (코드만 새로) |
| `사용 중지` | `disabled = 1`. **삭제 안 함** — 거래 이력 보존 |

### 검증

- 품목코드 중복 금지
- 품목그룹은 **말단 그룹만** (트리 중간 노드 금지)
- 배치추적은 재고 발생 후 끄기 불가 (ERPNext가 막음)
- 재고단위는 거래 발생 후 변경 불가

### 권한

| 역할 | 권한 |
|---|---|
| 전 사용자 | 조회 |
| 기준정보 관리자 | 등록·수정·중지 |

## Why

**재고 기본값을 품목그룹에서 상속하지 않고 품목마다 직접 입력** — 거점(창고)이 여러 곳인 구조에서는
그룹 상속이 오히려 불편함. 품목별 `item_defaults`(회사·창고별 기본값 자식 테이블)로 처리.
등록 부담은 `복사` 버튼과 Desk 뒷문 일괄 편집으로 완화.

**품목 이미지 미사용** — 현장 식별에 도움이 되지만 사진 등록·관리 부담이 실익을 넘음.

**고객 품번 검색 포함** — 고객이 자기 품번으로 문의하는 경우가 대부분이라 실무 빈도가 가장 높음.
자식 테이블 조회라 품목 수천 건에서 체감될 수 있으므로 구현 시 인덱스 확인 필요.

## Memory

품목 마스터 화면의 상세는 **드로어**(필드 위주). 재고 이력·변동 차트는 여기가 아니라
**재고 조회 화면**에서 품목 클릭 시 별도 화면 — `[[decision-ui-shell]]` 의 B 예외 기준 2
("이력·추세를 봐야 하는 대상은 별도 화면").

근거가 되는 확정 사항: 품목 구분은 `item_group` 트리만, 코드 수동 부여, 고객 품번은
`Item Customer Detail.ref_code` (`[[decision-item-coding]]`). 배치추적 범위는 추적 대상 자재만
(`[[decision-lot-rule]]`). 외주품 구분은 `is_sub_contracted_item` 플래그
(`[[decision-outsourcing-scope]]`).
