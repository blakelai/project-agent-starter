---
type: Project Data
title: 估算規則
description: 估算規則的可編輯專案資料。
status: draft
project_profile: project-agent/v1
---

# 估算規則

編輯下方結構化資料；保留欄位名稱、ID 與單位。未確認的事實保持空白。

## 結構化資料

<!-- project-data:start -->
```yaml
schema_version: 1
unit: person-day
minimum_analogues: 3
scenario_labels:
- low
- expected
- high
aggregation: Sum scenarios only; do not label summed quantiles as project P50/P80.
fallback: Use explicitly documented expert judgement range with low confidence; unknown
  is not zero.
risk_policy: Map every contingency to one risk ID; do not count the same risk in effort
  adjustment and schedule delay.
complexity_factors:
  low: 1.0
  medium: 1.0
  high: 1.0
note: No generic multiplier is enabled. Explain any adjustment for each work package.
```
<!-- project-data:end -->

[回到目錄](index.md)

## 關聯頁面

[歷史交付資料](historical-delivery.md) · [工作類型](work-types.md)
