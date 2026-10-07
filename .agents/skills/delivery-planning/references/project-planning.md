# Shared Capacity and Remaining-Work Forecasting

1. Read the goal, scope, success criteria, requirement priorities, and cross-REQ dependencies in
   vault/projects/<PROJ-ID>/project.md.
2. Confirm that every selected REQ has passed planning review and that net capacity already excludes
   out-of-scope activities. Count capacity only once within a plan.
3. Use schedule_project.py for expected/high scenarios. Projects outside the selected scope do not
   automatically receive capacity reservations.
4. For forecasts, use the same as_of across all REQs, with actual work status and remaining effort for
   each WP. The cutoff includes that day; scheduling starts the following day. Do not reschedule done
   or cancelled work. A cancelled predecessor does not automatically satisfy a dependency. Unknown
   remaining effort or blocker release dates prevent forecasting.
5. Keep unknown actual effort unknown; do not derive person-days from ticket elapsed time. Report known
   actual effort separately from remaining work to be scheduled.
6. Explain the model as a feasible greedy scenario with one assignee per WP, full-day reservations, and
   finish-to-start dependencies. It does not provide an optimal solution, probability percentile, or
   intraday scheduling.
7. Run baseline.py preview and obtain human confirmation of the report and exact input revision before
   recording by/at/source/revision with create. Use verify to check the saved bytes; it cannot authenticate
   the human or establish the correctness of the business decision.
