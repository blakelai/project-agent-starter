---
name: change-control
description: Assess changes to scope, capacity, dependencies or project baselines.
  Use when new requirements arrive, assumptions fail, staffing changes or delivery
  dates are revised.
---

# Change Control

Include vocabulary definitions, contexts, aliases and attachments in change impact. Read
vault/docs/domain-terminology.md; use terminology.py report to locate references and refresh only drafts.
Reconfirm changed business definitions with the domain owner; reassess each affected requirement's meaning,
acceptance and estimates. Preserve actuals, prior confirmations, and baseline term/context/asset snapshots.
Refreshing revisions does not approve definitions or close local impact questions.


1. Read existing baseline/assessment, progress actuals and the new requested change.
2. Write vault/requirements/<id>/changes/CR-xx.md using vault/templates/change-request.md: trigger, before/after,
   impacted AC/WP, estimate/schedule delta, options, risks, decision owner and decision status.
3. Re-run only invalidated evidence, impact, WBS, estimates and risks. Preserve completed actuals.
   For BRD or attachment changes, use vault/docs/brd-intake.md to compare original IDs and snapshots.
   Run scripts/refresh_brd.py --requirement <REQ-ID> only on a draft assessment. Reconcile added/removed
   items, stale evidence and image observations. Never refresh a baseline/closed requirement in place.
4. Reforecast using remaining effort with an explicit as-of date; the V1 schedule script schedules full WBS
   from scratch and MUST NOT be presented as an actuals-aware reforecast. Use a separate remaining-work
   assessment or a clearly documented manual forecast until an actuals-aware engine is added.
5. Show added/removed scope and resource effects separately. Keep baseline immutable and draft a superseding version.
6. Record an existing authorized decision; otherwise retain change as proposed. Do not silently reset commitment dates.
7. Identify downstream handoffs and wiki refresh requests after implemented changes.

## OKF editing contract

Before generating documents, read `documentation_language` from the project-data block in `vault/config/project.md` and apply the Document language policy in `AGENTS.md`. Use the resolved language for human-readable content; preserve machine-readable fields and original evidence.

Read `vault/docs/okf-profile.md`. Edit project knowledge under `vault/` as OKF Markdown. Structured facts live in the single marked YAML block in each Project Data note; preserve its markers, unknown fields, OKF frontmatter and surrounding prose. Update semantic body links when adding relationships. Frontmatter `status` is the knowledge lifecycle; project workflow status remains inside the data block. Commands run from the repository root.
