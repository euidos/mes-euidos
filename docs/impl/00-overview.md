# MES 1차 구현 개요

설계 정본은 Atlas Whiteboard 카드 (`.atlas/board/cards/`, `board_get`으로 조회).
이 문서들은 그 결정을 구현 명세로 번역한 것 — **왜**는 카드에, **무엇을 정확히**는 여기에.
코드 배치는 vertical-slice 스킬 규칙을 따름 (슬라이스 = Frappe Module, use-case 폴더, catch-all 금지).

## 아키텍처

```
Frappe 사이트
├ erpnext          이 포크 (main). 수정하지 않음
└ mes_euidos (신규 앱) — 슬라이스 구조
    ├ lot/                엔진 슬라이스: LOT 발번·분기
    │   └ issue_lot/          get_or_create_lot + 테스트
    ├ inventory/          엔진 슬라이스: 재고 전표의 유일한 창구
    │   └ gateway/            post_production · post_transfer · post_scrap + 테스트
    ├ execution/          실행 현황 — 실적·불량·비가동·원료교체·작업종료 use-case들
    │   ├ page/execution/     Desk 페이지 (Vue 마운트)
    │   ├ submit_output/      api.py(transport) + submit_output.py(logic) + test
    │   ├ record_downtime/
    │   ├ change_material/
    │   └ close_work/
    ├ traceability/       추적
    │   ├ page/trace/
    │   └ trace_lot/          양방향 재귀 쿼리 + 회수 집계 + test
    ├ master_ui/          품목·BOM·설비 화면의 조회·저장 use-case
    │   └ page/item, page/bom, page/workstation
    ├ production_ui/      작업지시 화면
    │   └ page/work_order
    ├ stock_ui/           재고 조회 화면
    │   └ page/stock
    ├ quality/            불량 코드 마스터 (1차: DocType + 시드만)
    │   └ doctype/mes_defect_code, mes_defect_cause
    ├ settings/           MES Settings DocType
    ├ documents/          MES Document DocType + LOT 스냅샷 로직
    ├ hooks.py            wiring만 — 훅·fixtures가 슬라이스 안을 가리킴
    └ ARCHITECTURE.md     슬라이스 맵 (구조 변경 시 같은 커밋에서 갱신)
```

주: 정확한 슬라이스 이름·묶음은 구현 세션이 `/plan` 에서 확정 — 위는 기준선.
`mold/` 슬라이스는 1차 제외 (`use_mold` 꺼짐). 스위치 조회 지점만 남김.

## 불변 원칙 (카드에서 확정)

1. **업무 규칙은 DocType 훅에만.** api.py는 transport(권한·파싱·에러 경계)만. 어느 경로로
   들어와도 동일 동작 (decision-business-logic-placement)
2. **MES가 만드는 재고 전표는 `inventory/gateway` 경유만.** Stock Entry 직접 생성 금지.
   ERPNext 표준 문서(구매·외주·출하)는 건드리지 않음 (decision-inventory-gateway)
3. **LOT 발번은 `get_or_create_lot()` 한 함수** (decision-lot-issuer)
4. **화면은 전부 자체 Vue, Desk는 셸.** frappe-ui 미사용, Frappe 내장 번들러.
   기본 목록·리포트 빌더는 고객 사용자 미노출 (decision-ui-architecture, frontend-stack)
5. **ERPNext 코어·포크 수정 금지** — custom field·훅·페이지로만
6. **금형은 스위치.** `use_mold` 기본 꺼짐. 분기 지점 10곳에 스위치 조회 (decision-mold-usage-switch)
7. use-case 폴더에는 **테스트 필수** (vertical-slice 규칙)

## 1차 범위

화면 7: 품목 · BOM · 설비 · 작업지시 · 실행 현황 · 재고 조회 · LOT 추적 (spec-mvp-scope)
제외: 생산계획·검사·부적합·출하·입출고·실사·외주·대시보드·리포트·설정 화면·모바일·금형 화면
→ Desk 뒷문 또는 2차. 단 **훅·게이트웨이는 1차부터 완전하게** — 뒷문 입력도 같은 규칙을 탐.

## 구현 순서

1. 앱 생성 + settings/ (MES Settings) + 창고 6종 시드
2. custom field 일괄 (fixtures)
3. quality/·documents/ DocType
4. lot/ (get_or_create_lot) + 훅 등록
5. inventory/gateway
6. 화면 슬라이스 7개 (품목 → BOM → 설비 → 작업지시 → 실행 현황 → 재고 조회 → LOT 추적)

각 단계마다 `/plan` 선언 → 승인 → 구현 → 검증 (compileall + 그래프 리빌드 + 테스트).
