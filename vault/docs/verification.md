---
type: Project Guide
title: Verification
description: Verification。
status: draft
---

# Verification

OKF migration validation on 2026-10-07: 23 automated tests passed.

Run `python scripts/validate.py --all` and `python -m unittest discover -s tests -v`.

The repository contains no populated sample project. Tests create isolated inputs in temporary directories
and cover DAG failures, resource exclusivity, calendar/capacity behavior, readiness, invalid references,
no overwrite, and missing owner confirmation. They do not depend on any populated requirement directory.

The OKF checks cover preservation of metadata/prose/extensions, duplicate data blocks and YAML keys,
workflow versus knowledge lifecycle status, provenance fields, the root-index exception, and Markdown
schedule generation. End-to-end checks change a Markdown estimate and verify the resulting dates and hashes.

Migration comparison preserved the parsed content of all 17 original project YAML files.
Local navigation links were checked. The 12 repository Skill definitions retain their host metadata and
use the updated OKF editing contract. No live Obsidian application was launched; presentation compatibility
uses standard Markdown, YAML properties and code blocks, without a community-plugin dependency.

No live OpenWiki, source repository or project-management platform is required for these checks. Integration
and factual evidence must be verified during actual project onboarding. Passing tests does not establish
forecast calibration, source truth or human approval identity.

[回到目錄](index.md)
