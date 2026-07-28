---
id: decision-business-logic-placement
type: decision
title: 업무 로직은 DocType 훅, API는 얇게
status: decided
created: 2026-07-27T12:22:44+00:00
updated: 2026-07-27T12:22:44+00:00
---

**연쇄 로직은 DocType 훅에. API 함수는 얇게.**

```
        ┌ 자체 화면 (Vue)     ┐
        ├ Desk 뒷문 수정      ┤ →  DocType 훅  →  검증 · LOT 분기 · 금형 타수 가산
        ├ 외부 연동 (향후)    ┤                    문서 스냅샷 · 재고 전표
        └ 데이터 보정·마이그레이션 ┘
```

| 층 | 책임 |
|---|---|
| Vue 화면 | 표시·입력 |
| `@frappe.whitelist()` API | 화면용 데이터 조립, 문서 저장 호출. **업무 규칙 없음** |
| **DocType 훅** (`validate` / `on_submit` 등) | **업무 규칙 전부** |

## Why

우리 설계의 연쇄 동작(LOT 분기, 금형 타수 가산, 문서 스냅샷, 재고 전표)이 API 함수 안에 있으면
그 함수를 거치지 않는 경로에서는 실행되지 않음. 훅에 두면 **어느 경로로 들어와도 동일하게 동작**함.

A-1(기본 목록 미노출)로 우회 입력 위험은 줄었지만 근거는 남음:
- 시스템 관리자가 Desk 뒷문에서 데이터를 고칠 때도 연쇄가 돌아야 함
- 설비 신호 수집·외부 ERP 연동이 붙으면 그 경로도 같은 로직을 타야 함
- 데이터 보정·마이그레이션 시 일관성

## Memory

관련 훅 지점: `validate`(저장 전 검증), `before_save`, `on_submit`(제출 시 전표·연쇄),
`on_cancel`(취소 시 되돌리기), `on_update_after_submit`.

구현 시 주의: LOT 발번은 한 함수(`get_or_create_lot`)로 모으기로 했고
(`[[decision-lot-issuer]]`), 그 함수를 훅에서 부르는 형태가 됨 — 발번 지점이 흩어지지 않도록.

금형 타수 가산은 `(양품 + 불량) ÷ total_cavity` (`[[decision-mold-shot-count]]`),
문서 스냅샷은 작업 종료 시 유효본 복사 (`[[decision-mes-document]]`) — 둘 다 훅에서 실행.
