# Architecture Review

Read the requirement's term_refs and vault/docs/domain-terminology.md before choosing models and contracts.
Use confirmed meanings within their contexts; route ambiguity to domain-terminology. Record current/proposed
system_mappings with source revisions or decision references, separately from business definitions. Do not
force every term into an aggregate/entity/table or redefine business meaning to match existing code.


1. Read the clarified requirement, impact analysis, source evidence and relevant existing ADRs.
2. Compare two viable alternatives (or explain why only one is viable), including operational consequences.
3. Evaluate only relevant concerns: consistency, transaction boundaries, retries/idempotency, compatibility,
   security, scale, rollout and recovery. Do not apply irrelevant framework checklists.
4. Write solution-assessment.md with decision driver, alternatives, tradeoffs, recommendation and unresolved facts.
5. Write an ADR with stable decision IDs, status proposed/accepted/superseded, owner and decision evidence.
   Preserve existing accepted decisions; record a superseding decision instead of rewriting history.
6. Feed required implementation and validation work into WBS, and material uncertainty into risks/questions.
7. Keep recommendations proposed until the authorized decision is evidenced. Reuse decisions already provided.

For substantial decisions use vault/templates/adr.md. This is a scoped architecture review, not a code implementation step.
