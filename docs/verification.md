# Verification

Validated on 2026-10-04: all 12 Skill formats and 15 automated tests passed.

Run `python scripts/validate.py --all` and `python -m unittest discover -s tests -v`.

The repository contains no populated sample project. Tests create isolated inputs in temporary directories
and cover DAG failures, resource exclusivity, calendar/capacity behavior, readiness, invalid references,
no overwrite, and missing owner confirmation. They do not depend on any populated requirement directory.

No live OpenWiki, source repository or project-management platform is required for these checks. Integration
and factual evidence must be verified during actual project onboarding. Passing tests does not establish
forecast calibration, source truth or human approval identity.
