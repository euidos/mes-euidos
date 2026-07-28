---
id: decision-scope-integration
type: decision
title: 기반 4결정 — 대상·UI·ERPNext 연동·마스터 소유
status: decided
created: 2026-07-27T01:44:21+00:00
updated: 2026-07-27T01:44:21+00:00
---

| # | 결정 | 채택 | 기각 | 이유 한 줄 |
|---|---|---|---|---|
| Q1 | 개발 대상 | **제품 라인 `mes_demo` (Desk 네이티브)** | 천일 Vue SPA 라인 | 두 라인 안 섞음 |
| Q2 | UI 패러다임 | **하이브리드** — 마스터·문서는 Desk 폼, 현장 실행만 커스텀 page | 전면 커스텀 UI | 폼 권한·필터·감사로그 재구현 회피 |
| Q3 | ERPNext 연동 깊이 | **트랜잭션 실사용 + 재고 posting 한 곳 격리** | 마스터만 참조 / 전면 결합 | 외부 ERP 있으면 그 지점만 교체 |
| Q4 | 마스터 소유 | **ERPNext DocType 재사용, 부족분만 custom field** | MES 전용 래퍼 DocType | 래퍼 = 이중 관리 |

## Why

Q3이 뿌리. 공장이 자체 ERP를 쓰든 안 쓰든 대응하려면 트랜잭션을 실제로 쓰되
재고 posting 지점이 한 모듈에 모여 있어야 함 — 연동 시 교체 범위가 거기서 끝남.
Q3 때문에 MES/ERP 경계가 흐려지므로 거래처(Customer/Supplier)도 마스터에 포함됨.

## Memory

**적용 업종: 범용 MES.** 우선 검증 대상은 **와이어하네스**이고, 사출·프레스는 나중에 설계를
뒤집지 않으려고 선제 반영한 것 (2026-07-28 정정 — 그 전까지 "대상 공정 = 사출·프레스"로
잘못 표기돼 있었음).

사출·프레스 기준 검토가 금형 마스터 복원(`[[decision-master-list]]`)과 LOT 단위 결정
(`[[decision-lot-rule]]`)을 낳았고, 두 결정 모두 하네스에도 유효함 —
하네스는 압착기 애플리케이터(다이스)가 금형에 해당하고 타수 수명·교체 관리를 하며,
`total_cavity = 1` 이면 계수 계산이 그대로 성립.

Q1 배경: 제품 라인은 Frappe page/workspace 기반 Desk 앱, 천일테크윈 버전은 Vue SPA로 별개.
앱명은 `euidos_mes` → `mes_demo` 로 리네임됨(커밋 8961856, 앱명 = repo명 규칙).
