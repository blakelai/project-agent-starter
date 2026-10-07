---
type: Project Playbook
title: 在 Obsidian 使用專案 Repository
description: 開啟 Vault、編輯 OKF 筆記、建立需求與重算排程。
status: draft
---

# 在 Obsidian 使用專案 Repository

## 開啟與導覽

將 Repository clone 到本機後，在 Obsidian 選 **Open folder as vault**，選擇其中的 `vault/` 資料夾。
開啟 [index.md](../index.md)，進入設定、來源、規劃、需求與模板。
其他支援 Markdown 的編輯器也可直接開啟同一資料夾。

不需要社群外掛。新增連結時使用標準 Markdown 相對連結，方便 Obsidian 與 GitHub 閱讀。
Obsidian 個人工作區與回收內容由 `.gitignore` 排除。Git 操作仍從 Repository 根目錄執行。

## 日常編輯

| 要修改的內容 | 編輯位置 |
|---|---|
| 名稱、說明、知識頁狀態 | 頁首 Properties |
| 背景、需求說明、架構選項、決策、週報 | Markdown 正文 |
| WBS、工時、容量、人員、日曆、questions、AC | 正文「結構化資料」的 YAML 區塊 |
| 排程結果 | 調整輸入後執行工具；在產生的 Markdown 表格查看 |
| 本機 checkout 的絕對路徑 | Repository 根目錄的 `.local/sources.md`，不提交 |

YAML 區塊可在編輯模式或 Source mode 中修改。維持縮排、資料型別、IDs 與區塊標記。
Obsidian 原生 Properties 不支援巢狀資料，因此複雜資料放在正文。
數字的理由寫在敘述段落，避免維護另一套手填總計。

## 建立與評估需求

1. 依 [初始化指南](initialization-guide.zh-TW.md) 填寫自己的設定與已確認事實。
2. 在 Repository 根目錄執行 `python scripts/init_requirement.py <REQ-ID>`，以實際 ID 取代尖括號。
3. 開啟 `requirements/<REQ-ID>/index.md`，編輯同目錄的 requirement、evidence、impact 等頁面。
4. Agent 在 Repository 根目錄工作，讀取 `AGENTS.md` 與 [Skill 目錄](skill-catalog.md) 的適用流程。
5. 修改後執行 `python scripts/validate.py --all`，再確認 git diff 並提交。

初始化工具會建立 OKF 頁面並更新需求導覽。一般知識頁可複製 [概念模板](../templates/concept.md)，
修改 metadata 與正文，再把連結加入相關頁與索引。新頁面也需要有效的 OKF metadata。

## 查看排程

範圍、評估、人員和日期已確認，且 blocking questions 已解決後，執行：

```bash
python scripts/validate.py --requirement <REQ-ID> --planning
python scripts/schedule.py --requirement <REQ-ID> --scenario expected
python scripts/schedule.py --requirement <REQ-ID> --scenario high
```

在需求資料夾開啟產生的 `schedule-expected.md` 與 `schedule-high.md`，閱讀時間表和逐日分配。
重算更新產物本文；人為評估寫入 `project-plan.md`。兩個情境不是統計百分位或交付承諾。

## 舊版本轉換

此分支把原本 `config/`、`knowledge/`、`planning/`、`docs/`、`templates/`、`requirements/`、`projects/`
搬到 `vault/`。專案 `.yaml` 內容轉入同名 `.md` 的資料區塊；requirement 資料與原敘述合併為一頁。
原始骨架沒有已填入的專案，因此本次提交不需要遷移真實 baseline。

如果自己的 checkout 已加入需求或改過資料，先提交或備份那些修改，再合併此分支並檢查差異。
已核准 baseline 保留原始版本，另記遷移對照；不要用新格式覆蓋核准證據。
舊 `.local/sources.yaml` 的映射資料需放入 `.local/sources.md` 的資料區塊，不能只改副檔名。
CLI 的 `--root` 仍指 Repository 根目錄。

## 參考

- [OKF 規約](okf-profile.md) · [資料契約](data-contract.md) · [維運](operations.md)
- [Obsidian Properties 官方說明](https://obsidian.md/help/properties)
- [Obsidian Vault 官方說明](https://help.obsidian.md/manage-vaults)

[回到目錄](index.md)
