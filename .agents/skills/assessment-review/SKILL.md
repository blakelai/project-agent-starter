---
name: assessment-review
description: Review readiness and consistency of project assessments before schedule
  generation or baseline. Use after analysis/estimation, when resuming work or validating
  a project plan.
---

# Assessment Review

Read vault/docs/domain-terminology.md. Verify terminology_review, per-term reviews, human confirmation
revisions and shared-question links. Confirmed meanings must match the requirement's context and current
definition/assets; unknown meanings cannot be bypassed with ASSUMED or background usage. A global answer
requires a separate requirement-impact review. A validator pass cannot prove human identity or semantic completeness.


1. Read all artifacts for the requirement, the data contract and relevant planning facts.
2. Reconcile AC coverage, contract consumers, evidence revisions, estimate basis, dependencies, skill capacity,
   external readiness, risk accounting and assumptions. Inspect the highest-impact source claims.
   For BRD-backed work, read vault/docs/brd-intake.md and check every original item is accounted for,
   FR source_refs match source_coverage, images have actual observations, and source/asset hashes are current.
   Pending coverage and unreviewed/unreadable images block readiness. Deferred/excluded items require an
   evidenced scope decision before planning; a populated decision_ref does not prove human approval.
3. Run python scripts/validate.py --requirement <REQ-ID> --stage <requirements|planning|delivery|closure>.
   Fix factual inconsistencies without fabricating evidence; a later current status cannot be downgraded by a flag.
4. Record requirements-phase findings in assessment.md; at planning/delivery/closure use assessment-review.md
   with findings, severity, evidence and resolution. Distinguish machine validation
   from domain judgement; passing the validator is not evidence of estimate accuracy.
5. Set assessment.md ready_for_planning true only if mandatory fields, owners, skill match and capacity window
   are adequate and no open question blocks the planning phase. Otherwise false with blockers and next actions.
6. Keep assessment status draft until an owner explicitly baselines it. Record owner confirmation and input
   versions for a baseline; never manufacture approval.
7. Hand off a concise summary of readiness, unresolved non-blocking assumptions and confidence.
8. At closure, verify progress coverage, completion/cancellation evidence, passed tests plus human AC acceptance
   (or explicit reasoned waiver), resolved delivery blockers and the human closure decision. Keep measured
   actuals distinct from remaining estimates. A closed label alone must never stand in for this evidence.

Read AGENTS.md, vault/docs/okf-profile.md and vault/docs/project-workflow.md before editing.
Apply the shared language, evidence, authority and file-format rules; do not duplicate or override them here.
