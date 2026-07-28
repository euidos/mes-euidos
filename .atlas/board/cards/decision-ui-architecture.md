---
id: decision-ui-architecture
type: decision
title: UI 구조 = Desk 커스텀 페이지 + 기본 목록 미노출
status: decided
created: 2026-07-27T09:26:49+00:00
updated: 2026-07-27T12:22:44+00:00
---

**ERPNext = 백엔드 엔진. 화면은 Desk 안의 커스텀 페이지로 전부 자체 제작.**

```
Frappe Desk (셸)
 ├ 상단바·좌측 메뉴·검색·알림          ← Frappe
 ├ Workspace (사용자별 개인화 홈)       ← Frappe. 로그인 시 첫 화면
 ├ 커스텀 페이지들 (Vue 마운트)         ← 화면 내부 100% 자체
 │    대시보드 · 품목 · BOM · 금형 · 계획 · 작업지시 · 현장실행 · 검사 · 추적 …
 └ ERPNext 기본 폼·목록                 ← 시스템 관리자 뒷문. 고객 사용자 미노출
```

| 결정 | 값 |
|---|---|
| 화면 위치 | **Desk 커스텀 페이지** (`/app/<page>`) |
| 화면 내부 | Vue 앱 마운트, 디자인 자체 |
| 로그인 후 첫 화면 | `User.default_workspace` 로 대시보드 지정 |
| 기본 목록·리포트 빌더 | **고객 사용자에게 미노출 (A-1)** |
| 계정 | **전원 System User** |
| 연쇄 로직 위치 | **DocType 훅** (`[[decision-business-logic-placement]]`) |

```javascript
frappe.pages['mes-dashboard'].on_page_load = function (wrapper) {
    const page = frappe.ui.make_app_page({ parent: wrapper, single_column: true });
    createApp(Dashboard).mount(page.main[0]);   // 이 안은 전부 자체
};
```

### Desk를 쓰는 대가로 얻는 것

| Frappe 기능 | 직접 만들면 |
|---|---|
| **Workspace** | 사용자가 홈에 카드·차트·바로가기 배치·편집 |
| **User Permission** | "이 사람은 3호기 데이터만" 사용자별 데이터 범위 |
| 권한 엔진 | 역할·필드 수준·문서 수준 |
| 알림·할당·코멘트·첨부 | 협업 기능 |
| 버전 이력 | 누가 언제 무엇을 바꿨나 |
| 인쇄 양식·다국어·단축키 | |

## Why

Desk 껍데기를 받아들이는 대신 Workspace 개인화·권한 엔진·알림·이력을 재구현하지 않음.
화면 내부는 빈 공간이라 Vue 앱을 붙이면 디자인 자유도는 그대로.

**A-1(기본 목록 미노출) 근거**: 기본 목록을 열면 ① 거기서 직접 수정해 우리 연쇄 로직을 우회할 수
있고 ② 화면이 두 종류(우리 디자인 / Frappe 디자인)로 보이며 ③ 숨긴 원가·단가 필드가 노출됨.
리포트 빌더의 이득(관리자가 표를 직접 조립)은 실제 사용률이 낮음 — 중소 제조업에서 필터 UI를
익혀 쓰는 사람은 1~2명이고 결국 엑셀로 내보내 작업함. 그 편의 때문에 위 셋을 감수할 균형이 아님.

기본 목록에서 바꿀 수 있는 것은 **내용**(열·라벨·색·버튼·필터)뿐이고 **모양**(레이아웃·타이포·
여백)은 Frappe 것 — CSS로 덮으면 업그레이드마다 깨짐. 그래서 노출하면 시각적 이질감이 남음.

## History

- 초안(Q2): **하이브리드** — 마스터·문서는 Desk 기본 폼, 현장만 커스텀. `superseded`
- 2차: **독립 주소 포털 + Website User** — 전면 자체 UI. `superseded`
  - 폐기 사유: Workspace 개인화·User Permission·알림·리포트 등 Frappe 기본 기능을 재구현하게 됨.
    사용자가 Desk 셸을 쓰는 쪽을 선택.
  - 이 전제 위에서 나왔던 하위 논의(포털 라우트 `www/`, "사람 수 × 화면 다양성" 배치 기준,
    Website User 비용 절감)는 무효.
- 2026-07-27 확정: **Desk 커스텀 페이지 + A-1**

## Memory

**Q4(마스터는 ERPNext DocType 재사용)는 유효** — 지금까지 확정한 백엔드 설계(품목·BOM·금형·
LOT·창고·계획)는 화면 방식과 무관하게 그대로.

**계정이 전원 System User가 됨** → 자체 호스팅이면 비용 0, 관리형 호스팅(Frappe Cloud류)은
인원수 과금 구조이므로 문진 14번(배포 모델)에 묶임. Frappe 16.28.0 기준 코드상 인원 제한은 없고
`User.simultaneous_sessions`(동시 세션)만 존재.

**현장 폰 화면도 Desk 페이지로 통일**(A). Desk 껍데기가 폰에서 자리를 먹으므로 `single_column`에
상단바를 접는 전체화면 처리가 필요 — 실제로 붙여보고 조정할 영역이라 지금 확정하지 않음.
QR 진입 주소는 `/app/work-execution?ws=IJ03` (`[[decision-shopfloor-execution]]`).

Frappe 16.28.0 확인 사항: `www/desk.html` 에 반응형 뷰포트와 "홈 화면에 추가" 메타는 있으나
`manifest.json`·서비스 워커는 없음 → 설치형 PWA·오프라인 캐시는 기본 제공이 아님.
권한 축소 수단: `Role.desk_access`, `User.block_modules`, 커스텀 `User Type`(허용 DocType·모듈 지정),
`User.default_workspace`, `Role.home_page`, Customize Form + Permission Level.
