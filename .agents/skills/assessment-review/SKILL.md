---
name: assessment-review
description: Review readiness and consistency of project assessments before schedule
  generation or baseline. Use after analysis/estimation, when resuming work or validating
  a project plan.
---

# Assessment Review


1. Read all artifacts for the requirement, the data contract and relevant planning facts.
2. Reconcile AC coverage, contract consumers, evidence revisions, estimate basis, dependencies, skill capacity,
   external readiness, risk accounting and assumptions. Inspect the highest-impact source claims.
3. Run python scripts/validate.py --requirement <REQ-ID>. Fix factual inconsistencies without fabricating evidence.
4. Write assessment-review.md with findings, severity, evidence and resolution. Distinguish machine validation
   from domain judgement; passing the validator is not evidence of estimate accuracy.
5. Set assessment.yaml ready_for_planning true only if mandatory fields, owners, skill match and capacity window
   are adequate and no open blocking question remains. Otherwise false with blockers and next actions.
6. Keep assessment status draft until an owner explicitly baselines it. Record owner confirmation and input
   versions for a baseline; never manufacture approval.
7. Hand off a concise summary of readiness, unresolved non-blocking assumptions and confidence.
