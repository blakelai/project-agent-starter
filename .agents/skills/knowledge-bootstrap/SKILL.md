---
name: knowledge-bootstrap
description: Initialize project knowledge routing from existing OpenWiki repository
  wikis. Use for new project repositories, adding sources, missing retrieval, or stale
  source evidence.
---

# Knowledge Bootstrap

Read vault/docs/domain-terminology.md and inspect the project glossary when establishing domain routing.
Register actual context boundaries from human input; leave unknown context null. Reuse approved concepts
without copying their definitions into a second glossary. Wiki vocabulary and implementation names need
explicit human clarification/confirmation before becoming project business definitions; record contradictions.


1. Read vault/config/project.md, vault/knowledge/sources.md and vault/docs/data-contract.md.
   Use init_project.py <PROJ-ID> for an empty project scope. Obtain the goal, success criteria, owner,
   scope and priorities from actual project decisions; do not invent them. Record all REQs that share
   the capacity pool in project.md before combined planning.
2. Confirm project boundary, source owners and required repositories. Keep URLs and logical IDs in
   the shared manifest; map checkouts in ignored .local/sources.md using vault/config/local-sources.template.md.
   Registry entries with kind: brd use a local Project Repository path, not a source checkout or OpenWiki
   workspace. Read vault/docs/brd-intake.md for their registration and byte-level source revisions.
3. Inspect existing OpenWiki entry pages and source commits. Reuse repository wikis; do not reinitialize them.
4. If OpenWiki MCP exists, discover available tools and their schemas; list workspaces/wikis, then search
   a concrete capability and read selected sections with returned wiki IDs/anchors. If multiple workspaces
   are ambiguous, resolve scope. Do not assume this Project Repository belongs to a workspace automatically.
5. Otherwise resolve checkout paths and use rg on selected wiki/source directories. Record fallback mode.
6. Write vault/knowledge/project-map.md with capability, source ID, entry page, owner and important cross-repo contracts.
7. Write vault/requirements/<id>/evidence.md for task-specific claims. Capture revision, observed_at and state.
   Check .claims evidence if available; do not equate generated timestamp with verified current source.
8. Record unknowns and contradictions. Request a targeted wiki refresh in its owning repo when needed.
9. Validate routing by answering one lifecycle question and one cross-repo consumer question with evidence.

Read vault/docs/openwiki-integration.md for setup commands. The manifest is our adapter, not OpenWiki's API.

Read AGENTS.md, vault/docs/okf-profile.md and vault/docs/project-workflow.md before editing.
Apply the shared language, evidence, authority and file-format rules; do not duplicate or override them here.
