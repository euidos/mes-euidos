---
name: plan
description: Plan implementation work by DECLARING intent in the source — plan tags on existing symbols, stubs for new ones, PLAN.md for the story — reviewed live in the Atlas viewer and gated on human approval. Use BEFORE implementing any non-trivial change. After implementing, audit-plan verifies the work against the approved declaration.
---

# Plan → Review → Gate → Implement → Audit

A plan is **declared, not diffed** (contract v1, 2026-07-23): you annotate
the tree with intent, the watcher indexes it live, a human approves it, you
implement, and the auditor checks the result against what was declared. The
tree stays green while you plan — tags are comments, additions are stubs.

## 0. Dev server + graph-first comprehension

`curl -s http://127.0.0.1:8177/api/graph -o /dev/null` — if it fails, start
`uvx euidos-graph up` from the repo root (add `--bind lan` only for remote
review over Tailscale). Understand the code you're about to change through
the `atlas` MCP tools (`search_nodes`, `impact`, `call_sequence`, `flows`,
`current_plan`) BEFORE planning. Prefer graph queries over grep.

## 1. Declare the plan (three instruments)

**Tags** — on existing symbols, comment block directly above the `def`/`class`:

```python
# plan(edit): gate cost daily BEFORE ack/enqueue so we spend nothing
# on a request we'll refuse anyway.
def handle(payload: dict) -> dict:
```

- Verbs: `edit` (body will change, structure stays) · `delete` (symbol goes;
  say what supersedes it) · `rewrite` (structure changes — you may replace
  the body with a skeleton NOW, knowingly breaking it).
- One tag per symbol; continuation comment lines join the note; the
  `# atlas:` pragma may share the block.
- File-level intent = same grammar in the comment block at line 1 of the
  file (e.g. planning a module's deletion).
- Doctype/schema intent goes on the CONTROLLER class (JSON can't carry
  comments).

**Stubs** — for anything NEW: real files at real target paths, typed
signatures, docstring = the step's stated intent, body sketches the intended
calls/branches (or just `...`). A callee that doesn't exist yet gets stubbed
too — a name with no node is not a plan. Realizing a business-process step?
Put `# atlas: realizes process:<id>` on the line above the def (it may share
the comment block with a plan tag); new/changed process steps belong in
`atlas/model.json`.

**PLAN.md** — at the repo root: the story of the whole change (goal, order,
risks). Lifted verbatim into the review payload. It is part of the plan's
lifecycle: the auditor requires its deletion when the work is done.

Do NOT implement while planning. `edit`/`delete` tags leave bodies untouched;
only `rewrite` may skeletonize.

## 2. Checkpoint = save; sanity-check what the reviewer sees

The watcher indexes saves within seconds. Check:
`curl -s http://127.0.0.1:8177/api/plan | jq '.summary, .lints'` —
counts must match your declaration and **lints must be empty** (orphan tags,
duplicate tags, unknown verbs, empty notes are listed with file:line).

## 3. Request review, then GATE — never implement unapproved plans

Tell the user: "Plan ready for review at http://127.0.0.1:8177 (or the
machine's Tailscale address). When you've decided, tell me (or any Claude)
'approve' or 'request changes: <why>'." The reviewer's Claude records it:
`uvx euidos-graph decide approve|request-changes --comment "…" [--url http://<tailnet>:8177]`
Then block:

    euidos-graph gate --timeout 3600

Exit 0 = approved (the declared plan is frozen into a manifest) → implement.
Exit 2 = changes requested → revise the declaration, repeat from step 2.
Exit 3 = timeout → ask the user; do not proceed.

## 4. Implement, then AUDIT

Implementing a tag = doing the work AND deleting the tag; implementing a stub
= filling the body; finishing = deleting PLAN.md. Then:

    euidos-graph audit-plan          # --strict to make advisories blocking

Exit 0 = clean (manifest consumed; cycle complete). Exit 2 = findings:
`tag-remains` / `stub-unimplemented` / `delete-unresolved` / `plan-md-remains`
block; `undeclared-change` (you touched something you never declared) is
advisory — explain it to the user or declare-and-re-review. Exit 4 = no
manifest (nothing was approved).

Never write to `graphify-out/` (gitignored, derived); never commit graphs.
Tags, stubs, and PLAN.md ARE committed while a plan is in flight — they are
the plan.
