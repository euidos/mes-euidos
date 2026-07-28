---
id: decision-lot-issuer
type: decision
title: LOT 발번 = 함수 1개 + 설정 플래그
status: decided
created: 2026-07-27T01:44:21+00:00
updated: 2026-07-27T03:21:00+00:00
---

| 기준 | A. WO를 일 단위 분할 | **B. WO 계획단위 유지, 발번 함수 1개** | C. 설정으로 둘 다 |
|---|---|---|---|
| 개발량 | 0 (기본 동작) | 함수 1개 | 분기 2벌 유지 |
| 금형 세팅 주기 정합 | 어긋남 | 맞음 | — |
| 자재 예약·투입 | 하루치씩 파편화 | WO 단위 유지 | — |
| 분기 규칙 변경 | 불가 | **설정 플래그** | 설정 |
| WO ↔ Batch | 1:1 강제 | 1:N | 선택 |

**채택: B.**

```python
def get_or_create_lot(work_order, ctx):
    """ctx = {date, workstation, shift, mold, material_batch, param_rev}
    켜진 플래그의 값만 모아 LOT 키 구성. 키가 바뀌면 새 LOT 발번."""
```

**규칙 = 키 구성 요소 선택**, 그뿐. 코드 분기 없음. 조 단위가 필요한 공장이 오면
`lot_split_on_shift` 를 켜면 그 시점부터 쪼개짐 (`[[table-tenant-options]]` 1번).

## Why

WO = 계획 단위(금형 1세팅), Batch = 품질 추적 단위. 원래 주기가 다른 두 개념을 1:1로 묶을 이유 없음.
A는 개발량 0이지만 WO 경계가 금형 교체 스케줄과 어긋나고 레진 예약이 하루치씩 끊김.
C는 설정 항목 하나가 곧 분기 두 벌의 유지 비용.

## Memory

구현 지점 (미착수):
- `Item.create_new_batch` 자동생성 OFF — ERPNext 기본은 WO 제출 시 Batch 1개(`work_order.py` → `make_batch`)
- 실적 등록 진입점에서 `get_or_create_lot()` 1회 호출
- `[[decision-lot-rule]]` 의 Batch custom field 5개를 그 시점에 채움 — **플래그와 무관하게 항상**

발번을 한 함수로 모으는 이유: 규칙 교체가 그 함수 안에서 끝남. 발번이 여러 진입점에 흩어지면
나중에 분기 규칙을 못 바꿈 — 되돌릴 수 없는 세 가지 중 하나(`[[table-tenant-options]]` Memory).
