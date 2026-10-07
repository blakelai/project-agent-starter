---
name: risk-analysis
description: Build an actionable risk register from requirements, impacts, WBS and
  capacity. Use before project planning and whenever uncertainty or external dependencies
  change.
---

# Risk Analysis


1. Inspect unresolved scope, external/cross-team readiness, contract/schema migration, environment, unfamiliar
   technology, release coordination, single-expert dependency and parallel work conflicts relevant to this requirement.
2. Write risks.md with ID, cause-event-effect description, probability/impact (low/medium/high), owner,
   trigger, affected_work, mitigation and treatment.
3. Use effort-included only if estimation already carries its effort; use calendar-gate when WBS not_before
   captures a bounded external wait; use monitor-only for no added reserve. Explain residual exposure.
4. Do not convert ordinal high/medium/low into invented probabilities or automatic buffer days.
5. Verify risk IDs and affected WP references. Convert scope-changing unknowns into blocking questions.
6. Update register as facts change; mark closed risks with evidence, not because implementation started.

## OKF editing contract

Before generating documents, read `documentation_language` from the project-data block in `vault/config/project.md` and apply the Document language policy in `AGENTS.md`. Use the resolved language for human-readable content; preserve machine-readable fields and original evidence.

Read `vault/docs/okf-profile.md`. Edit project knowledge under `vault/` as OKF Markdown. Structured facts live in the single marked YAML block in each Project Data note; preserve its markers, unknown fields, OKF frontmatter and surrounding prose. Update semantic body links when adding relationships. Frontmatter `status` is the knowledge lifecycle; project workflow status remains inside the data block. Commands run from the repository root.
