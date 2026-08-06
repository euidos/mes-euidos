---
id: decision-frontend-stack
type: decision
title: 프론트 = 순수 Vue 3 + Frappe 번들러
status: decided
created: 2026-07-27T12:22:44+00:00
updated: 2026-08-06T00:00:00+00:00
---

**순수 Vue 3 + Frappe 내장 번들러.** `frappe-ui` 미사용. 코드·디자인 재사용 없음 — 방법론만 차용.

| 방법론 | 내용 |
|---|---|
| 배치 | **Desk 커스텀 페이지** 안에 Vue 앱 마운트 (`frappe.ui.make_app_page` → `createApp().mount()`) |
| 부팅 | 페이지의 `.py` 에서 초기값 조회 후 주입 (로그인 사용자·설비 컨텍스트 등) |
| 빌드 | **Frappe 내장 번들러** (`*.bundle.js`) — 별도 프론트 빌드 파이프라인(Vite·webpack) 없음 |
| 서버 호출 | `frappe.call` → `<app>.api.<모듈>.<함수>` |
| 서버측 | `api/*.py` 에 화면용 함수. **DocType 직접 노출 안 함** |

| 기준 | **순수 Vue** | frappe-ui |
|---|---|---|
| 디자인 | 완전 자체 | 부품에 고유 스타일 → 덮어쓰기 비용 |
| 데이터 호출 | `frappe.call` 래퍼 파일 1개 | 전용 훅 |
| 의존성 | 없음 | 라이브러리 + Tailwind 계열 |

## Why

디자인을 전부 자체 설계하므로 기성 부품 모음의 이득(완성된 디자인)이 사라지고 덮어쓰기 비용만 남음.
데이터 호출 편의는 `frappe.call` 을 감싸는 함수 몇 개로 충분 — 파일 하나면 됨.

업무 규칙은 API 함수가 아니라 DocType 훅에 둠 (`[[decision-business-logic-placement]]`) —
화면은 표시·입력만 담당.

이 방식은 Frappe 가 Desk 자체 기능(Form Builder·Workflow Builder·file uploader, `.vue` 53개)에
쓰는 방식과 동일하다 — 플랫폼의 결을 따라가는 선택이지 추가 베팅이 아니다.
frappe-ui 의 자리는 Desk 밖 독립 포털(고객사 셀프서비스 등)을 만들 때이고, 그때 별도 결정한다.

## 빌드에 대한 정정 (2026-08-06)

최초 기록의 "node 도구체인 없음" 은 **틀린 서술**이었다. Frappe 내장 번들러 자체가
esbuild(Node) 다 — `bench build` 는 Node 를 실행하고, frappe 는 `esbuild-plugin-vue3` 를
내장해 `.vue` SFC 를 공식 지원한다. 이 결정이 실제로 배제하는 것은 **별도** 프론트
파이프라인(Vite·webpack·Tailwind)이지 Node 그 자체가 아니다.

실무 결과: `.vue` 를 쓰는 클라이언트 앱의 이미지는 thin layer(클론+pip)로는 못 만들고
**빌드 스테이지가 있는 full build** 가 필요하다 (`public/dist` 는 커밋하지 않는다 —
빌드 산출물은 이미지 빌드가 만든다). tenant-base 가 mes_euidos 자산에 이미 하던 그대로다.
kyp 에서 이 오해로 thin-layer 배포가 한 번 막혔다 — fleet-infra release-kyp 가 full build 로
전환된 이유.

## Memory

**천일테크윈 버전 조사 결과 (2026-07-27, 코드 재사용은 안 함 — 방법론 확인용)**

`/root/work/clients/천일테크윈/euidos_mes_천일버전` — Vue 3 SPA를 포털 경로(`/euidos-mes`)에 올린 구조.
components 21개, views 18개, `api/master_data.py` 517줄. 우리가 결론 낸 구조와 동일한 방식이었고,
별도 프론트 파이프라인 없이 Frappe 번들러만 씀 (Node 는 bench build 가 쓴다 — 위 정정 참조).

그 코드의 한계(참고): 데이터 대부분이 브라우저 `localStorage` 시드(`domain/store.js`, `seed.js`)이고
실제 서버 연동은 마스터 CRUD뿐. 작업지시·실행·검사·재고·추적 화면은 골격만 존재.
업종도 하네스 기준이라 금형 개념이 없음.

**Q1 재검토 종결**: "제품 라인과 천일 라인을 안 섞는다"는 결정은 유지. 근거는 바뀜 —
원래 근거였던 "UI 방식이 다르다"는 사라졌고(실제로는 같은 방식), 대신 **천일은 고객 납품물이라
제품과 한 코드로 묶이면 서로 발목을 잡는다**는 것이 유지 근거.
