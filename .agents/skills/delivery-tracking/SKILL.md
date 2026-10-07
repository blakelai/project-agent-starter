---
name: delivery-tracking
description: Track delivery from backlog handoff through progress, acceptance and closure. Use for tracker mappings, status reports, actual and remaining effort updates, milestone reviews, acceptance evidence, or closing completed/cancelled scope.
---

# Delivery Tracking

1. Read AGENTS.md, vault/docs/project-workflow.md, vault/docs/planning-and-delivery.md, the plan, and the baseline.
   Follow shared language, OKF, evidence, and external-action authority rules. Run
   `workflow.py --requirement <REQ-ID> --stage delivery` to create missing delivery artifacts.
2. For handoff, read [Backlog Mapping](references/backlog-handoff.md). Preserve stable REQ/WP-to-tracker
   mappings. Leave external IDs unknown until verified. Do not create tickets, change sprints, assign others,
   or send messages without authorization.
3. For progress updates, read [Outcomes and Reporting](references/progress-reporting.md). Record each WP's
   status, actual effort, remaining-effort scenarios, and blockers at the same as_of date. Completion requires
   a date and evidence; retain null for unknown actual effort and explain why it is unknown.
4. Distinguish implementation completion, test success, and business acceptance. Record human AC acceptance
   or waivers in traceability.md. Do not substitute PRs, commits, effort spent, or successful Agent checks
   for human acceptance.
5. Validate progress with `validate.py --requirement <REQ-ID> --stage delivery`, then use delivery-planning
   to schedule remaining work. Do not produce misleadingly precise finish dates when remaining effort or
   blocker release dates are unknown. Route capacity or scope changes through change-control.
6. Before closure, require complete human acceptance or reasoned waivers, work completion/cancellation
   records, and the human closure decision. Run `validate.py --requirement <REQ-ID> --stage closure`;
   after it passes, run `close_requirement.py --requirement <REQ-ID>`.
7. Record actual scope, measurement methods, and lessons. Add only comparable, measured outcomes to
   delivery history. Preserve historical baselines.
