# Use-case / transport 명세

각 use-case = 폴더 (api.py transport + 로직 파일 + 테스트). api.py는 `@frappe.whitelist()` +
권한·파싱·에러 경계만. 반환은 화면이 바로 쓸 모양으로.

## execution/ — 실행 현황 화면의 쓰기 경로

| use-case | 시그니처 (logic) | 하는 일 |
|---|---|---|
| `submit_output` | `(workstation, qty_ok, defects: [{code, qty}], operator=None)` | 현재 Job Card에 실적 행 추가. operator 기본 = 로그인 사용자의 Employee. 불량 행 → #6 훅 연쇄 |
| `record_downtime` | `(workstation, action: start\|stop, reason=None)` | 비가동 시작·종료. 시각은 서버 시각 |
| `change_material` | `(workstation, new_batch, qty_before)` | 현 LOT 마감(qty_before 기록) → `get_or_create_lot` 재호출 (material_batch 갱신) |
| `report_param_change` | `(workstation, note)` | 조건 변경 신고 → 새 LOT |
| `change_mold` | `(workstation, new_mold, qty_before)` | use_mold=1 전용. 타수 확정 + 금형 위치 갱신 + 새 LOT |
| `close_work` | `(work_order, final_qty)` | 02-hooks #4 흐름. 문서 스냅샷 + post_production |
| `get_floor_state` | `()` → 설비 카드 목록 | 설비별: 현 WO·품목·진행률·현 LOT·비가동 여부 |

## traceability/trace_lot

| 함수 | 내용 |
|---|---|
| `trace(batch_or_item, direction: up\|down, depth=5)` | 재귀. up=소비 배치(Stock Entry Detail), down=산출·출하(Delivery Note). `mes_origin_batch`·`mes_supplier_lot` 링크 따라감 |
| `recall_summary(batch)` | down 전개 후 집계: 총량·고객별 수량·재고 잔량. 엑셀 내보내기용 rows 반환 |

깊이 상한 5 + 방문 집합으로 순환 차단. `batch_no` 인덱스 확인.

## master_ui/ — 조회·저장 (업무 규칙 없음, ERPNext 문서 저장 호출만)

| use-case | 내용 |
|---|---|
| `list_items` / `save_item` | 노출 필드는 04-screens 품목 탭 구성. 검색은 코드·품명·`customer_items.ref_code` |
| `list_boms` / `get_bom_detail` / `new_bom_version` | 활성만 목록. 상세는 탭 데이터(자재·공정·부산물·구조·이전버전). 구조 탭은 지연 로딩(한 단계) |
| `list_workstations` / `save_workstation` | 계획 기준(근무시간표·휴일)은 읽기 전용 반환 |

## production_ui/

| use-case | 내용 |
|---|---|
| `list_work_orders` | 필터: 상태·품목·설비·기간·지연만 |
| `get_wo_detail` | 탭: 자재(소요·투입·잔여)·공정(Job Card별)·LOT(발번 목록)·진행(누적 곡선 데이터) |
| `create_work_order` | 기본 BOM 자동, `use_multi_level_bom` 기본 1, 건별 해제. Capacity 오류(CapacityError)는 사용자 메시지로 변환 |
| `wo_action` | start / stop / complete / cancel |

## stock_ui/

| use-case | 내용 |
|---|---|
| `stock_overview` | Bin 집계: actual·reserved·ordered·projected + 안전재고 플래그 |
| `item_stock_detail` | 창고별 잔량·LOT별 잔량(Batch 필드 포함)·이동 이력(SLE)·기간별 잔량 추이 |

## 공통 규약

- 날짜는 ISO 문자열, 수량은 float, 화면 표기 규약(단위·상태 라벨)은 프론트 상수
- 에러: `frappe.throw` 메시지는 한국어 사용자 문구. 예외를 그대로 새지 않게 api.py에서 경계
- 권한: api.py에서 역할 검사 (역할 체계는 9단계 권한 설계에서 확정 — 1차는 System Manager + 기준정보 관리자 + 생산 담당 3종 가정)
