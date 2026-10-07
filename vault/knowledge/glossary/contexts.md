---
type: Project Data
title: 領域上下文
description: 詞彙定義適用的業務邊界。
status: draft
project_profile: project-agent/v1
---

# 領域上下文

依人類提供的業務邊界新增上下文。每筆需要 `id`（CTX- 開頭）、`name`、`definition`。
上下文未釐清時，術語的 `context_id` 保持 null。不要自行把同名術語合併。
上下文定義也納入術語確認版本，修改後需重新確認受影響的術語。

<!-- project-data:start -->
```yaml
schema_version: 1
contexts: []
```
<!-- project-data:end -->

[詞彙首頁](index.md) · [操作規約](../../docs/domain-terminology.md)
