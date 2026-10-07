---
name: solution-assessment
description: Assess solution impacts and architecture choices using requirement and source evidence. Use for a clarified requirement, cross-repository effects, API/schema changes, integrations, or design tradeoffs; reuse an adequate existing solution for small changes.
---

# 方案與影響評估

1. 讀取 AGENTS.md、vault/docs/project-workflow.md 與相關 requirement.md、term_refs、evidence.md。
   遵守共用語言、OKF、來源與人類確認規則。未知詞義交由 domain-terminology。
2. 先檢查影響範圍。需要獨立方案文件時執行 `python scripts/workflow.py --requirement <REQ-ID> --stage solution`。
   小型變更可在 requirement.md 記錄沿用既有方案的依據，不強制建立 ADR 或虛構替代方案。
3. 依 [影響檢查](references/impact-analysis.md) 查證實際來源、合約、消費者、遷移與失敗行為。
   以 CONFIRMED/POSSIBLE/UNKNOWN 表達影響；現況實作不等於已確認的業務定義。
4. 只有重大取捨才讀 [架構審查](references/architecture-review.md)，比較可行方案與操作後果。
   將影響、方案與判斷放進 solution-assessment.md；重大決策另用 ADR 並引用確認紀錄。
5. 列出需要進入 WBS 的工作與仍未解決的問題，標示 blocks 階段；不在此產生沒有依據的估算。
6. 交給 delivery-planning；來源變更只重做受影響部分，不重新走所有分析。
