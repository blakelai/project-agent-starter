# Artifact contract v1

Use UTF-8 Markdown and YAML. All YAML artifacts carry `schema_version: 1`.
`requirement.yaml` is authoritative for IDs, facts, AC and blocking questions;
Markdown is a narrative summary. Reconcile both when changing scope.

## Authority and provenance

- `config/project.yaml`: routing and project settings.
- `knowledge/sources.yaml`: shared source IDs, repo URLs and wiki roots; NOT an OpenWiki configuration file.
- `.local/sources.yaml`: machine-specific checkout paths, ignored by Git.
- `planning/*`: owned planning facts with validity windows and explicit units.
- `evidence.yaml`: each evidence record has `id`, `source_id`, `path`, `source_revision`,
  `observed_at`, `state` and `claim`. `source_revision` refers to the checkout commit;
  wiki timestamps alone do not establish source freshness. Use `synthetic: true` for fixtures.
- `requirement.yaml`: `status: intake|clarified|assessed|baseline|closed`; `facts` use
  `CONFIRMED|ASSUMED|UNKNOWN`; `questions` include `blocking` and `status: open|resolved`.
- `impact-analysis.md`: use `CONFIRMED|POSSIBLE|UNKNOWN` plus evidence IDs; record absent
  evidence and incompatible/contradictory sources explicitly.
- `architecture-options.md`: describe alternatives and consequences. `decisions.md` records
  `proposed|accepted|superseded` decisions with owner and confirmation evidence.
- `work-breakdown.yaml`: `work_packages` have `id`, `name`, `work_type`, `complexity`,
  `acceptance_ids`, `evidence_ids`, `deliverable`, `done_when`, `depends_on`, `skills`,
  `assigned_to`, `not_before` and `priority`. Dependencies are finish-to-start, next workday.
- `estimation.yaml`: `estimates` reference WP IDs, `basis`, `historical_refs`, `confidence`
  and `effort_pd: {low, expected, high}`. These are judgement scenarios, not quantiles.
  Do not store totals manually; scheduler computes them. If no basis exists, keep
  requirement in intake and write the unresolved estimate as a question.
- `risks.yaml`: each risk has probability/impact, owner, trigger, mitigation, affected work,
  and `treatment: effort-included|calendar-gate|monitor-only`. Not-before gates belong in WBS.
- `traceability.yaml`: links AC -> work packages -> test evidence; `planned` is not `passed`.
- `assessment.yaml`: readiness and explicit owner confirmation when establishing a baseline.
- `schedule-expected.yaml` / `schedule-high.yaml`: generated algorithm outputs with input hashes.
- `project-plan.md`: executive assessment; interpret scenario windows and confidence.
- `progress.yaml`: actuals and remaining-effort range by WP, as-of date, external blockers.
- `projects/<id>/baseline/`: immutable copies + hash manifest created only after explicit owner baseline decision.
- `changes/`: proposed scope/resource/date changes, impact, decision and superseded baseline.

## Scheduling model

One assigned person per WP; each person executes at most one WP per workday.
A WP can consume only that person's net fraction on eligible days. Skill matching is set inclusion,
not an inferred skill-level multiplier. Weekends, holidays and leave add no effort.
The scheduler consumes the entire calendar day for the selected task, even if it finishes early;
this conservative model intentionally does not reuse a final-day remainder.

`not_before` is an external readiness date, not development effort. Missing an external readiness
fact blocks scheduling until a bounded assumption is recorded and acknowledged as a scenario.
Unresolved blocking questions and non-ready assessments block the scheduling command.
The deterministic greedy schedule is feasible under these simplified rules, not an optimal RCPSP result,
and no project confidence percentile is claimed.

The precedence-only lower bound uses the same assigned person's calendar/capacity while ignoring
competition for that person. Its terminal predecessor chain explains dependency pressure; it is NOT
the critical chain of the resource-constrained plan. Compare it with the final resource-constrained end.

## Scope of validators

`validate.py` checks structural types, IDs, DAG, references, estimate ordering, skill/capacity alignment,
required artifacts and readiness for scheduling. It cannot verify that a wiki claim is factually true,
that estimates are calibrated, or that an approval actually came from the named human.
