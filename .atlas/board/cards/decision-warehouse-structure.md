---
id: decision-warehouse-structure
type: decision
title: 창고 5개 + WIP 경유 ON + 재생재 회수 ON
status: decided
created: 2026-07-27T04:17:35+00:00
updated: 2026-07-27T04:17:35+00:00
---

| 창고 | 경유 | 무엇이 있나 | 끄는 방법 |
|---|---|---|---|
| 원자재 | 항상 | 레진·마스터배치·코일·부자재 | — |
| **재공(WIP)** | **ON** | 라인에 투입된 자재 | Work Order `skip_transfer` |
| 완제품 | 항상 | 검사 통과분 | — |
| 불량 | 항상 | 판정 대기·불합격품 | — (선택 아님) |
| **재생재** | **ON** | 분쇄한 스프루·런너 | 재생재 품목 미등록 |

**창고 5개는 처음부터 전부 생성.** 스위치는 "만들까"가 아니라 "경유할까".

| | 나중에 끄기 | 나중에 켜기 |
|---|---|---|
| WIP 경유 | 쉬움 (`skip_transfer`) | 쉬움 — 켠 시점부터 기록 |
| 재생재 품목 | 쉬움 (품목 미등록) | 쉬움 — 과거 데이터만 없음 |
| **창고 구조 자체** | — | **어려움 — 과거 재고 이관 필요** |

### 재생재는 네이티브 처리 (개발 0)

```python
# bom.py:984
def has_scrap_items(self):
    return any(d.get("secondary_item_type") == "Scrap" ... for d in self.get("secondary_items"))
```

BOM `secondary_items` 에 재생재를 `Scrap` 유형으로 등록 → 실적 등록 시 Work Order `scrap_warehouse` 로
자동 입고. "제품 100개 + 재생재 3kg 산출" 이 한 전표로 기록됨.

**수율 손실과 구분**: 회수해서 다시 쓰는 것 = `secondary_items`(Scrap), 태우거나 사라지는 것 =
BOM `process_loss_percentage`. 다른 필드임.

## Why

창고를 안 만드는 것과 안 경유하는 것은 비용이 다름 — 빈 창고는 비용 0, 나중에 쪼개는 것은 재고 이관 작업.
그래서 구조는 최대로 만들고 운용만 끔.

WIP를 기본 ON으로 두는 이유: 사출은 호퍼에 레진 며칠분을 부어놓아 **라인 재고가 실재**함.
`skip_transfer` 면 그 물량이 장부상 원자재 창고에 남아 있어 실사 때마다 차이가 남.
조립처럼 그때그때 꺼내 쓰는 공정은 차이가 작으므로 업체 판단(문진).

불량 창고가 선택 항목이 아닌 이유: 양품과 같은 창고에 두면 판정 전 물건이 출하 가능 상태가 됨.

## Memory

**창고는 Stock 모듈, 공정은 Manufacturing 모듈로 분리돼 있음.** Manufacturing은 창고를 정의하지 않고
참조만 하므로, 창고를 어떻게 쪼개도 공정 설계는 바뀌지 않음. 접점은 세 곳:

```python
# work_order.py:567 — 기본값 출처는 Manufacturing Settings 가 아니라 Company
def set_default_warehouse(self):
    if not self.wip_warehouse and not self.skip_transfer:
        self.wip_warehouse = frappe.get_cached_value("Company", self.company, "default_wip_warehouse")
    if not self.fg_warehouse:
        self.fg_warehouse = frappe.get_cached_value("Company", self.company, "default_fg_warehouse")
```

1. `Company` — `default_wip_warehouse` `default_fg_warehouse` `default_scrap_warehouse`
2. `Work Order` — `source_warehouse` `wip_warehouse` `fg_warehouse` `scrap_warehouse` (건별 덮어쓰기)
3. `BOM Operation` — 공정별 창고 체인. `track_semi_finished_goods` 를 켤 때만 동작하며
   우리는 안 씀 (`[[decision-bom-structure]]`)

기본 창고가 Company에 있다는 사실은 문진 14번(배포 모델)과 맞물림 — 한 사이트에 여러 공장이면
Company별로 기본 창고가 갈리므로 다중 회사 구성이 자연히 지원됨.

재생재를 별도 품목으로 두는 이유: 물성 클레임이 신재/재생재 혼합률로 귀결되는 일이 잦음.
품목이 없으면 투입 비율이 기록되지 않아 원인 추적이 끊기고, 재료비도 실제보다 높게 잡힘.
