---
name: vertical-slice
description: How code is organized in euidos repos — feature folders + vertical slices. Use BEFORE creating any new file, endpoint, doctype, or flow, when deciding where code goes, and when moving/renaming anything (dotted paths are API). Covers Frappe-specific slice rules, the use-case folder shape, the move-safety checklist, and the verification ritual.
---

# Vertical slices in euidos repos

One rule generates everything: **code lives with the feature it serves; a
slice owns its transport, logic, models, and tests.** The repo's
`ARCHITECTURE.md` is the authoritative slice map — read it first; update it in
the same commit as any structural change.

## Where does new code go? (decision procedure)

1. **Which feature is this for?** → that slice's folder. New feature → new
   top-level slice: folder + entry in `modules.txt` (Frappe: slice = Module;
   its doctypes live in `<slice>/doctype/` — never parked in the default
   module, which owns nothing).
2. **Is it a new use-case** (an endpoint or user-visible operation)? → a
   use-case folder in the canonical shape:
   ```
   <slice>/<use_case>/
     __init__.py        # re-exports the use-case's public surface (if any)
     api.py             # transport ONLY: @frappe.whitelist, envelope/permission
                        # checks, request parsing, error boundary
     <use_case>.py      # logic — importable and testable without HTTP context
     test_<use_case>.py # REQUIRED — a use-case folder without a test is not done
   ```
   A use-case that is genuinely one file stays a slice-root file; promote it
   to a folder on the second artifact (and the test counts as one).
3. **Shared by several use-cases of ONE slice?** → slice-root module
   (`channel/security.py`, `agent/audit.py`).
4. **Shared by several slices?** → the shared kernel (e.g. `vault/`). Kernels
   are small, stable, and NEVER import slices. Resist creating kernels; two
   slices copying 30 lines beats a premature one — extract at the third copy.
5. **Cross-cutting wiring** (scheduler, permission hooks, fixtures) → only in
   `hooks.py`, pointing INTO slices.

## Dependency rules

- Direction: transport slices → engine/domain slices → shared kernel. Never
  backwards, never sideways between peers.
- **A slice's public surface is its `__init__` exports** — the ONLY names
  other slices may import. Everything not exported is private, underscore or
  not. Adding an export is an API decision; write it deliberately. Carve-out:
  dotted STRINGS handed to the framework (`frappe.enqueue` targets, hooks
  scheduler/permission paths) must name real module paths and may point at
  slice internals — they are wiring, not imports; the move checklist is what
  protects them.
- Web pages (`www/`, `templates/`) are plumbing: thin controllers importing
  slice PUBLIC surfaces. A www page calling slice logic directly is correct —
  routing it through the slice's HTTP `api.py` would be
  transport-calling-transport.
- Two deploy units (e.g. a Frappe app and a standalone sidecar) may share a
  contract only via (a) a deliberately frappe-free module imported by both
  sides of ONE repo, or (b) duplicated code pinned by a **golden-vector
  test** on BOTH sides (fixed inputs → hardcoded digest), so drift fails a
  test instead of production.

## Tests

- Unit/integration tests sit BESIDE the artifact they test (use-case folder,
  doctype folder); slice-wide e2e at slice root; never in another slice or in
  the kernel (a kernel test that imports a consumer slice belongs to that
  slice).
- Prefer tests that run WITHOUT a bench (pure logic, golden vectors) — they
  gate every commit anywhere. Frappe-context tests use the
  IntegrationTestCase/FrappeTestCase try-import idiom and run under
  `bench --site <site> run-tests --module <dotted.test.module>`
  (`set-config allow_tests true` first).

## Frappe hard rules — dotted paths are API

These break silently at runtime, not at import. When you MOVE or RENAME
anything, in the SAME commit:

1. **Find every dotted reference**: `grep -rn "old.dotted.path"` across
   `*.py *.json *.txt *.js *.md` — hooks.py (scheduler, permission hooks,
   after_migrate), patches.txt, `frappe.enqueue("…")` strings, doctype JSON
   descriptions/defaults, fixtures, page JSONs and their .js, README run
   commands, and OTHER repos calling `/api/method/<dotted.path>`.
2. **DB-stored paths** (handler paths resolved via importlib): a data patch
   rewriting the stored prefix, registered in patches.txt
   (post_model_sync). If a hooks-based allowlist gates those paths, the
   rename invalidates external registrations — release-note it.
3. **Externally-addressed whitelisted methods**: keep a re-export shim at the
   old path for one release (re-importing the decorated function keeps it
   whitelisted). **In-flight queue jobs**: RQ payloads already in Redis carry
   old dotted targets through the deploy window — moved enqueue TARGETS need
   one-release alias modules too (`old_module.py` re-importing the function).
4. **Deploy ordering across repos**: a caller's *defaults* may only point at
   paths that exist in EVERY fleet state during the roll. Old default + shim
   on the callee covers both; flipping the default waits for convergence.
5. Doctype moves between modules: update JSON `"module"`, move the folder,
   add a patch `frappe.db.set_value("DocType", name, "module", NewModule)`.
   Removing a module: folder + modules.txt line + patch deleting the
   `Module Def`. Dead doctypes: delete folder + patch `frappe.delete_doc`.

## Verification ritual (after any structural change)

1. `python3 -m compileall -q <pkg>`.
2. Rebuild the graph **from clean state** (`rm -rf graphify-out` first — the
   incremental extractor state goes stale after mass `git mv`): entrypoint
   count unchanged (± intended), dangling = 0, flow lens traces the moved
   use-cases end-to-end.
3. **Body-hash invariant** for pure moves: diff pre/post `(label, body_hash)`
   multisets — every changed symbol must be explainable (import fix, path
   string, rename). An unexplained change means logic drifted.
4. Pure-unit tests locally; Frappe tests on a bench. No bench around? A
   disposable one from the PUBLIC image verifies install+migrate+tests:
   mariadb + redis containers + `frappe/erpnext:v15`, bind-mount the app,
   `pip install --ignore-requires-python --no-deps -e` + missing pure deps,
   append to sites/apps.txt (NEWLINE-SAFE — see gotchas), new-site (wait for
   mariadb readiness first), install-app, migrate, run-tests.
5. Adversarial review before merge: one pass hunting dotted-path/runtime
   breakage, one judging the slicing against the rules. Fix, re-verify,
   repeat until findings stop.

## Gotchas (each one cost real time on 2026-07-22)

- **`frappe.cache().get_value(k)` poisons `frappe.local`'s request cache with
  None**; a later `set_value(k, v, expires_in_sec=…)` writes redis only, so a
  same-request re-read returns the stale None. Guards that must see fresh
  state use `get_value(k, expires=True)`.
- **Appending to newline-terminated registries** (patches.txt, apps.txt)
  without checking the trailing newline silently concatenates entries —
  always append newline-safely.
- Frappe's whitelist registry keys on the FUNCTION OBJECT — a shim that
  re-imports the decorated function keeps the old dotted path working with
  identical allow_guest/methods.
- Comments claiming wiring that doesn't exist are worse than no comments
  (hooks claimed a CORS filter that was never wired). The graph's dead-code
  report is the arbiter — delete dead code; make surviving comments true.
- Catch-all modules (`api/`, `lib/`, `utils/`) collect orphans and decay into
  lies. No feature → no home → question it.
- By-kind folders are allowed only INSIDE a slice, for a layered engine's
  internals (an acyclic import graph converging on one state machine is the
  test) — never at the top level.
