---
type: Project Data
title: 工作類型
description: 工作類型的可編輯專案資料。
status: draft
project_profile: project-agent/v1
---

# 工作類型

編輯下方結構化資料；保留欄位名稱、ID 與單位。未確認的事實保持空白。

## 結構化資料

<!-- project-data:start -->
```yaml
schema_version: 1
work_types:
  domain-model-change:
    description: domain model change
  external-integration:
    description: external integration
  event-integration:
    description: event integration
  observability:
    description: observability
  integration-test:
    description: integration test
  rollout:
    description: rollout
  backend-api:
    description: backend api
  event-contract:
    description: event contract
  schema-change:
    description: schema change
  migration:
    description: migration
  frontend:
    description: frontend
  security-review:
    description: security review
  documentation:
    description: documentation
```
<!-- project-data:end -->

[回到目錄](index.md)
