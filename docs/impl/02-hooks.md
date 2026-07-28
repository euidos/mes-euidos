# 훅 명세 — 업무 규칙의 유일한 자리

`hooks.py` `doc_events` 로 등록, 구현체는 각 슬라이스 안 (wiring은 슬라이스 내부를 가리켜도 됨 — 문자열 경로는 API임, 이동 시 vertical-slice 체크리스트).

## #1 LOT 발번 — lot/issue_lot

```python
def get_or_create_lot(work_order, ctx) -> str:
    """ctx = {date, workstation, shift, material_batch, param_rev, mold}
    켜진 lot_split_* 플래그의 값만 모아 키 구성. 키가 바뀌면 새 Batch 발번.
    코드: {YYMMDD}-{접두+호기2자리}-{순번3자리}  예 260801-IJ03-001
    - YYMMDD = WO 시작일 (일자 분기 OFF이므로 날짜 바뀌어도 유지)
    - 순번 = 같은 (일자,호기) 안 분기 순번
    발번 시 Batch custom field 항상 기록: production_date·workstation·shift·work_order
    (+mold if use_mold). shift는 Shift Type 시각과 현재 시각으로 자동 판정,
    자정 넘김은 근무 시작일 기준 (decision-operator-shift)."""
```

- `Item.create_new_batch` 자동생성은 MES 관리 품목에서 끔 — WO 제출 시 ERPNext `make_batch` 가
  아니라 첫 실적 등록 시 이 함수가 발번 (decision-lot-issuer)
- 호출처: execution use-case들 + Work Order 훅. **다른 곳에서 Batch 직접 생성 금지**

## #2 Work Order 훅

| 이벤트 | 로직 |
|---|---|
| `validate` | use_mold=1일 때: `mes_mold` 의 기간 겹침 검사 → **경고** (frappe.msgprint, 차단 아님) |
| `on_submit` | 자동 Batch 생성 억제 확인 |

## #3 Job Card 훅

| 이벤트 | 로직 |
|---|---|
| `validate` | 불량 행의 defect_code 필수, qty > 0 |
| `on_update`(실적 추가 시) | use_mold=1: 타수 가산 `(양품+불량) ÷ total_cavity` + 보정 타수. 수명·보전 도달 시 경고 (mold_life_action=경고만) |

## #4 작업 종료 — execution/close_work (훅 아님, use-case 로직이 게이트웨이 호출)

```
close_work(work_order):
  1. 유효 문서 스냅샷 → Batch에 기록 (documents/ 로직 호출)   ← #5와 연동
  2. inventory.gateway.post_production(
       consume=[(레진배치, qty)...],   ← WIP 창고에서
       produce=(item, qty, batch),     ← 완제품 창고로
       scrap=[(재생재, qty)])          ← 재생재 창고로
  3. Job Card·WO 상태 갱신
```

## #5 MES Document 훅 — documents/

| 이벤트 | 로직 |
|---|---|
| `on_update` | 같은 `doc_no` 의 다른 유효본을 자동 `폐기` (유효본은 항상 1개) |

스냅샷: 작업 종료 시점의 유효 문서(item 매칭)를 Batch 자식 테이블로 복사. 작업자 입력 0
(decision-mes-document).

## #6 불량 → 판정 대기 — quality/ (2차에 화면, 훅은 1차부터)

| 이벤트 | 로직 |
|---|---|
| Job Card 불량 행 저장 시 | 불량 수량을 불량 창고로 이동(gateway.post_transfer) + 판정 대기 레코드 생성 (decision-disposition: 자동 생성) |

1차에서 판정 처리는 뒷문. 판정 대기 DocType은 기존 `defect_disposition` 스켈레톤 재정의.

## #7 Employee 훅 (경량)

| 이벤트 | 로직 |
|---|---|
| 상태 → 퇴사 | 연결된 User 계정 비활성화 |

## 금지 사항

- 훅 안에서 Stock Entry 직접 생성 금지 → 반드시 inventory/gateway
- 훅 밖(api.py·화면)에 업무 규칙 금지
- `use_mold` 분기는 훅 첫 줄에서 조용히 return — 화면은 설정을 읽어 요소 미렌더
