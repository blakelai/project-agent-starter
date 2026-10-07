# Impact Analysis

Follow the requirement's term_refs and vault/docs/domain-terminology.md. Compare current implementation
against the approved business meaning, recording differences rather than silently redefining a term.
Keep evidence-backed current mappings separate from proposed mappings and human definition confirmation.
On changed term revisions, reassess affected FR/AC/contracts and record open questions before estimation.


1. Read requirement.md and evidence.md. Search relevant capability and lifecycle in OpenWiki first.
2. Follow module, aggregate, API/event and consumer links across configured repository boundaries.
3. Verify exact contracts and relevant source/test files at recorded revisions where impact depends on them.
4. Write solution-assessment.md covering domain, contracts, downstream consumers, data migration, deployment,
   security, observability, operations, rollback and multi-fab configuration where applicable.
5. For each impact record CONFIRMED/POSSIBLE/UNKNOWN, evidence IDs, reason, affected owner and open question.
   Explain why an apparently unaffected surface is out of scope when that matters to acceptance.
6. Document backward compatibility, duplicate delivery, retry ownership and failure propagation explicitly.
7. Update evidence.md and the source revision list; separate current implementation from desired future design.
8. Handle unresolved design tradeoffs in the architecture substep; never derive PD estimates from wiki text.
