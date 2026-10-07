---
type: Project Data
title: Repository 與 Wiki 來源登錄
description: Repository 與 Wiki 來源登錄的可編輯專案資料。
status: draft
project_profile: project-agent/v1
---

# Repository 與 Wiki 來源登錄

編輯下方結構化資料；保留欄位名稱、ID 與單位。未確認的事實保持空白。

除了 Repository／Wiki 來源，此清單也接受 `kind: brd` 的本機文件來源；`path` 相對於 Project Repository 根目錄。
需求初始化的 `--source` 會登錄 BRD，原文與附件雜湊則存入各需求的來源快照。詳見 [BRD 流程](../docs/brd-intake.md)。

## 結構化資料

<!-- project-data:start -->
```yaml
schema_version: 1
sources: []
```
<!-- project-data:end -->

[回到目錄](index.md)

## 關聯頁面

[跨專案知識地圖](project-map.md) · [OpenWiki 串接](../docs/openwiki-integration.md)
