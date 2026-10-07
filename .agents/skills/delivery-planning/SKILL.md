---
name: delivery-planning
description: Build traceable work packages, estimate effort, and plan shared capacity across requirements. Use for decomposition, estimation updates, project schedules, or evidence-based remaining-work forecasts; invoke only the needed substep.
---

# Delivery Planning

1. Read AGENTS.md, vault/docs/project-workflow.md, vault/docs/planning-and-delivery.md, the requirements,
   and relevant solution assessments. Follow shared language, OKF, evidence, and authority rules.
   Check the requirements gate first and keep unresolved dependencies blocking.
2. Run `python scripts/workflow.py --requirement <REQ-ID> --stage planning` to create missing files;
   this action does not approve work or change workflow status.
3. For decomposition, read [Work Breakdown](references/work-breakdown.md). Define WPs, AC mappings,
   and dependencies without introducing unsupported effort estimates.
4. For estimation, read [Effort Estimation](references/effort-estimation.md). Preserve the basis and
   low/expected/high scenarios. Use risk-analysis to update treatments without counting the same risk
   in both estimated effort and an additional buffer.
5. Run `python scripts/validate.py --requirement <REQ-ID> --stage planning`, then use assessment-review.
   Set ready_for_planning only after review passes. Draft plans and forecast scenarios do not establish
   external delivery commitments.
6. For scheduling, read [Shared Capacity and Forecasting](references/project-planning.md). Include all
   competing REQs in one project.md, with explicit priorities, cross-REQ dependencies, and the complete
   scope that shares the capacity pool.
7. Run `python scripts/schedule_project.py --project <PROJ-ID> --scenario expected`, then the high scenario.
   Keep schedule.py for isolated single-REQ scenarios; separate schedules cannot establish the absence
   of capacity conflicts.
8. For forecasts during execution, obtain progress, actual observations, and explicitly estimated remaining
   effort from delivery-tracking, all at the same cutoff. Use
   `schedule_project.py --project <PROJ-ID> --as-of <YYYY-MM-DD>`. Never infer remaining effort by subtracting
   time spent from the original estimate.
9. Explain how resources and external waits affect dates. After human confirmation of the exact version,
   use baseline.py preview/create to preserve the baseline. Retain previous baselines and actual observations;
   route commitment changes through change-control.
