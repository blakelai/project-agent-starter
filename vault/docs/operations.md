---
type: Project Guide
title: Project operations
description: Project operations。
status: draft
---

# Project operations

## Owners

| Artifact | Accountable role | Update trigger |
|---|---|---|
| Wiki/source evidence | Source module owner / architect | Code/contract change or evidence drift |
| Requirement / AC | Product/domain owner | Clarification or scope change |
| Estimates / history | Technical lead + work owner | Scope change or measured closure |
| Capacity / calendar | Team lead | Allocation, leave, support or planning window change |
| Risks | Named risk owner | Trigger, mitigation or external readiness update |
| Baseline | Project owner | Explicit decision accepting scope/resources/window |
| Progress | Delivery lead / work owners | Review cadence or material blocker |

## Resume

Read assessment.md, requirement questions, evidence revisions, decisions, risks and last progress as-of date.
Do not restart the whole pipeline when inputs are unchanged. Re-run only invalidated phases, then reconcile.

## Baseline

Use delivery-planning and assessment-review. Run baseline.py preview against the selected project report,
obtain the owner's decision on that exact revision, then use baseline.py create with its revision and real
by/at/source metadata. Use baseline.py verify to check the saved bytes. See [commands](project-workflow.md).
Snapshots under vault/projects/<PROJ-ID>/baseline/<version> cannot be overwritten by the tool; live progress
can continue changing. The tool records supplied confirmation, not a new approval or external tracker action.

## Progress and change

Use delivery-tracking for observed work status, accepted outcomes, actuals and explicit remaining ranges.
All selected REQs need the same as_of for schedule_project.py --as-of. Forecast from the following day;
exclude done/cancelled work, retain unknown actuals, and reject unknown remaining work or blocked resume dates.
The full-WBS single-REQ schedule.py remains an isolated scenario, not a remaining-work forecast.

Compare with the immutable baseline; route invalidated scope, capacity or dependencies through change-control.
Reuse adequate analysis and rerun only affected phases. Preserve actual observations and old approval evidence.
Inputs and closure conditions are defined in [planning and delivery](planning-and-delivery.md).

## CI adoption

Run `python scripts/validate.py --all` on artifact changes; run unit tests when tools change.
Install `requirements.txt` in your approved Python environment. Sample pipeline is in ci/azure-pipelines.yml.
Agent judgement and owner review remain necessary; lint success is not business acceptance or calibrated forecast.

## Closure

Run validate.py --stage closure, then close_requirement.py. All work must be done or explicitly cancelled;
each AC needs passed tests and human acceptance, or a reasoned human waiver. Resolve delivery blockers and
record the human closure decision with by/at/source/summary. Record actual scope/effort measurement method,
elapsed duration, major scope changes and lessons.
Convert only measured comparable outcomes into historical-delivery records. Do not use ticket elapsed duration
as effort, story points as PD, or synthetic fixtures as history. Refresh changed source wikis in their owners' workflow.

[回到目錄](index.md)
