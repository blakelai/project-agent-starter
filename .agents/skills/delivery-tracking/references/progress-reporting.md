# Progress Reporting


1. Read baseline/project plan, progress.md, current risk register and evidence of delivered work.
2. Record as-of date, completed deliverables/test evidence, actual_effort_pd, remaining_effort_pd range and blockers.
   Do not infer completion from PR existence, commits, effort spent or unsupported percent-complete values.
3. Compare baseline milestone dates and scope with observed delivery; distinguish date variance, scope variance,
   capacity change and unresolved dependency.
4. Generate progress-report.md from vault/templates/status-report.md with achievements, current forecast range,
   confidence, top risks, decisions needed and named next actions.
5. Show unknown actuals as unknown. Report effort consumption separately from accepted deliverable completion.
6. Trigger change-control if baseline assumptions/scope/capacity are invalidated. Use schedule_project.py --as-of only after all selected progress records have the same cutoff and explicit remaining effort. Preserve actual observations and the prior baseline.
7. At closure, record accepted AC evidence, actual effort/scope boundaries and lessons; propose validated
   historical-delivery samples, but do not mark unmeasured numbers as actuals.
