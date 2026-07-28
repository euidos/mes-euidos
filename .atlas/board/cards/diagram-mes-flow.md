---
id: diagram-mes-flow
type: diagram
title: MES 설계 전체 흐름
status: decided
created: 2026-07-27T01:44:21+00:00
updated: 2026-07-27T01:44:21+00:00
---

```flow
{"kind":"graph","dir":"LR",
 "groups":[{"id":"m","label":"마스터"},{"id":"p","label":"계획·실행"},{"id":"t","label":"추적"}],
 "nodes":[
  {"id":"item","label":"Item 품목","group":"m"},
  {"id":"routing","label":"Routing 공정템플릿","group":"m"},
  {"id":"bom","label":"BOM 다층","group":"m"},
  {"id":"mold","label":"MES Mold 금형","group":"m"},
  {"id":"ws","label":"Workstation 호기","group":"m"},
  {"id":"rmlot","label":"원료 Batch","group":"m","shape":"db"},
  {"id":"wo","label":"Work Order","group":"p","shape":"round"},
  {"id":"jc","label":"Job Card 공정별","group":"p","shape":"round"},
  {"id":"se","label":"Stock Entry 제조","group":"p"},
  {"id":"ng","label":"불량·재작업","group":"p","shape":"diamond"},
  {"id":"batch","label":"Batch = LOT","group":"t","shape":"db"},
  {"id":"trace","label":"역추적 조회","group":"t","shape":"diamond"}],
 "edges":[
  {"from":"item","to":"bom"},
  {"from":"routing","to":"bom","label":"생성시 1회 복사"},
  {"from":"bom","to":"wo","label":"계획 단위 (금형 1세팅)"},
  {"from":"wo","to":"jc","label":"공정당 1장"},
  {"from":"ws","to":"jc","label":"호기"},
  {"from":"mold","to":"jc","label":"금형·타수"},
  {"from":"jc","to":"batch","label":"조 단위 발번"},
  {"from":"jc","to":"se","label":"실적"},
  {"from":"jc","to":"ng","label":"NG"},
  {"from":"ng","to":"batch","label":"순번 +1","dashed":true},
  {"from":"rmlot","to":"se","label":"소비"},
  {"from":"batch","to":"trace","label":"일자·호기·조·금형"},
  {"from":"se","to":"trace","label":"원료 로트","dashed":true}]}
```

범용 MES (우선 검증: 와이어하네스). WO = 계획 단위, Batch = 품질 추적 단위 — 주기 다름.
원료 로트는 Batch에 복제 안 함. Stock Entry 소비 이력이 유일 경로.

## Memory

전체 설계 흐름 요약 카드. 개별 결정은 `[[decision-scope-integration]]`
`[[decision-master-list]]` `[[decision-item-coding]]` `[[decision-routing]]`
`[[decision-bom-structure]]` `[[decision-lot-rule]]` 참조.
미결: `[[decision-lot-issuer]]`.

`use_multi_level_bom` 체크 여부가 BOM→WO 간선의 실제 동작을 가름:
ON이면 하위 BOM 공정까지 Job Card 생성 + 하위 원자재 폭발 소비(반제품 재고 미발생),
OFF면 반제품을 재고에서 소비하고 하위 WO를 별도 발행.
