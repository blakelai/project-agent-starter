---
type: Project Guide
title: Baselines and execution
description: Baselines and execution。
status: draft
---

# Baselines and execution

Initialize `<PROJ-ID>/project.md` with init_project.py and select all REQs sharing the capacity pool.
Use schedule_project.py for a combined full-work schedule, or add --as-of for explicit remaining-work forecasts.
After owner acceptance of the exact reviewed revision, use baseline.py preview/create/verify to preserve
the selected report and its inputs under `<PROJ-ID>/baseline/<version>/`. Record actual approval provenance;
baselines cannot be overwritten by the tool, and changes supersede them.

The starter has no accepted real baseline and makes no delivery commitment. Execution progress belongs in
requirement progress.md and reviewed status reports. The legacy single-REQ schedule.py remains full-WBS only.

[Workflow, Skills and commands](../docs/project-workflow.md) · [Data contract](../docs/planning-and-delivery.md)

[回到目錄](index.md)
