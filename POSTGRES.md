# ERPNext on PostgreSQL (euidos pg-port)

This fork (`euidos/mes_euidos-pg`, branch `pg-port/version-16`) runs ERPNext on
PostgreSQL 17. Upstream ERPNext supports MariaDB only; the frappe framework's
postgres support is official-but-experimental. Everything here keeps the
MariaDB path byte-for-byte identical unless a comment marked `pg-port:` says
otherwise, so rebases onto upstream `version-16` stay cheap.

The **repo** is `mes_euidos-pg`; the **Frappe app** is still `mes_euidos`
(`pyproject [project] name`), so `bench get-app <url>` lands it in
`apps/mes_euidos` and `bench install-app mes_euidos` is unchanged.

## How the port works

Three layers, smallest-diff-first:

1. **`mes_euidos/setup/pg_compat.sql`** — MariaDB builtins recreated as SQL
   functions in the site's `public` schema: `ifnull`, `if`, `curdate`,
   `datediff`, `date_add`/`date_sub`, `to_days`, `last_day`, `year`/`month`/
   `day`/`hour`/`minute`/`second`/`week`/`quarter`, `monthname`, `dayofweek`,
   `dayofyear`, `unix_timestamp`, `from_unixtime`, `truncate`, `instr`,
   `timediff`, `field`, a `group_concat` aggregate and a token-translating
   `date_format`. Each datetime helper has `timestamp` and `timestamptz`
   overloads (PG will not implicitly cast `now()` to plain timestamp during
   function resolution; `timestamptz` is the datetime category's preferred
   type, so unknown literals resolve there deterministically).
   Installed by `mes_euidos.setup.install.setup_pg_compat` via the
   `before_install` and `after_migrate` hooks — no-op on MariaDB, idempotent
   (`CREATE OR REPLACE` throughout), and safe to re-run any time:
   `bench --site <site> execute mes_euidos.setup.install.setup_pg_compat`.

2. **`mes_euidos/pg_driver_compat.py`** — registers identity JSON loaders with
   psycopg2 so `json`/`jsonb` columns come back as *strings*, which is what
   MariaDB (LONGTEXT) does and what every `json.loads` call site in frappe and
   mes_euidos expects. Imported from `mes_euidos/__init__.py`.

3. **Call-site edits**, each tagged `pg-port:` — only where MySQL *syntax or
   semantics* cannot be bridged by a function:
   - ANSI grouping: ungrouped selects aggregate-wrapped (`Max`/`Min`) or the
     group key extended; the same SQL runs on both engines. MySQL previously
     returned an arbitrary row's value — the aggregate makes it deterministic.
   - Double-quoted string literals → single quotes (PG treats `"x"` as an
     identifier).
   - `LIMIT off, cnt` → `LIMIT cnt OFFSET off`; alias-in-HAVING → expression
     in WHERE/HAVING; `(SELECT alias)` → repeated expression; `'a' - 'b'`
     string math → `TIMEDIFF`.
   - `TIMESTAMP(date, time)`, `FORCE INDEX`, `INTERVAL N unit`, zero-date
     `'0000-00-00'` comparisons, `GROUP_CONCAT ... SEPARATOR` → engine-gated
     (`frappe.db.db_type`) or rewritten portably (`INTERVAL 'N' unit` parses
     on both engines).
   - Unquoted mixed-case table refs (`tabItem.x` outside `from`) → backticked
     (frappe's PG adapter translates backticks to double quotes).
   - `frappe.db.get_value`/`get_all` with aggregate pseudo-fields
     (`{"MAX": ...}`) → explicit query-builder queries (frappe injects a
     default `ORDER BY creation` that violates PG grouping rules).

## Deployment requirement: ICU collation

Initialize the PostgreSQL cluster (or at least the site database) with the
ICU root collation, e.g. in docker:

```yaml
environment:
  POSTGRES_INITDB_ARGS: "--locale-provider=icu --icu-locale=und-x-icu --locale=C.UTF-8"
```

glibc locales ignore punctuation on the first collation pass, so `ORDER BY`
over names sorts `_Test ...` after `Advances ...` — the opposite of MariaDB.
ICU `und` treats punctuation as non-ignorable and matches MariaDB's ordering,
which order-sensitive ERPNext code (GL comparison, float summation order,
list views) and the test suite expect.

## Deviations from MySQL behaviour (accepted)

- `week()` uses ISO week numbering (MySQL mode 0 differs by ±1 at year
  boundaries); ERPNext only buckets rows by week.
- Aggregate-wrapped formerly-arbitrary values are now deterministic
  (`Max`/`Min`), on MariaDB too.
- `group_concat` supports no inline `ORDER BY`/custom separator (the two call
  sites that needed `SEPARATOR` now use engine-gated `STRING_AGG`).

## Known-not-ported

- `mes_euidos/patches/**` — migration patches for pre-existing MariaDB sites.
  **Postgres sites must be created fresh at or after this branch's version**
  (fresh installs mark all patches as executed). Cross-engine data moves use
  the pgloader runbook (fleet-infra `spec-pg-migration`), not patches.
- `Project Update` daily email queries reference columns that do not exist in
  the doctype — broken upstream on both engines, left as-is.
- Regional fixtures beyond the wizard defaults (UAE VAT, IRS 1099 custom
  fields) are syntax-fixed but not functionally exercised.

## Verified on postgres:17 / frappe version-16

- `bench new-site --db-type postgres --install-app mes_euidos` — clean, twice
  (second run exercising the before_install hook).
- Setup wizard (company, standard COA, fiscal year, KRW).
- Transaction flows: PO→PR→PI, SO→DN→SI→Payment Entry, stock transfer,
  BOM→Work Order→transfer+manufacture entries.
- Reports: General Ledger, Stock Ledger, AR, AP, Trial Balance, Balance
  Sheet, P&L, Stock Balance.
- Link-field search queries (item/lead/warehouse/employee/project-users).
- Static sweep: all 459 raw `frappe.db.sql` strings EXPLAINed against a live
  PG site; remaining flags are substitution artifacts or engine-gated code.
- mes_euidos test suite on the ICU cluster (2026-07-27): `sales_order` 85/85,
  `sales_invoice` 131/131, `purchase_receipt` 107/107, `stock_entry` 77/77,
  `payment_entry` 54/54, `work_order` 85/86.

## Known issues

- `test_valuation_rate_missing_on_make_stock_entry` (work_order) fails only
  inside a full-module run: an earlier test leaks state that lets the stock
  entry find a valuation rate. Standalone repro of the same scenario on a
  clean site raises the expected ValidationError on PG — the guarded logic
  itself is correct. Not investigated further.
- Payment reconciliation with `limit` filters and regional flows (UAE VAT /
  IRS 1099 with their custom fields installed) are syntax-fixed but not
  functionally exercised.

## Branch policy

These repos carry **only** `pg-port/version-16` — upstream ERPNext's ~555
development branches are deliberately not kept (they were pruned after the
fork; every one of them still lives in `frappe/erpnext`). Upstream's tags are
kept, so the base version (`v16.29.0`) stays identifiable.

## Rebasing on upstream

Upstream is not a branch in this repo, so add it as a remote once:

```sh
git remote add upstream https://github.com/frappe/erpnext.git
git fetch upstream version-16
git rebase upstream/version-16 pg-port/version-16
```

Conflicts should only appear where upstream touched a `pg-port:`-tagged line.
After rebasing: reinstall a scratch PG site, run the e2e flow script and the
EXPLAIN sweep, then run the module tests.
