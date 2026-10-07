---
type: Project Data
title: '{{REQ_ID}} — 需求'
description: '{{REQ_ID}} — 需求的可編輯專案資料。'
status: draft
project_profile: project-agent/v1
---

# {{REQ_ID}} — Requirement intake

IDs、facts、AC 與 questions 以本頁「結構化資料」為準；下方段落補充背景與判斷。

## Problem and business outcome

To clarify. Record measurable outcome without inventing a target.

## Actors and current / expected behavior

To clarify; cite evidence.md for existing behavior.

## Scope / non-goals / constraints

To clarify.

## Acceptance criteria

Add stable FR and AC IDs in requirement.md; explain the context here without duplicating authoritative fields.

## Assumptions and questions

See requirement.md. No delivery commitment before blocking questions are resolved.

## 結構化資料

<!-- project-data:start -->
```yaml
schema_version: 1
id: '{{REQ_ID}}'
synthetic: false
status: intake
source_documents: []
goal: TO_CLARIFY
actors: []
scope: []
non_goals: []
constraints: []
facts: []
functional_requirements: []
acceptance_criteria: []
questions:
- id: Q-01
  question: What observable outcome and failure behavior are required?
  blocking: true
  status: open
  owner: requester
```
<!-- project-data:end -->

## 關聯頁面

[來源證據](evidence.md) · [影響分析](impact-analysis.md) · [驗收追蹤](traceability.md)

[回到目錄](index.md)
