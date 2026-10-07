---
name: requirement-analysis
description: Clarify incoming project requirements into goals, scope and testable
  acceptance criteria. Use for new requirements, vague stakeholder requests, or scope
  refinement.
---

# Requirement Analysis


1. Use scripts/init_requirement.py <REQ-ID> to create a new intake, without overwriting existing work.
2. Read only relevant product/lifecycle wiki sections and record evidence.md.
3. Populate requirement.md with business goal, actors, current/expected behavior, constraints and non-goals.
   Separate business outcome from proposed implementation. Put authoritative fields in its project-data block
   and use the same page's prose for context and rationale.
4. Assign stable FR-xx and AC-xx IDs. Make each AC observable: trigger, input, expected outcome, failure case.
5. Mark facts CONFIRMED/ASSUMED/UNKNOWN with evidence IDs or assumption owner. Ask only questions whose
   answers materially change behavior, acceptance, architecture, effort, dependency or timeline.
6. Record questions with blocking/status/owner; resolved questions require answer and source.
7. Keep useful analysis moving while scope is blocked. Do not silently select synchronous/asynchronous
   behavior or failure semantics. Do not enter detailed solution design at this step.
8. Mark clarified only after scope and AC are sufficiently bounded; leave blocking questions visible.

Use vault/templates/requirement/ and vault/docs/data-contract.md. Never mark an intake assessed merely because files exist.

## OKF editing contract

Before generating documents, read `documentation_language` from the project-data block in `vault/config/project.md` and apply the Document language policy in `AGENTS.md`. Use the resolved language for human-readable content; preserve machine-readable fields and original evidence.

Read `vault/docs/okf-profile.md`. Edit project knowledge under `vault/` as OKF Markdown. Structured facts live in the single marked YAML block in each Project Data note; preserve its markers, unknown fields, OKF frontmatter and surrounding prose. Update semantic body links when adding relationships. Frontmatter `status` is the knowledge lifecycle; project workflow status remains inside the data block. Commands run from the repository root.
