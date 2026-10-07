---
type: Project Data
title: 專案範圍與優先序
description: 跨需求的目標、規劃集合、優先序與依賴。
status: draft
project_profile: project-agent/v1
---

# 專案範圍與優先序

先填寫真實目標、成功標準與決策人，再登錄此次一起分配容量的所有 REQ。
requirements 每筆包含 id、priority（越小越優先）。dependencies 每筆包含 predecessor 與 successor，
各以 requirement_id、work_package_id 指向確切工作包。欄位不可用推測填滿。

<!-- project-data:start -->
```yaml
schema_version: 1
id: '{{PROJECT_ID}}'
name: null
owner: null
goal: null
success_criteria: []
scope: []
non_goals: []
requirements: []
dependencies: []
```
<!-- project-data:end -->

[完整工作流程](../docs/project-workflow.md)
