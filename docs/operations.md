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

Read assessment.yaml, requirement questions, evidence revisions, decisions, risks and last progress as-of date.
Do not restart the whole pipeline when inputs are unchanged. Re-run only invalidated phases, then reconcile.

## Baseline

Draft artifacts require no routine approvals. Establishing a baseline requires the project owner's explicit
decision; keep approval provenance and exact input/output versions. Existing authorized acceptance suffices.
Copy approved artifacts and hash manifest under projects/<id>/baseline/<version> and preserve previous versions.
The starter does not automatically create baselines or change external trackers.

## Progress and change

Use actual accepted deliverables/test evidence, actual effort and remaining effort range. Unsupported
percent-complete statements are not facts. Report against immutable baseline; route new scope/capacity or
invalid assumptions through change-control. Do not rerun the full-WBS scheduler and call it an actuals-aware
reforecast. V1 requires a separately prepared remaining-work assessment or a documented manual forecast.

## CI adoption

Run `python scripts/validate.py --all` on artifact changes; run unit tests when tools change.
Install `requirements.txt` in your approved Python environment. Sample pipeline is in ci/azure-pipelines.yml.
Agent judgement and owner review remain necessary; lint success is not business acceptance or calibrated forecast.

## Closure

Record accepted AC, actual scope/effort measurement method, elapsed duration, major scope changes and lessons.
Convert only measured comparable outcomes into historical-delivery records. Do not use ticket elapsed duration
as effort, story points as PD, or synthetic fixtures as history. Refresh changed source wikis in their owners' workflow.
