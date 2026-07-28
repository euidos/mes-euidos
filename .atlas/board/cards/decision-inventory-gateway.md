---
id: decision-inventory-gateway
type: decision
title: 재고 posting 격리 = inventory_gateway 모듈
status: decided
created: 2026-07-28T07:54:07+00:00
updated: 2026-07-28T07:54:07+00:00
---

**Q3 방침("재고 posting 한 곳 격리")의 구현 설계.**

```
mes_euidos/inventory_gateway.py     ← 유일한 재고 창구

def post_production(...)     # 작업 종료: 자재 소비 + 완제품 입고 + 재생재
def post_transfer(...)       # WIP 이동 · 불량 창고 · 판정 복귀
def post_scrap(...)          # 폐기

규칙: MES 코드 어디서도 Stock Entry를 직접 만들지 않는다. 반드시 이 모듈을 거친다.
```

| 재고 이동 지점 | 게이트웨이 경유 |
|---|---|
| 작업 종료 (제조 전표) | **O** |
| WIP 이동 | **O** |
| 불량 창고 이동·판정 | **O** |
| 폐기·재생재 | **O** |
| 외주 출고·입고 (Subcontracting) | X — ERPNext 표준 문서 |
| 구매 입고·출하 (Purchase Receipt / Delivery Note) | X — 표준 문서 |

**채택: A — MES가 만드는 전표만 격리.** ERPNext 표준 문서는 건드리지 않음.

## Why

격리 목적: 자체 ERP가 있는 공장에서 MES는 생산 실행만 하고 재고·회계는 그쪽이 반영.
그때 이 모듈 안에서 "ERPNext에 쓰는 대신 외부 API 호출 + 로컬은 기록만"으로 바꾸면
바깥 코드는 손대지 않음.

B(표준 문서까지 훅으로 가로챔)를 기각한 이유: 자체 ERP가 있는 공장이라면 구매·판매·외주 정산은
**애초에 그쪽 ERP에서 일어나고 ERPNext에 입력 자체를 안 함.** MES가 교체해야 하는 것은 생산이
만드는 재고 변동뿐. 표준 흐름 개입은 업그레이드마다 깨지는 유지비만 남김.

## Memory

DocType 훅(`[[decision-business-logic-placement]]`)과의 관계: 훅은 검증·LOT 분기·타수 등
**업무 규칙**의 자리, 게이트웨이는 **재고 전표 생성**의 자리. 훅 안에서 재고를 움직일 일이 있으면
게이트웨이 함수를 호출하는 구조 — 두 결정이 충돌하지 않음.

외부 ERP 연동 시나리오: `MES Settings` 에 연동 모드가 생기면 게이트웨이가 분기.
전표 대신 인터페이스 테이블 기록 → 외부 ERP 배치 전송. 이 부분은 실제 연동 건이 나올 때 설계.
