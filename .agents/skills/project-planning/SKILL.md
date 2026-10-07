---
name: project-planning
description: Create a resource-constrained schedule from validated WBS, effort ranges,
  capacity and calendar. Use only for planning-ready requirements with resolved blocking
  questions.
---

# Project Planning


1. Read assessment.md and run python scripts/validate.py --requirement <REQ-ID> --planning.
2. If blocked, document readiness issues and continue independent analysis; do not produce a commitment date.
3. Confirm assignments, net capacity validity window, leave, holidays, external not_before dates and chosen start.
4. Run python scripts/schedule.py --requirement <REQ-ID> --scenario expected and again with --scenario high.
5. Read both outputs. Report effort range, scenario finish window, precedence lower bound, resource delay,
   external gates and confidence. These are deterministic scenarios, not delivery percentiles.
6. Write project-plan.md with scope, milestones, resources, assumptions, risks, options and next decisions.
7. Explain the greedy single-person-per-WP/full-day model. Do not claim an optimal schedule or label the
   precedence-only chain as a resource-constrained critical path.
8. Record baseline only after explicit project-owner confirmation and copy exact inputs/output hashes into
   vault/projects/<project-id>/baseline/<version>. Keep draft plans reviewable without requiring routine approvals.

## OKF editing contract

Read `vault/docs/okf-profile.md`. Edit project knowledge under `vault/` as OKF Markdown. Structured facts live in the single marked YAML block in each Project Data note; preserve its markers, unknown fields, OKF frontmatter and surrounding prose. Update semantic body links when adding relationships. Frontmatter `status` is the knowledge lifecycle; project workflow status remains inside the data block. Commands run from the repository root.
