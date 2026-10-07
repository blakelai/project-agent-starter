# OpenWiki Project Agent Starter

用既有 Repository Wiki、12 個 Repository-local Skills 與可重算的排程工具，管理需求評估和交付。
所有日常專案內容集中在 **[vault/index.md](vault/index.md)**，採用 **OKF v0.2 Markdown**。
在 Obsidian 選 **Open folder as vault**，開啟 Repository 的 `vault/`，再開啟 `index.md`。
也可使用其他 Markdown 編輯器或 GitHub 閱讀。骨架保留空白資料與模板，沒有填入範例專案。

## 內容格式

| 內容 | 位置與格式 |
|---|---|
| 指南、需求、知識、規劃、ADR、進度、模板 | `vault/` 內的 OKF `.md` |
| 導覽與變更紀錄 | OKF 保留檔案 `index.md`、`log.md` |
| 可計算資料 | 同一 `.md` 內的 `project-data` YAML 區塊；不另存平行 YAML 原稿 |
| 排程輸出 | 產生的 OKF `.md`，包含表格、逐日分配與輸入 SHA-256 |
| Agent、Skills、host metadata | `AGENTS.md`、`.agents/skills/` 的工具原生格式 |
| 驗證、排程、CI | Python、`requirements.txt`、`ci/azure-pipelines.yml` |

OKF bundle 的範圍是 `vault/`。程式和 host 設定保留執行工具需要的格式。
先讀 [Obsidian 操作](vault/docs/obsidian-guide.md)、[OKF 規約](vault/docs/okf-profile.md) 與
[資料契約](vault/docs/data-contract.md)。

## 環境與驗證

所有命令從 **Repository 根目錄** 執行。Python 3.10+；唯一外部 Python 套件為 PyYAML。

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python scripts/validate.py --all
python -m unittest discover -s tests -v
```

未設定的欄位以 null 或空集合保留。資料驗證允許尚未初始化的 intake，排程驗證會阻擋缺少必要資料的需求。

## 初始化專案

1. 設定 [專案設定](vault/config/project.md) 的 project ID、名稱、owner 與 Wiki 路由。
2. 填寫 [來源登錄](vault/knowledge/sources.md)，連結已有 OpenWiki 的 Source Repository。
3. 從 `vault/config/local-sources.template.md` 建立 `.local/sources.md`，映射本機 checkout。
4. 填寫 [規劃資料](vault/planning/index.md) 的真實人員、技能、淨容量、有效期限、日曆與歷史資料。
5. 設定 OpenWiki workspace / host integration，或使用 filesystem retrieval。
6. 用 `python scripts/init_requirement.py <REQ-ID>` 建立需求 intake。
7. 讓 Agent 讀取 AGENTS.md，依相關 Skills 完成分析與 readiness review。
8. 問題解決、資料確認後執行排程：

```bash
python scripts/validate.py --requirement <REQ-ID> --planning
python scripts/schedule.py --requirement <REQ-ID> --scenario expected
python scripts/schedule.py --requirement <REQ-ID> --scenario high
```

將 `<REQ-ID>` 換成自己的需求 ID。產物位於 `vault/requirements/<REQ-ID>/`，Obsidian 可直接開啟。

## 文件與目錄

- [初始化指南](vault/docs/initialization-guide.zh-TW.md)：完整中文導入流程。
- [OpenWiki 串接](vault/docs/openwiki-integration.md)：routing、workspace、retrieval 與 freshness。
- [Skills](vault/docs/skill-catalog.md) 與 [HVE 參考](vault/docs/hve-reference.md)。
- [操作 Prompt](vault/docs/prompts.md)：初始化、需求評估、backlog、週報與變更。
- [模板](vault/templates/index.md)、[規劃](vault/planning/index.md)、[需求](vault/requirements/index.md)。
- `scripts/`、`tests/`：驗證與 greedy 排程工具；測試資料只在隔離的暫存目錄內建立。
- `ci/azure-pipelines.yml`：可選的 artifact / tool 驗證 pipeline。

Skills 的自動發現方式由 Agent host 決定；必要時明確指示它讀指定 SKILL.md。
排程是 full-WBS greedy 可行解：每 WP 一位負責人、每人每天最多一個 WP；支援相依、淨容量、休假與
not-before gate。沒有最佳化、機率模型、actuals-aware reforecast 或外部 tracker 自動寫入。
