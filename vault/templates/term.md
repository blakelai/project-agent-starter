---
type: Domain Term
title: 領域詞彙
description: 業務定義、釐清問題與系統設計對應。
status: draft
project_profile: project-agent/v1
---

# 領域詞彙

先保留原始用語及出處，不明確的定義與翻譯保持空白。由人類補充並確認。
下方定義區塊可放文字、表格與本地圖片；業務含義只在這裡維護。
圖片放在 `assets/<TERM-ID>/`，用標準 Markdown 行內圖片連結引用。

## 業務定義、適用邊界與規則

<!-- term-definition:start -->

<!-- term-definition:end -->

## 結構化資料

<!-- project-data:start -->
```yaml
schema_version: 1
id: '{{TERM_ID}}'
status: needs-clarification
observed_labels: []
context_id: null
names:
  zh-TW: null
  en: null
aliases: []
sources: []
related_terms: []
questions:
- id: TQ-01
  question: 請說明此詞的業務定義、適用範圍與容易混淆的邊界。
  affects_definition: true
  status: open
  owner: null
system_mappings: []
confirmation: null
confirmation_history: []
```
<!-- project-data:end -->

問題的答案以本頁為準；需求文件只引用問題並記錄對需求的影響。
系統對應放在 `system_mappings`，不以程式碼反推尚未確認的業務定義。

[操作規約](../docs/domain-terminology.md)
