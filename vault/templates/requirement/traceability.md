---
type: Project Data
title: 驗收追蹤
description: 驗收追蹤的可編輯專案資料。
status: draft
project_profile: project-agent/v1
---

# 驗收追蹤

編輯下方結構化資料；保留欄位名稱、ID 與單位。未確認的事實保持空白。

`source_coverage` 追蹤原始 BRD 條目到 FR 的分析結果；`links` 追蹤 AC 到工作包及測試證據。
BRD 初始化會建立 pending 紀錄；完整欄位與就緒條件見 [BRD 規約](../../docs/brd-intake.md)。

## 結構化資料

<!-- project-data:start -->
```yaml
schema_version: 1
links: []
source_coverage: []
```
<!-- project-data:end -->

## 關聯頁面

[需求與驗收條件](requirement.md) · [交付工作](work-breakdown.md)

[回到目錄](index.md)
