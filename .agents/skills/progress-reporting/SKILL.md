---
name: progress-reporting
description: Generate evidence-based project status reports and remaining-effort forecasts.
  Use for weekly reviews, management reporting, slippage or project closure.
---

# Progress Reporting


1. Read baseline/project plan, progress.md, current risk register and evidence of delivered work.
2. Record as-of date, completed deliverables/test evidence, actual_effort_pd, remaining_effort_pd range and blockers.
   Do not infer completion from PR existence, commits, effort spent or unsupported percent-complete values.
3. Compare baseline milestone dates and scope with observed delivery; distinguish date variance, scope variance,
   capacity change and unresolved dependency.
4. Generate progress-report.md from vault/templates/status-report.md with achievements, current forecast range,
   confidence, top risks, decisions needed and named next actions.
5. Show unknown actuals as unknown. Report effort consumption separately from accepted deliverable completion.
6. Trigger change-control if baseline assumptions/scope/capacity are invalidated. Do not use the full-WBS
   scheduler as a remaining-work forecast; use a separate remaining-work scenario with explicit provenance.
7. At closure, record accepted AC evidence, actual effort/scope boundaries and lessons; propose validated
   historical-delivery samples, but do not mark unmeasured numbers as actuals.

## OKF editing contract

Read `vault/docs/okf-profile.md`. Edit project knowledge under `vault/` as OKF Markdown. Structured facts live in the single marked YAML block in each Project Data note; preserve its markers, unknown fields, OKF frontmatter and surrounding prose. Update semantic body links when adding relationships. Frontmatter `status` is the knowledge lifecycle; project workflow status remains inside the data block. Commands run from the repository root.
