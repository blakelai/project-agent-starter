---
type: Project Guide
title: Artifact contract v1
description: Artifact contract v1。
status: draft
---

# Artifact contract v1

Use OKF v0.2 Markdown in `vault/`, with the local [project-agent/v1 profile](okf-profile.md).
Structured artifacts contain one marked YAML block with `schema_version: 1`.
`requirement.md` holds authoritative IDs, facts, AC and blocking questions in that block;
the same page's prose explains context. There is no parallel YAML source file.
Field names below refer to the data block unless explicitly called frontmatter.

## Authority and provenance

- `vault/config/project.md`: routing and project settings. `documentation_language` is the default language
  for Agent-authored documents, using a language-code string such as `zh-TW`, `en` or `ja`.
  A missing, null or blank value defaults to `zh-TW`; an explicit per-task language overrides it.
  See the [OKF profile](okf-profile.md) for editing scope and machine-readable field preservation.
- `vault/knowledge/sources.md`: shared source IDs, repo URLs and wiki roots; BRD entries use `kind: brd`
  and a Repository-relative `path`. It is not an OpenWiki configuration file.
- `vault/intake/<BRD-ID>/brd.md`: original OKF BRD with stable lowercase `## br-...` items and local images
  in `assets/`. Its prose is authoritative original input; interpretation remains in the assessment.
- `.local/sources.md`: machine-specific checkout paths, ignored by Git.
- `vault/planning/*`: owned planning facts with validity windows and explicit units.
- `evidence.md`: each evidence record has `id`, `source_id`, `path`, `source_revision`,
  `observed_at`, `state` and `claim`. `source_revision` refers to the checkout commit;
  wiki timestamps alone do not establish source freshness. Use `synthetic: true` for fixtures.
  For `kind: brd`, source_revision is the captured manifest SHA-256 covering the BRD and referenced images;
  path must identify the document, an original item anchor, or a captured image. See [BRD intake](brd-intake.md).
- `requirement.md`: `status: intake|clarified|assessed|baseline|in-progress|closed`; `facts` use
  `CONFIRMED|ASSUMED|UNKNOWN`; `questions` include `blocking` and `status: open|resolved`, with optional `blocks` stages and `affected_work`.
  Requirements clarification does not require WBS or estimates; see [phase gates](planning-and-delivery.md).
  Optional `source_documents` records BRD snapshots and image observations. BRD-backed FRs each need
  `source_refs: [{document_id, item_id}]`; one FR may refer to multiple original items.
- `solution-assessment.md`: combine scoped impacts and alternatives; use `CONFIRMED|POSSIBLE|UNKNOWN` plus evidence IDs; record absent
  evidence and incompatible/contradictory sources explicitly.
- Material decisions use an ADR with `proposed|accepted|superseded`, owner and decision evidence.
  Existing impact-analysis, architecture-options and decisions documents remain valid historical references.
- `work-breakdown.md`: `work_packages` have `id`, `name`, `work_type`, `complexity`,
  `acceptance_ids`, `evidence_ids`, `deliverable`, `done_when`, `depends_on`, `skills`,
  `assigned_to`, `not_before` and `priority`. Dependencies are finish-to-start, next workday.
- `estimation.md`: `estimates` reference WP IDs, `basis`, `historical_refs`, `confidence`
  and `effort_pd: {low, expected, high}`. These are judgement scenarios, not quantiles.
  Do not store totals manually; scheduler computes them. If no basis exists, keep
  planning readiness false and write the unresolved estimate as a planning-blocking question.
  A semantically clarified requirement can remain clarified while estimation is pending.
- `risks.md`: each risk has probability/impact, owner, trigger, mitigation, affected work,
  and `treatment: effort-included|calendar-gate|monitor-only`. Early monitor-only risks may link FR IDs in
  `affected_requirements`; planning requires affected WP references. Not-before gates belong in WBS.
- `traceability.md`: links AC -> work packages -> test evidence; `planned` is not `passed`.
  For captured BRDs, `source_coverage` accounts for every original item and agrees with FR source_refs.
  Dispositions are pending/analyzed/needs-clarification/deferred/excluded. See [the full contract](brd-intake.md).
- `assessment.md`: readiness and explicit owner confirmation when establishing a baseline.
- `vault/knowledge/glossary/`: context-scoped domain terms, shared questions, separately evidenced system
  mappings, and human confirmation of exact business-definition revisions. See [terminology](domain-terminology.md).
- `requirement.md` also holds `term_refs` and `terminology_review`. Meaning references need valid confirmation
  and impact review; shared `term_question` answers stay in the term page. Unconfirmed meanings cannot be
  converted to ASSUMED facts or non-blocking background to bypass readiness. Even a no-term assessment
  must record its terminology review. Existing assessments must add this before their next planning run.
- `schedule-expected.md` / `schedule-high.md`: generated algorithm outputs with input hashes.
- `project-plan.md`: executive assessment; interpret scenario windows and confidence.
- `progress.md`: actuals, explicit remaining-effort range, work status, as-of date, blockers and closure.
  Each AC also has a human acceptance/waiver record at closure; planned tests cannot imply acceptance.
- `vault/projects/<PROJ-ID>/project.md`: goal, success criteria, owner, selected REQs with priority, cross-REQ dependencies.
- `forecast-<scenario>.md`: remaining-work scenario from a common inclusive observation cutoff.
- `vault/projects/<id>/baseline/`: immutable copies + hash manifest created only after explicit owner baseline decision.
- Change notes use `vault/templates/change-request.md` within the relevant project: proposed scope/resource/date changes,
  impact, decision and superseded baseline.

Full project, question, progress, acceptance and baseline field rules: [planning and delivery](planning-and-delivery.md).
Commands, artifact materialization and phase routing: [project workflow](project-workflow.md).

## Scheduling model

One assigned person per WP; each person executes at most one WP per workday.
A WP can consume only that person's net fraction on eligible days. Skill matching is set inclusion,
not an inferred skill-level multiplier. Weekends, holidays and leave add no effort.
The scheduler consumes the entire calendar day for the selected task, even if it finishes early;
this conservative model intentionally does not reuse a final-day remainder.

`not_before` is an external readiness date, not development effort. Missing an external readiness
fact blocks scheduling until a bounded assumption is recorded and acknowledged as a scenario.
Unresolved blocking questions and non-ready assessments block the scheduling command.
For shared capacity across REQs, use schedule_project.py with all competing work selected.
Separate project runs do not reserve capacity against one another. Forecast mode substitutes explicit remaining
effort after as_of and preserves historical observations; it never subtracts actuals from original estimates.
The deterministic greedy schedule is feasible under these simplified rules, not an optimal RCPSP result,
and no project confidence percentile is claimed.

The precedence-only lower bound uses the same assigned person's calendar/capacity while ignoring
competition for that person. Its terminal predecessor chain explains dependency pressure; it is NOT
the critical chain of the resource-constrained plan. Compare it with the final resource-constrained end.

## Scope of validators

`validate.py` checks structural types, IDs, DAG, references, estimate ordering, skill/capacity alignment,
phase-dependent required artifacts, delivery/closure evidence metadata and readiness for scheduling.
Project scope and combined DAG validation occurs in schedule_project.py; baseline hash integrity is checked
separately by baseline.py verify. It cannot verify that a wiki claim is factually true,
that estimates are calibrated, or that an approval actually came from the named human.
BRD validation also checks original item IDs, coverage, image review records and source freshness.
It does not interpret images, evaluate the semantic quality of a mapping, or prove a reviewer inspected a file.

The repository-wide check also validates supported OKF metadata and the local data profile, including
duplicate YAML keys and duplicate data blocks. It is not a full OKF conformance suite.
Schedule hashes cover current validation inputs as well as calculation inputs.
Terminology checks cover definition/context/asset hashes, shared-question links, scope, confirmation metadata
and readiness. They do not discover every ambiguous phrase or authenticate a human. Definition content uses
one marked term-definition block in the same Markdown note; structured values remain in project-data.

[回到目錄](index.md)
