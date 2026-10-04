# HVE Core patterns worth adopting

Checked: 2026-10-04. This starter provides original local workflows; no HVE files are bundled or installed.
HVE is an SDLC pattern source; it does not supply this starter's effort/capacity scheduling calculations.

| Official component | Kind | Useful pattern | Starter application |
|---|---|---|---|
| requirements-author | Skill | Structured BRD/PRD, traceability, lifecycle gates | requirement-analysis and traceability |
| EARS acceptance reference | Skill reference | Trigger/state/outcome wording | Observable AC with failure behavior |
| BRD-to-PRD handoff reference | Skill reference / contract | Durable, validated handoff payload | assessment readiness and backlog handoff |
| functional-planner | Skill + consuming Agent | Read-only PRD-to-backlog hierarchy | work-breakdown and backlog-handoff |
| backlog-management / backlog-manager | Skill / Agent | Platform-specific execution boundary | Separate draft planning from authorized tracker mutation |
| rpi-research / rpi-plan / rpi-review | Skills | Reuse adequate evidence; plan and review artifacts | evidence readiness and assessment-review |
| adr-creation | Agent | Decision documentation | architecture-review and decisions.md |
| system-architecture-reviewer | Agent | Scoped tradeoff review | architecture-review |
| hve-builder | Skill | Maintain instruction/agent/skill artifacts | Future local skill evolution |

Official entry points:

- [Requirements author](https://github.com/microsoft/hve-core/blob/main/.github/skills/project-planning/requirements-author/SKILL.md)
- [EARS acceptance](https://github.com/microsoft/hve-core/blob/main/.github/skills/project-planning/requirements-author/references/prd/ears-acceptance.md)
- [BRD-to-PRD handoff](https://github.com/microsoft/hve-core/blob/main/.github/skills/project-planning/requirements-author/references/brd/brd-to-prd-handoff-v1.md)
- [Agent / consuming-skill catalog](https://github.com/microsoft/hve-core/blob/main/.github/CUSTOM-AGENTS.md)
- [RPI lifecycle](https://github.com/microsoft/hve-core/blob/main/docs/rpi/README.md)
- [Repository overview](https://github.com/microsoft/hve-core)

Adoption options: reference a pattern and keep an independent local implementation; vendor an exact folder
at a recorded commit with dependencies and attribution; or use the official host integration when applicable.
If vendoring, inspect referenced templates, instructions and sibling resources rather than copying one SKILL.md.
Check each component's own license: requirements-author currently declares CC-BY-4.0 in frontmatter, while
repository-level licensing does not establish a uniform license for every skill. Pin a release/commit and
review upgrades through a diff. Agent definitions require host adaptation; placing an Agent file in a skill
folder does not turn it into a portable Skill. Do not copy HVE tool allowlists or approval logic blindly.
