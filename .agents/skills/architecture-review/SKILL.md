---
name: architecture-review
description: Review architecture alternatives and document project decisions. Use
  for external integrations, new persistence, contract changes, reliability tradeoffs
  or material implementation uncertainty.
---

# Architecture Review

Read the requirement's term_refs and vault/docs/domain-terminology.md before choosing models and contracts.
Use confirmed meanings within their contexts; route ambiguity to domain-terminology. Record current/proposed
system_mappings with source revisions or decision references, separately from business definitions. Do not
force every term into an aggregate/entity/table or redefine business meaning to match existing code.


1. Read the clarified requirement, impact analysis, source evidence and relevant existing ADRs.
2. Compare two viable alternatives (or explain why only one is viable), including operational consequences.
3. Evaluate only relevant concerns: consistency, transaction boundaries, retries/idempotency, compatibility,
   security, scale, rollout and recovery. Do not apply irrelevant framework checklists.
4. Write architecture-options.md with decision driver, alternatives, tradeoffs, recommendation and unresolved facts.
5. Write decisions.md with stable decision IDs, status proposed/accepted/superseded, owner and decision evidence.
   Preserve existing accepted decisions; record a superseding decision instead of rewriting history.
6. Feed required implementation and validation work into WBS, and material uncertainty into risks/questions.
7. Keep recommendations proposed until the authorized decision is evidenced. Reuse decisions already provided.

For substantial decisions use vault/templates/adr.md. This is a scoped architecture review, not a code implementation step.

## OKF editing contract

Before generating documents, read `documentation_language` from the project-data block in `vault/config/project.md` and apply the Document language policy in `AGENTS.md`. Use the resolved language for human-readable content; preserve machine-readable fields and original evidence.

Read `vault/docs/okf-profile.md`. Edit project knowledge under `vault/` as OKF Markdown. Structured facts live in the single marked YAML block in each Project Data note; preserve its markers, unknown fields, OKF frontmatter and surrounding prose. Update semantic body links when adding relationships. Frontmatter `status` is the knowledge lifecycle; project workflow status remains inside the data block. Commands run from the repository root.
