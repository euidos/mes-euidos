---
id: note-model-coverage
type: note
title: Work-world model — what Praxis knows about this system
status: active
created: 2026-07-31T15:00:00+00:00
updated: 2026-07-31T15:00:00+00:00
---

| what | count | provenance |
|---|---|---|
| documents (objects) | 460 | code (frappe + mes-euidos) |
| flows (activities) | 1,759 | mappers, buttons, derived writes, postings |
| rules | 4,285 | throw/warn guards + link filters + form rules, each w/ bypass |
| status derivations | 250 | status_map (server) + get_indicator (client) |
| state-guarded verbs | 462 | button guards |
| clock flows | 79 | scheduler entrypoints |
| policy engines | 53 | authored registry w/ arbitration modes |
| locks / tolerances | 22 / 19 | authored registry |

Praxis answers MECHANISM questions ("가능한 원인"). Instance questions ("지금 이 주문 어디까지?") → ERP 화면에서 확인.
