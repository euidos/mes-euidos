---
id: decision-production-planning
type: decision
title: 생산계획·작업지시 구조 + Capacity Planning 켬
status: decided
created: 2026-07-27T07:18:22+00:00
updated: 2026-07-27T07:18:22+00:00
---

### 층 구조 — 무엇이 어느 주기로 생성되나

| 층 | DocType | 주기 | 단위 | 누가 |
|---|---|---|---|---|
| ① 수요 | Sales Order / Blanket Order | 수시 | 주문·약정 | 영업 |
| ② 생산계획 | **Production Plan** | 주 1회 (+변경) | 기간 (1주~1개월) | 생산관리 |
| ③ 작업지시 | **Work Order** | 계획 실행 시 | **금형 1세팅** (수 시간~수 일) | 계획에서 자동 |
| ④ 작업표 | **Job Card** | WO 생성 시 자동 | 공정 × 설비 | 자동 |
| ⑤ 실적 | Stock Entry + Batch | 교대마다·수시 | 등록 1회 | 현장 |

| 관계 | 비율 | 무엇이 끊는가 |
|---|---|---|
| 생산계획 → 작업지시 | 1 : N | 품목·금형이 다르면 별도 지시 |
| 작업지시 → 작업표 | 1 : N | 공정 수만큼 |
| 작업지시 → LOT | 1 : N | 조건 분기 (`[[decision-lot-rule]]`) |
| 작업표 → 실적 등록 | 1 : N | 교대마다 |

계획은 **필수 경로가 아님** — 급한 건·시험 생산·재작업은 계획을 건너뛰고 WO 직접 발행.

### 채택

| 항목 | 채택 | 기각 |
|---|---|---|
| WO 발행 | **Production Plan + 수동 병행** | 판매주문 1건 = WO 1건 (금형을 하루 세 번 갈게 됨) |
| 포캐스트 그릇 | **`Blanket Order`** (기간·수량 약정) + `Sales Order` (확정 지시) | 전용 DocType 신설 |
| 고객 파일 수신 | **업로드 폼 + 고객별 매핑 규칙** | EDI 직결 (요구 시) |
| Capacity Planning | **켬**, `capacity_planning_for_days` 90 | 끔 |
| 금형 중복 배정 | **경고** | 차단 / 미검증 |
| 동적 스케줄러 | **안 만듦 — 1단계(가시화+검증)만** | 자동 재배치 |

### 스케줄링 단계론

| 단계 | 무엇 | 결정 주체 | 판단 |
|---|---|---|---|
| **1. 가시화 + 검증** | 간트 읽기, 겹침·금형 충돌 경고 | 사람 | **지금 여기** |
| 2. 수동 리스케줄 | 간트에서 순서 변경 → 제약 검사 | 사람 | 가치/비용 최고. 후보 |
| 3. 규칙 기반 제안 | 같은 금형 묶기, 밝은 색 → 어두운 색 | 사람 (제안 참고) | 4단계 이후 |
| 4. 자동 최적화 (APS) | 시스템 | 시스템 | 맞춤 영역, 제외 |

## Why

**동적 스케줄러를 만들지 않는 이유 셋:**
1. 목적함수가 업체마다 다름 — 납기 준수 / 금형 교체 최소화 / 가동률 / 재고 최소가 서로 상충.
   사출엔 색상 순서 제약까지 붙음(흑색→백색은 퍼지 손실 수십 kg, 반대는 미미).
   목적함수가 다르면 자동화는 업체별 맞춤이 되어 제품 라인에 넣을 수 없음.
2. 계획이 자주 바뀌면 현장이 안 봄 — 아침 순서와 오후 순서가 다르면 반장이 준비한 금형·자재가
   헛일이 되고, 두 번 겪으면 종이로 돌아감. 현장이 원하는 건 "오늘 계획은 하루 안 바뀐다".
3. 제약 조건 최적화는 상용 APS 제품 영역. MES에 곁다리로 붙여 이길 수 없음.

**Capacity Planning을 켜는 이유**: 납기 회신 근거와 설비 부하 가시화. 끄는 건 나중에 되지만
꺼둔 기간의 스케줄 데이터는 소급 생성이 안 됨. 사출은 근무시간표가 단순(24시간 연속)하고
사이클타임이 안정적이라 계산이 현실과 잘 맞음 — 수작업 위주 공장은 반대.

## Memory

**Capacity Planning의 실제 동작과 한계** (소스 확인):

```python
# work_order/services/operations.py:118
def _validate_capacity_window(self, row, plan_days):
    if date_diff(row.planned_end_time, self.doc.planned_start_date) <= plan_days:
        return
    frappe.throw("Unable to find the time slot in the next {0} days for the operation {1}. ...",
                 CapacityError)
```

- 기본 `capacity_planning_for_days or 30`. 설비가 꽉 찼을 때뿐 아니라 **한 WO 자체가 그 기간을
  넘길 때도** 던짐 — 사이클타임 단위를 잘못 입력(분/초 혼동)하면 즉시 발생.
  메시지는 "일수를 늘리라"고 안내하지만 원인이 오입력이면 잘못된 대응이 됨
- `planned_start_time` / `planned_end_time` 은 **WO 제출 시 1회 계산되어 저장**.
  실적이 지연돼도 후속 Job Card가 자동으로 밀리지 않음
- 시스템이 하는 것은 겹침 **검증**뿐 (`job_card.py:343 validate_overlap_in_time_log`).
  재계획은 사람이 함 → "계획 수립 도구이지 동적 스케줄러가 아님"

**금형 중복 배정은 ERPNext가 모름** — 금형은 우리가 만든 개념(`[[decision-mold-doctype]]`).
WO 제출 시 "이 금형이 겹치는 기간에 다른 WO에 배정돼 있나" 쿼리 한 번으로 경고.

**Production Plan 주요 필드**: `get_items_from`(Sales Order / Material Request / 비우면 직접 입력),
`sales_orders`, `po_items`(만들 것), `sub_assembly_items`(BOM 전개 자동), `mr_items`(부족 자재 →
구매요청), `combine_items`(여러 주문의 같은 품목 합치기 — 사출에서 핵심), `ignore_existing_ordered_qty`,
`include_safety_stock`.

**색상·수지 필드는 지금 넣지 않음.** 3단계 제안 기능의 근거 데이터지만 품목의 **정적 속성**이라
나중에 추가해 소급 입력이 됨(품목 수만큼 행 채우면 끝). 되돌릴 수 없는 것은 그때만 존재하는 값
(어느 조·어느 금형)이지 마스터 속성이 아님 — 문진 항목으로만 등록.

**변환기와 스케줄러는 층이 다름**: 변환기는 ① 수요 층(고객 포캐스트 → 문서), 스케줄러는 ③④ 층.
변환기 설계에서 스케줄링을 고려할 필요 없음.
