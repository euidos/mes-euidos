# Production-grade Korean ERP/MES translations

## Goal

Ship a Korean translation catalog for every translatable Frappe and
`mes_euidos` source in the checked-out revisions, including strings that
already have a Korean translation. Combine static gettext catalogs and source
extraction with the dynamic messages exposed by `kyp.jh.internal` on
`dev-jh`; no single extractor is authoritative on its own.
The catalog must load automatically with the app, use terminology familiar to
Korean ERP/MES operators, and preserve meaning in each UI and business
context.

## Terminology and style

- Keep `BOM` as `BOM`.
- Prefer terminology used by established Korean ERP/MES products. Public
  references include
  [ECOUNT production management](https://www.ecount.com/kr/ecount/trial/suitable-erp-for-production-management),
  [ECOUNT ERP functions](https://www.ecount.com/kr/ecount/trial/what-is-erp),
  and
  [Douzone MES10 training material](https://www.douzone.com/product/msg/mkt_2023/images/FoEX_ERP10_edu.pdf).
- Use concise noun phrases for labels, fields, and buttons.
- Use concise polite Korean for guidance and errors, such as
  `확인해 주세요` and `처리할 수 없습니다`.
- Preserve product names, identifiers, code, placeholders, markup, links,
  whitespace semantics, and number formats.

## Context and consistency

Treat a translation's semantic key as:

`source text + Frappe context + ERP domain + UI role`

The same semantic key must always have the same Korean translation. The same
English text may have different translations only when its semantic key
differs. Different English expressions that represent one ERP concept use one
canonical Korean term. Every intentional exception records its source
location and rationale.

Recover context from both apps' POT catalogs, source call sites, DocType
metadata, field types, and existing translations. Translate and review in
domain groups: accounting, selling, buying, stock, manufacturing, quality,
HR, and system administration.

Existing Korean is subject to the same review as untranslated English.
`bench get-untranslated` is only a negative check: a truthy but inappropriate
translation such as `Appointment → 약속` is not evidence of quality.

## Authoritative source union

Build the reviewed inventory from the union of:

1. Frappe's complete static POT/PO and source extraction;
2. `mes_euidos`' complete static POT/PO and source extraction, including
   Workspace, DocType name, field, option, report, print, web, and bundled
   JavaScript messages;
3. site-backed DocType, Page, Report, Workflow, Custom Field, Navbar, and
   server-message extraction from `kyp.jh.internal`; and
4. explicit context variants and runtime fallbacks retained by the reviewed
   catalog.

Record source app, locations, gettext context, and extraction methods for
every key. Acronym-bearing module names such as `CRM` must not be lost through
case-changing helpers such as `unscrub`.

Audit to a fixed point: extract the union, translate and review it, compile
and load it through Frappe, re-extract, then repeat until no new key appears
and every source/context key is either translated or explicitly classified.

## Runtime format

`mes_euidos/translations/ko.source.jsonl` records the exact, unambiguous
source/context union and its app/location/extraction provenance. Bench's
`get-untranslated` text format is used only as a final runtime check because
it omits already translated strings, depends on the current site database,
and its pipe escaping cannot distinguish some combinations of literal and
actual newlines.

`mes_euidos/translations/ko.context-overrides.json` explicitly records every
reviewed default fallback or gettext context retained outside that exact
source extraction. Tests require the catalog key set to equal the source
inventory plus this approved overlay, preventing silent context typos.

`mes_euidos/translations/ko.csv` is the complete runtime overlay. Frappe v16
loads this file directly from installed apps, so it requires neither a
database import nor an MO compilation step. Because `mes_euidos` loads after
`frappe`, its entries can replace unsuitable core translations.

Keep MES-owned translations in `mes_euidos/locale/ko.po` synchronized with the
CSV. A compiled `mes_euidos.mo` is loaded after the app's CSV and must never
reintroduce an older translation. Frappe-owned strings remain in the CSV
overlay only. Automated checks enforce equality wherever CSV and PO overlap.

## Quality gates

- Every source/context key in the static and dynamic union is represented,
  except explicitly classified non-linguistic input.
- The full extraction reaches a fixed point: a second extraction after
  packaging introduces zero new keys.
- Existing Korean translations are checked against the same glossary,
  context, and style rules as newly translated strings.
- CSV is valid UTF-8 and every row has two or three columns.
- Source/context keys are unique and semantic-key collisions are reviewed.
- Python, JavaScript, and named placeholders have identical multisets in the
  source and translation.
- HTML/XML tags, links, escaped characters, and newline structure are
  preserved.
- Protected ERP terms and the Korean terminology glossary are enforced.
- Unapproved English residue, inconsistent honorific style, literal
  translation patterns, and excessive UI expansion are rejected.
- `BOM` can never be translated as `봄`.
- Existing `verify_translation_files("mes_euidos")` passes.
- The Frappe v16 loader returns the expected Korean values from the packaged
  CSV/PO combination.
- A fresh `bench get-untranslated ko` run reports only reviewed exclusions.
- Named regression examples including `Appointment`, `Total Warehouses`,
  `Permission Manager`, CRM Settings labels, and administrator user/login
  labels resolve to reviewed Korean at runtime.
- Representative accounting, buying, stock, manufacturing, and quality
  screens and messages are checked in a real browser on `dev-jh`.

## Delivery

Commit the translation catalog, glossary/context records, and focused
validation tooling to `pg-port/version-16`. Push the verified commit to the
existing upstream branch. Whiteboard-card and Atlas-plan stages are omitted
at the founder's explicit request.
