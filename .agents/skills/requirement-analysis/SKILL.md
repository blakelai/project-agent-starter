---
name: requirement-analysis
description: Clarify incoming project requirements into goals, scope and testable
  acceptance criteria. Use for new requirements, vague stakeholder requests, or scope
  refinement.
---

# Requirement Analysis


1. Use scripts/init_requirement.py <REQ-ID> to create a new intake, without overwriting existing work.
2. Read only relevant product/lifecycle wiki sections and record evidence.yaml.
3. Populate requirement.yaml with business goal, actors, current/expected behavior, constraints and non-goals.
   Separate business outcome from proposed implementation. Mirror the narrative in requirement.md.
4. Assign stable FR-xx and AC-xx IDs. Make each AC observable: trigger, input, expected outcome, failure case.
5. Mark facts CONFIRMED/ASSUMED/UNKNOWN with evidence IDs or assumption owner. Ask only questions whose
   answers materially change behavior, acceptance, architecture, effort, dependency or timeline.
6. Record questions with blocking/status/owner; resolved questions require answer and source.
7. Keep useful analysis moving while scope is blocked. Do not silently select synchronous/asynchronous
   behavior or failure semantics. Do not enter detailed solution design at this step.
8. Mark clarified only after scope and AC are sufficiently bounded; leave blocking questions visible.

Use templates/requirement/ and docs/data-contract.md. Never mark an intake assessed merely because files exist.
