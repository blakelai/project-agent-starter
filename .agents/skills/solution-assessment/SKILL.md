---
name: solution-assessment
description: Assess solution impacts and architecture choices using requirement and source evidence. Use for a clarified requirement, cross-repository effects, API/schema changes, integrations, or design tradeoffs; reuse an adequate existing solution for small changes.
---

# Solution Assessment

1. Read AGENTS.md, vault/docs/project-workflow.md, and the relevant requirement.md, term_refs, and evidence.md.
   Follow shared language, OKF, source, and human-confirmation rules. Route unknown meanings to domain-terminology.
2. Identify the impact scope first. When a separate assessment is needed, run
   `python scripts/workflow.py --requirement <REQ-ID> --stage solution`. For small changes, record the basis
   for reusing an existing solution in requirement.md; do not require an ADR or invent alternatives.
3. Follow [Impact Analysis](references/impact-analysis.md) to verify original sources, contracts, consumers,
   migrations, and failure behavior. Classify impacts as CONFIRMED/POSSIBLE/UNKNOWN. Current implementation
   does not establish a confirmed business definition.
4. Read [Architecture Review](references/architecture-review.md) for material tradeoffs, comparing viable
   options and operational consequences. Record impacts, options, and reasoning in solution-assessment.md;
   capture material decisions in ADRs with confirmation evidence.
5. Identify work to include in the WBS and unresolved questions, specifying their blocks stages.
   Do not produce unsupported estimates at this step.
6. Continue with delivery-planning. When sources change, revisit only affected analysis rather than restarting
   every assessment step.
