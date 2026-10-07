---
name: change-control
description: Assess changes to scope, capacity, dependencies or project baselines.
  Use when new requirements arrive, assumptions fail, staffing changes or delivery
  dates are revised.
---

# Change Control


1. Read existing baseline/assessment, progress actuals and the new requested change.
2. Write vault/requirements/<id>/changes/CR-xx.md using vault/templates/change-request.md: trigger, before/after,
   impacted AC/WP, estimate/schedule delta, options, risks, decision owner and decision status.
3. Re-run only invalidated evidence, impact, WBS, estimates and risks. Preserve completed actuals.
4. Reforecast using remaining effort with an explicit as-of date; the V1 schedule script schedules full WBS
   from scratch and MUST NOT be presented as an actuals-aware reforecast. Use a separate remaining-work
   assessment or a clearly documented manual forecast until an actuals-aware engine is added.
5. Show added/removed scope and resource effects separately. Keep baseline immutable and draft a superseding version.
6. Record an existing authorized decision; otherwise retain change as proposed. Do not silently reset commitment dates.
7. Identify downstream handoffs and wiki refresh requests after implemented changes.

## OKF editing contract

Read `vault/docs/okf-profile.md`. Edit project knowledge under `vault/` as OKF Markdown. Structured facts live in the single marked YAML block in each Project Data note; preserve its markers, unknown fields, OKF frontmatter and surrounding prose. Update semantic body links when adding relationships. Frontmatter `status` is the knowledge lifecycle; project workflow status remains inside the data block. Commands run from the repository root.
