---
id: decision-item-coding
type: decision
title: 품목 구분·코드·고객 품번 매칭
status: decided
created: 2026-07-27T01:44:21+00:00
updated: 2026-07-27T01:44:21+00:00
---

| 항목 | 채택 | 기각 | 비용 |
|---|---|---|---|
| 품목 구분 | **`item_group` 트리** (원자재·반제품·완제품·부자재) | `mes_managed` 플래그 / 둘 다 | custom field 0 |
| item_code | **수동 부여** | 자동 네이밍 시리즈 | 0 |
| 고객 품번 매칭 | **Item > Customer Items `ref_code`** | 커스텀 매핑 테이블 | 네이티브, 개발 0 |
| 공급처 품번 | **Item > Supplier Items `supplier_part_no`** | 동상 | 네이티브 |

MES 화면 필터 = `item_group in (원자재, 반제품, 완제품, 부자재)`.

## Why

BOM·생산 로직이 어차피 품목 종류로 갈림 → 그룹이 이미 그 역할. 플래그는 중복.
고객 품번은 행으로 N개 추가 가능 → 납품 문서·라벨 자동 표시, 고객 바코드 스캔 시 내부 품목 역조회.

## Memory

DocType: 고객 매핑은 `Item Customer Detail` 자식 테이블(필드 `ref_code`),
공급처는 `Item Supplier`(필드 `supplier_part_no`).

custom field 현재 0개. 도면번호 등 요구 생기면 추가 — 그때도 래퍼 DocType은 만들지 않음
(`[[decision-scope-integration]]` Q4).

사출 기준 재검토 결과 이 결정들은 영향 없음 — 품번 체계는 공정 종류와 독립.
