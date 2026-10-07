# Work Breakdown


1. Read requirement.md, solution-assessment.md when present, existing solution evidence and relevant ADRs.
2. Build work-breakdown.md using the contract in vault/docs/data-contract.md.
3. Give every package a concrete deliverable, done_when condition, work_type/complexity, skills, evidence IDs
   and acceptance_ids. Include review, package-level testing and necessary migration/rollout work.
4. Separate shared E2E tests from package testing; describe estimate boundaries to avoid double counting.
5. Define finish-to-start dependencies and not_before readiness gates; never encode waiting time as effort.
6. Require one explicit assigned_to person for the V1 scheduler. Use candidate roles while unassigned,
   but leave scheduling readiness false. Do not auto-assign work in an external tracker.
7. Link every AC to at least one package in traceability.md and keep test evidence planned until executed.
8. Validate DAG and references with scripts/validate.py. Flag oversized/uncertain work for a spike or split.

Avoid tasks such as 'implement feature' without a verifiable result. Do not estimate during decomposition.
