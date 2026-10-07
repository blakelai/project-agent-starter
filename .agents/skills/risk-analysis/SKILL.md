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
   Before WBS exists, a monitor-only risk may use affected_requirements (FR IDs) with affected_work empty.
   Map risks to actual work packages before planning; do not require invented work just to register an early risk.
3. Use effort-included only if estimation already carries its effort; use calendar-gate when WBS not_before
   captures a bounded external wait; use monitor-only for no added reserve. Explain residual exposure.
4. Do not convert ordinal high/medium/low into invented probabilities or automatic buffer days.
5. Verify risk IDs and affected WP references. Convert scope-changing unknowns into blocking questions.
6. Update register as facts change; mark closed risks with evidence, not because implementation started.

Read AGENTS.md, vault/docs/okf-profile.md and vault/docs/project-workflow.md before editing.
Apply the shared language, evidence, authority and file-format rules; do not duplicate or override them here.
