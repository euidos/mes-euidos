---
name: whiteboard
description: Record discussions, decisions, specs, and run status as whiteboard cards the founder views live in Atlas. Use when brainstorming, comparing options, deciding designs, or running long multi-step work.
---

# Whiteboard — the human frontend of agent thought

The Atlas viewer has a **Whiteboard** tab: project-scoped boards of cards
that YOU author. It serves TWO audiences with one card:

- **The founder** reviews at a glance what you are considering — the card's
  face is compressed and visual, because the whole point is less reading.
- **Future agents** (including future you) recall full context — verbose
  memory is welcome, but only in its designated place (see below).

It is the discussion-layer sibling of the plan contract: plan tags declare
code intent in the tree; whiteboard cards record the thinking around it.
**Read the relevant board (`board_get`) before re-opening any topic, and
`board_search` before re-deciding anything.**

## One board per project — and a project IS a repo

Adjacent repos are read-only context: every decision made for developing a
repo stays within that repo, at `.atlas/board/cards/<id>.md` (markdown +
frontmatter), committed to git. The daemon watches the files; the viewer
updates live. Cards belong to the repo the discussion concerns — when
working outside the daemon's launch repo, pass `project=<repo-alias>`.

## When to write a card — and when not

WRITE when discussion produces something durable:
- a design **decision** (even a small one, if someone could re-litigate it)
- an agreed **spec** (the mandatory final step of any brainstorm)
- a **gotcha/insight** worth a week's memory
- a long run's **status** (the founder watches the card, not the chat log)
- a **visualization** that answers better than prose ever could

DO NOT write for:
- chat-sized answers to simple questions
- restating what code/git/CLAUDE.md already records
- work you are about to do anyway with no open question in it
- knowledge with a better home: box-specific procedure -> workspace
  `handbook/`; per-repo architecture -> that repo's `docs/`. The board is a
  live surface, not an archive.

## How card bodies are WRITTEN (founder rule, 2026-07-23; v2 2026-07-24)

**The visual IS the explanation. Text is captions.** (founder, 2026-07-24)

Build every face AROUND one main visual — a diagram or a table that carries
the COMPLETE story on its own. Write the visual first; only then ask what
text is still needed, and keep each piece to a one-line caption. If a
reader must read prose to understand the card, the visual is incomplete —
fix the visual, don't add paragraphs.

- A cycle/flow/architecture gets ONE diagram covering the WHOLE loop —
  end to end, including the unhappy paths (fail → where?). Never a
  fragment diagram plus bullets that finish the story in words.
- Options/comparisons/questions -> a table. A question list is a table of
  `question × options`.
- Prose bullets on a face: hard budget ~5 lines TOTAL. Each must earn its
  line by saying something no visual can (a rationale, a contract clause).
- Diagrams are ```flow fences (interactive React Flow — see below); tables
  sort on header click; spec checkboxes render a progress bar; pins render
  jump-chips into Browse/Flow; `canvas` cards run sandboxed HTML/SVG/JS
  for anything the fence can't draw. Mermaid is GONE — never author it.

Remaining text uses **caveman Ultra** (canonical skill in the workspace
`handbook/skills/caveman/`; inlined here so this stays portable): drop
articles/filler/hedging/pleasantries; fragments fine; abbreviate common
words (evt, tbl, proj, cfg, btn); `->` for causality; identifiers, API
names, numbers NEVER abbreviated. Full sentences ONLY where ambiguity is
dangerous (decision rationale, contract clauses) — max 2 lines.

## Diagrams: the ```flow fence

A json fence rendered as an INTERACTIVE React Flow canvas (pan, pinch
zoom, collapsible groups, auto layout via ELK — layout order never needs
hand-tuning). Schema:

```
{"kind": "graph" | "seq",          graph = flowchart (default), seq = sequence
 "dir": "TD" | "LR",               graph only, default TD
 "groups": [{"id", "label"?}],     graph only — collapsible containers
 "nodes": [{"id", "label",
            "group"?,              member of groups[].id
            "shape"?,              box (default) | round | diamond | db
            "pin"?}],              Atlas graph node id -> click jumps to it
 "edges": [{"from", "to", "label"?, "dashed"?}]}
```

- kind "seq": nodes = participants (lanes), edges = messages TOP-DOWN in
  author order; `from == to` draws a self-message stub.
- Node labels ≤5 words; detail goes in edge labels or the caption line.
- Group anything ≥ 6 nodes — the founder collapses groups to skim.
- Invalid json shows an error + the raw fence; check your commas.

**`## Memory` section (agent-facing, always LAST):** verbose context for
future recall — why alternatives lost, constraints discovered, exact
identifiers, related cards (`[[card-id]]`). Compression rules do NOT apply
there; completeness beats brevity. Everything above it stays founder-first.

## Tools (atlas MCP)

`project_list()` · `board_get(project?)` · `board_upsert_card(card_id,
type, title, body, status?, pins?, project?, expires?)` ·
`board_archive_card(card_id, archived?, project?)` ·
`board_search(q)` — one query over EVERY project's board.

## Card lifecycle

- **Edit in place is the default.** Stable slug ids (`decision-…`, `spec-…`,
  `note-…`); revisiting a topic updates its card. Check `board_get` before
  creating anything.
- **Supersede, don't duplicate**: a reversed decision rewrites its card
  (status `superseded` on the old choice inside `## History`, new outcome
  on top).
- **Archive** (`board_archive_card`) hides; git keeps. Never delete files.
- **Ephemeral cards**: brainstorm scratch and one-off visuals get
  `expires: <days>` — they auto-archive once the time elapses and the card
  has settled (never applies to decision/spec, never to open/active).
- The board auto-orders by lifecycle: `active` pins top (Live), `open` and
  recently-edited float (Working), decided/done/stale sink (Settled). You
  never manage placement — status honesty IS placement.

## Card types and bodies

| type | body |
|---|---|
| `note` | markdown (headings, lists, GFM tables) |
| `table` | markdown, table-first |
| `decision` | options × criteria GFM table, **chosen option bolded**, then `## Why` and (when revisited) `## History`; status `open` → `decided` |
| `spec` | checkbox list `- [x] …` of agreed requirements; status `open` → `done` |
| `plan` | usually NOT needed — the viewer injects a live plan card while a plan is in flight |
| `status` | a ```json fence: `{"goal": str, "steps": [{"label", "state": "pending|active|done|failed", "note"?}], "subagents"?: [{"label","state","detail"?}], "eta"?: str}` |
| `diagram` | a ```flow fence (interactive React Flow — schema below) |
| `canvas` | an HTML/SVG/JS document — renders SANDBOXED in the viewer (no network, no parent access); for rich visualization/animation chat cannot show |

`pins`: graph node ids — the viewer renders jump-chips into Browse/Flow.
Get ids from atlas MCP `search_nodes`.

## Status discipline (agent runs)

At the start of a long/multi-step run, upsert `status-run` (singleton per
board, status `active`): goal, planned steps, subagent fan-out, honest ETA.
Update states as steps finish; on completion set status `done` with the
outcome in the fence. The founder watches this card instead of the chat log.

Liveness (working/idle) is INSTRUMENTED separately — Claude Code hooks stamp
`.atlas/run.json` via `euidos-graph run-status`; never write that file from
a skill, and never let it replace the steps narrative above.
