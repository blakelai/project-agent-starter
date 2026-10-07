---
type: Project Guide
title: OpenWiki connection playbook
description: OpenWiki connection playbook。
status: draft
---

# OpenWiki connection playbook

Verified against the official README on 2026-10-04. Existing wiki installations can be reused.
Record your exact tested OpenWiki version in the project onboarding record; do not assume `main` is pinned.
Source: https://github.com/langchain-ai/openwiki/blob/main/README.md

## Shared facts and local paths

`vault/knowledge/sources.md` is this starter's source registry, NOT a native OpenWiki settings file.
Populate real source IDs/URLs/wiki roots. Create `.local/sources.md` from
`vault/config/local-sources.template.md`; keep per-machine absolute paths out of shared configuration.
Never commit provider credentials or local OpenWiki private state.

## Native workspace and MCP route

From a directory containing or near your source checkouts, run `openwiki link`; interactively create a
workspace and select existing wiki-bearing repositories. Inside a member repository, inspect with
`openwiki workspace current` and select with `openwiki workspace use <workspace-name>` (use your actual name).
The native registry is local, so each developer/runner sets it up; the manifest documents intended membership.

Use `openwiki integrations list` to inspect existing host integration. If the agent host is not connected,
install the selected integration as documented by your OpenWiki release, for example:

```bash
openwiki integrations install codex --project .
```

Discover actual MCP tool schemas; tools of interest are `openwiki_list_workspaces`, `openwiki_list_wikis`,
`openwiki_search` and `openwiki_read`. Search a concrete question, then read complete relevant sections using
returned wiki IDs/anchors. Do not hardcode tool argument names from this guide.

A Project Repository without its own `openwiki/` does not automatically become a wiki/workspace member.
Verify that the host's installed retrieval tools can discover and target the source wiki/workspace from this
working directory. If the schema cannot express that context, run retrieval in a source member context or
use the filesystem route. Do not invent a remote OpenWiki URL or an unverified MCP server configuration.

## Filesystem route — works without MCP

Resolve source ID -> `.local/sources.md` checkout -> `wiki_root`.
Read `openwiki/quickstart.md` if present; otherwise inspect the installed wiki's actual entry/index.
Use `rg` for targeted retrieval, then read the relevant full sections and source/test files:

Use mapped actual checkouts to search relevant lifecycle/contracts, then inspect source and tests.
Record the actual source commit, dirty paths/content hashes if relevant, and the observed wiki section.

Record source commit with `git -C <checkout> rev-parse HEAD`, query scope, wiki page, source path and observation date in evidence.md.
If the checkout is dirty, record changed paths and their hashes or use a clean pinned checkout. HEAD alone
cannot identify uncommitted bytes. Keep only relevant excerpts and evidence, not duplicated entire wikis.

## Freshness and update ownership

Before material re-assessment compare source revisions and relevant source changes. A page generation date
alone does not prove the underlying source is current. Repository Claims under `openwiki/.claims/` can help
inspect grounded evidence; connector-derived facts do not carry the same repository-Claims guarantee.
Request/run a targeted owner workflow when wiki drift matters. Use `openwiki --update` inside the source
repository when authorized. Do not run `--init` on an existing wiki just to connect it: it regenerates the wiki.

Preserve the OpenWiki-managed `OPENWIKI:START` / `OPENWIKI:END` block in existing AGENTS.md; project rules belong
outside it. Cross-project capability maps are maintained project artifacts. Running code-mode OpenWiki on
this management repository documents this repository's files; it does not automatically synthesize the
entire business system from all source wikis.

[回到目錄](index.md)
