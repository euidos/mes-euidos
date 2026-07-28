# 화면 명세 — 1차 7화면

공통: Desk 커스텀 페이지(`frappe.pages[...]` + `make_app_page(single_column=True)`)에 Vue 3 마운트.
frappe-ui 미사용, Frappe 번들러(`*.bundle.js`). 서버 호출은 `frappe.call` 래퍼 하나.
목록 골격·드로어/별도화면·인라인 액션(읽기만) 규칙은 decision-ui-shell.
Workspace 6개(현황·기준정보·생산·품질·재고·설정) 구성, 1차엔 있는 화면만 바로가기 노출.

각 화면 상세는 spec-screen-* 카드가 명세 그 자체 (열·필터·탭·동작·검증 표). 여기는 카드 참조 + 구현 보충만.

| 화면 | 카드 | 상세 유형 | 데이터 소스 (03-use-cases) | 보충 |
|---|---|---|---|---|
| 품목 | spec-screen-item | 드로어 (탭 4) | master_ui.list_items/save_item | 고객품번 검색 인덱스 확인 |
| BOM | spec-screen-bom | **별도 화면** (탭 5) | master_ui.list_boms/get_bom_detail/new_bom_version | 상태별 편집 잠금(초안만). 원가는 전 사용자 노출 |
| 설비 | spec-screen-workstation | 드로어 | master_ui.list_workstations/save_workstation | 실시간 상태 열 없음. 계획 기준 읽기전용 |
| 작업지시 | spec-screen-work-order | **별도 화면** (탭 4) | production_ui.* | 다층 전개 기본 켬. 금형 요소는 use_mold 조건부 렌더 |
| 실행 현황 | spec-screen-execution | 단일 화면 (카드 그리드 + 패널) | execution.get_floor_state + 쓰기 6종 | 작업자 기본값 = 로그인 Employee. 불량 코드는 MES Defect Code 목록 |
| 재고 조회 | spec-screen-stock | 목록 + **별도 상세 화면** | stock_ui.* | 변동 차트는 SLE 일자 집계 |
| LOT 추적 | spec-screen-trace | 단일 화면 (검색 + 양방향 트리) | traceability.trace/recall_summary | 트리(들여쓰기), 회수 요약 + 엑셀. 인쇄 고려한 마크업 |

## 프론트 구조 (슬라이스 안 page/ + 공용 최소)

```
mes_euidos/public/js/
  mes_common/        frappe.call 래퍼, 표·필터바·드로어·상태칩 등 공용 컴포넌트 (공유 커널 성격 — 최소 유지)
각 슬라이스 page/<name>/
  <name>.js          frappe.pages 부트스트랩
  <Name>App.vue      화면 루트
  components/        그 화면 전용
```

공용 컴포넌트는 세 번째 중복에서 추출 (vertical-slice: 커널 성급 생성 금지).

## 표기 규약 (전 화면)

- 날짜 `YYYY-MM-DD`, 시각 `HH:mm`. 수량 천단위 콤마, 단위 병기
- 상태 라벨 한국어 고정: 초안/미착수/진행중/완료/중단/종료, 유효/폐기, 사용/중지
- 빈 상태·로딩·에러 3태 컴포넌트 공용
- 확인 대화: 상태를 바꾸는 동작(시작·중단·완료·취소·작업종료)에만
