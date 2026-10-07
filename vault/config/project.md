---
type: Project Data
title: 專案設定
description: 專案設定的可編輯專案資料。
status: draft
project_profile: project-agent/v1
---

# 專案設定

編輯下方結構化資料；保留欄位名稱、ID 與單位。未確認的事實保持空白。

## 結構化資料

<!-- project-data:start -->
```yaml
schema_version: 1
project_id: null
name: null
owner: null
timezone: Asia/Taipei
documentation_language: zh-TW
knowledge_mode: filesystem
openwiki_workspace: null
```
<!-- project-data:end -->

## 文件預設語言

`documentation_language` 規範 Agent 新增或重新產生文件時使用的語言，預設 `zh-TW`（臺灣繁體中文）。
可改成 `en`（英文）、`ja`（日文）或其他明確的語言代碼。設定值放在上方結構化資料區塊。
單次任務明確指定語言時，以該次要求為準；不會自動更改專案設定。
未設定、`null` 或空白時沿用 `zh-TW`。完整範圍與既有文件處理方式見 [OKF 規約](../docs/okf-profile.md)。

[回到目錄](index.md)

## 關聯頁面

[來源登錄](../knowledge/sources.md) · [人員與技能](../planning/people.md)
