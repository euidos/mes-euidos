<!-- euidos-graph:conventions:start -->
## Atlas conventions (euidos-graph — managed section, edit via euidos-cli src/euidos_cli/docs/AGENT-CONVENTIONS.md)

- **Understand code through the `atlas` MCP first**: query flows,
  callers/callees, endpoints, doctypes and their pointers instead of reading
  whole files; then read only the `file:Lline` ranges the answers give back.
  Rationale is indexed into the graph — the why is already there.
- **Write rationale where the graph indexes it**: every function/class gets a
  docstring whose FIRST LINE reads as a flow step (what this does in the
  process, one sentence); every non-obvious call gets a comment on or directly
  above the call line stating why it happens here (numbered in orchestrators:
  `# 3. typed answer to an open flow`). Only these two positions are indexed —
  they render in the atlas flow viewer as the step's rationale.
- **Organize by feature (vertical slices)**: before creating/moving ANY file,
  endpoint, doctype, or flow, use the `vertical-slice` skill and the repo's
  `ARCHITECTURE.md` (authoritative slice map). Slice = Frappe module;
  use-case folders hold `api.py` (transport only) + logic + tests; dotted
  paths are API — moves require caller updates, data patches, and shims in
  the same commit.
<!-- euidos-graph:conventions:end -->
