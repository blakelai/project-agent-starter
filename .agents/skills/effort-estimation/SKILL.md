---
name: effort-estimation
description: Estimate auditable effort ranges using comparable delivery evidence.
  Use after WBS or to re-estimate changed work; distinguish estimates from schedule
  dates.
---

# Effort Estimation


1. Read WBS, vault/planning/work-types.md, historical-delivery.md and estimation-rules.md.
2. Select comparable samples by scope, work type, complexity and definition of measured person-day.
   Cite sample IDs. Exclude synthetic samples from real project estimates.
3. For each WP document basis, scope boundary, similarities/differences and justified adjustments.
4. Emit low/expected/high effort_pd values, confidence and historical_refs in estimation.md.
   Use historical-range or expert-judgement basis. With insufficient samples, record lower confidence,
   estimate-owner reasoning and a bounded range; if no defensible basis exists, record a blocking question.
5. Keep normal development/testing effort separate from external calendar waiting. Map contingencies to risk IDs.
6. Do not call judgement scenarios P50/P80. If measured quantiles are later used, document sampling and
   calibration; project quantiles need an explicit joint aggregation model, including correlated risk.
7. Run validation. Let scripts compute totals; do not hand-edit summary numbers or schedule dates.

A factor must describe what it changes and why. Do not multiply every package by a generic uncertainty factor.

## OKF editing contract

Before generating documents, read `documentation_language` from the project-data block in `vault/config/project.md` and apply the Document language policy in `AGENTS.md`. Use the resolved language for human-readable content; preserve machine-readable fields and original evidence.

Read `vault/docs/okf-profile.md`. Edit project knowledge under `vault/` as OKF Markdown. Structured facts live in the single marked YAML block in each Project Data note; preserve its markers, unknown fields, OKF frontmatter and surrounding prose. Update semantic body links when adding relationships. Frontmatter `status` is the knowledge lifecycle; project workflow status remains inside the data block. Commands run from the repository root.
