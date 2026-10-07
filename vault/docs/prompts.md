---
type: Project Guide
title: Project task prompts
description: Project task prompts。
status: draft
---

# Project task prompts

Replace angle-bracket fields with the actual project inputs.

## Project setup

Read AGENTS.md, vault/docs/project-workflow.md and apply knowledge-bootstrap. Inspect the existing repository wikis, populate sources,
map local checkouts, and build the capability routing map. Initialize <PROJ-ID> and record the actual goal,
success criteria, owner and selected requirements with priorities. Verify one lifecycle question and one
cross-repository dependency question with source revisions. Preserve OpenWiki-managed instructions.

## Requirement assessment

For a BRD-backed assessment, provide its repository-relative Markdown path and read vault/docs/brd-intake.md.
Initialize with --source, read original items/tables/images, then map BRD items to FR and AC. Record image
observations and account for every original item; do not modify the original BRD or infer unread image content.

Evaluate <REQ-ID>: <requirement statement>. Apply the assessment workflow with actual repository evidence
and planning facts. Clarify acceptance, failure semantics, external ownership and readiness. Produce useful
independent analysis while questions remain open; schedule only after blocking questions are resolved.

## Domain terminology

Apply domain-terminology to <REQ-ID> and its BRD. Read original text, tables and images. Look up relevant
context-scoped terms; register unknown or conflicting meanings with source quotes and targeted human
questions. Do not invent definitions or translations. Link shared questions and term revisions, produce
the clarification/impact report, and continue independent analysis. Record confirmation only when the
human has explicitly accepted that exact definition version; then reassess each affected requirement.

## Backlog draft

Apply delivery-tracking (backlog handoff substep) to <REQ-ID> for <tracker/project>. Draft the hierarchy, AC, dependencies, effort
ranges and stable local import IDs. Keep proposed owners distinct from external assignment. Do not mutate the tracker.

## Status report

Apply delivery-tracking as of <date> against baseline <version> for <PROJ-ID>. Use accepted deliverables, actual effort,
explicit remaining effort ranges and current blockers. Ask delivery-planning to run schedule_project.py
--project <PROJ-ID> --as-of <date> after every selected REQ has the same cutoff. Preserve actual observations
and baseline; report date/scope changes, uncertainties and decisions needed with owners.

## Change assessment

Apply change-control to <scope/capacity/dependency change>. Compare with baseline <version>, preserve actuals,
and show AC/WP changes and effort/window deltas. Keep the baseline until the authorized decision is recorded.


## Phase-specific planning

Apply delivery-planning to <REQ-ID> for <decomposition / estimation / schedule substep>. Reuse adequate analysis.
Materialize only needed phase files with workflow.py. Run the appropriate validate.py --stage gate; after
assessment-review confirms readiness, run --planning. Select all REQs sharing capacity in <PROJ-ID>/project.md,
then run schedule_project.py; do not treat independent REQ schedules as capacity reservations.

## Acceptance and closure

Apply delivery-tracking and assessment-review to <REQ-ID>. Verify completed or explicitly cancelled work,
passed test evidence plus human AC acceptance (or explicit reasoned waiver), resolved blockers and the human
closure decision. Run validate.py --stage closure, then close_requirement.py. Record measured actuals and
lessons; do not invent approval or mark planned tests passed.

[Workflow and commands](project-workflow.md) · [回到目錄](index.md)
