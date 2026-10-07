---
name: impact-analysis
description: Analyze project requirement effects across repository wikis and original
  code. Use for behavior, domain, API, event, schema, integration or compatibility
  changes.
---

# Impact Analysis


1. Read requirement.md and evidence.md. Search relevant capability and lifecycle in OpenWiki first.
2. Follow module, aggregate, API/event and consumer links across configured repository boundaries.
3. Verify exact contracts and relevant source/test files at recorded revisions where impact depends on them.
4. Write impact-analysis.md covering domain, contracts, downstream consumers, data migration, deployment,
   security, observability, operations, rollback and multi-fab configuration where applicable.
5. For each impact record CONFIRMED/POSSIBLE/UNKNOWN, evidence IDs, reason, affected owner and open question.
   Explain why an apparently unaffected surface is out of scope when that matters to acceptance.
6. Document backward compatibility, duplicate delivery, retry ownership and failure propagation explicitly.
7. Update evidence.md and the source revision list; separate current implementation from desired future design.
8. Hand unresolved design tradeoffs to architecture-review; never derive PD estimates from wiki text.

## OKF editing contract

Read `vault/docs/okf-profile.md`. Edit project knowledge under `vault/` as OKF Markdown. Structured facts live in the single marked YAML block in each Project Data note; preserve its markers, unknown fields, OKF frontmatter and surrounding prose. Update semantic body links when adding relationships. Frontmatter `status` is the knowledge lifecycle; project workflow status remains inside the data block. Commands run from the repository root.
