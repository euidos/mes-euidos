---
id: note-audit-defects
type: note
title: Defect register — 2026-07-30 business-logic audit by-catch
status: open
created: 2026-07-30T14:00:00+00:00
updated: 2026-07-30T14:00:00+00:00
---

Found while auditing for Praxis logic extraction. NOT fixed — port agent to triage.

| # | defect | site | impact |
|---|---|---|---|
| 1 | `calculate_contribution()` iterates `this.frm.doc.doctype.sales_team` — `doc.doctype` is a STRING → permanent no-op | public/js/utils/sales_common.js:353 | sales-team allocation never computed client-side; server throw only at save |
| 2 | JS `received_qty = qty + rejected_qty` omits `process_loss_qty` (server includes it) | public/js/controllers/buying.js:245 vs subcontracting_receipt.py:552 | client shows wrong received qty until save |
| 3 | JS commission bound checks only `> 100`; server enforces `0..100`; JS also mutates field to 100 before throwing | public/js/utils/sales_common.js:329 | negative commission passes client |
| 4 | SO Closed-check runs AFTER `super().on_cancel()` side effects | selling/doctype/sales_order/sales_order.py:536-540 | cancel of Closed SO partially executes before throwing |
| 5 | `ignore_linked_doctypes` assigned a BARE STRING (substring membership, not tuple) | stock/doctype/quality_inspection/quality_inspection.py:203 | cancel-link exemption semantics accidental |
| 6 | `overproduction_percentage_for_sales_order` used as MULTIPLIER not increment | selling/doctype/sales_order/sales_order.py:2047 | pending qty = qty × pct (e.g. 10% → 0.1×qty) when nothing pending |
| 7 | Fiscal Year `on_trash` has NO GL-Entry guard | accounts/doctype/fiscal_year/fiscal_year.py:36-40 | FY with postings deletable |
| 8 | duplicate portal route `purchase-orders` | hooks.py:153,162 | dead rule |
| 9 | `Accounts Settings.over_billing_allowance` fieldtype Currency, semantics percent | accounts_settings.json:217 | data-model smell, confuses configuration |
| 10 | over_picking: SO aggregate uses `over_picking_allowance`, Pick List rows use `over_delivery_receipt_allowance` | sales_order.py:718 vs pick_list.py:539 | two different caps for the same business act |
| 11 | permission asymmetry: bulk close = write perm, single close = submit perm | sales_order.py:981 vs :1833 | same action, two authority levels |
| 12 | delivery-schedule split algorithm exists ONLY client-side; server persists blindly | sales_order.js:709-763 vs sales_order.py:885 | API callers can write arbitrary schedules |

Source: 8-perspective audit, full reports in graphify-euidos board [[decision-praxis-logic-display]] Memory.
