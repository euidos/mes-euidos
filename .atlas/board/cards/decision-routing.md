---
id: decision-routing
type: decision
title: 공정 순서 = Routing 템플릿 재사용
status: decided
created: 2026-07-27T01:44:21+00:00
updated: 2026-07-27T01:44:21+00:00
---

| 기준 | A. BOM마다 공정 직접 입력 | **B. Routing 템플릿 재사용** |
|---|---|---|
| 신규 BOM 등록 | 매번 전 공정 재입력 | 템플릿 적용 1회 |
| 표준시간 일관성 | 입력자마다 다름 | 템플릿에서 통일 |
| 공정 순서 검증 | 없음 | `set_routing_id()` 가 역순 차단 |
| 구버전 봉인 | 불가 | `disabled` 플래그 |
| 공정이 제품마다 다를 때 | 유리 | 템플릿이 방해 |
| 적합 산업 | 금형·특수기계·시제품 (job shop) | **사출·프레스·PCB·부품 양산** |

**채택: B.** 배타 아님 — 특수 제품은 BOM에서 `routing` 비우고 operations 직접 입력하면 A 동작. 코드 분기 0.

## Why

사출·프레스는 공정 흐름이 소수 표준 패턴(건조→성형→후가공→검사→포장)인데 품번은 수백 개.
A면 같은 흐름을 수백 번 재입력 → 오타·공정 누락·표준시간 편차.

## Memory

**복사 시멘틱 주의** — 템플릿 수정이 기존 BOM에 소급 반영되지 않음:

```python
# bom.py:923
def set_routing_operations(self):
    if self.routing and self.with_operations and not self.operations:
        self.get_routing()
```

`not self.operations` 조건 때문에 **BOM 생성 시 1회 복사**뿐. 표준시간 개정 시 기존 BOM은
새 버전 재발행 필요 (A도 동일 제약이라 B의 상대 우위는 유지되나, "템플릿만 고치면 전파된다"는
근거는 성립하지 않음 — 최초 논의에서 이 점을 잘못 말했다가 소스 확인 후 정정).

복사되는 필드: `_get_routing_fields()` = sequence_id, operation, workstation, workstation_type,
description, time_in_mins, batch_size, operating_cost, idx, hour_rate, set_cost_based_on_bom_qty, fixed_time.

사출 관련: 다캐비티는 BOM Operation `batch_size` 로 1 사이클 산출 수 모델링 (미결정, 예고만).
