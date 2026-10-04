# OpenWiki Project Agent Starter

以既有 Repository Wiki、結構化規劃資料與 12 個 Repository-local Skills，管理需求評估、排程與交付。
此骨架只有工具、規則與空白模板；請填入自己的專案來源、人力、日曆與歷史交付資料。

## 環境與驗證

Python 3.10+；唯一外部 Python 套件為 PyYAML。

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python scripts/validate.py --all
python -m unittest discover -s tests -v
```

未設定的欄位以 null 或空集合保留。資料驗證允許尚未初始化的 intake，排程驗證會阻擋缺少必要資料的需求。

## 初始化專案

1. 設定 config/project.yaml 的 project ID、名稱、owner 與 Wiki 路由。
2. 填寫 knowledge/sources.yaml，連結已有 OpenWiki 的 Source Repository。
3. 從 config/local-sources.template.yaml 建立 .local/sources.yaml，映射本機 checkout。
4. 填寫 planning/ 的真實人員、技能、淨容量與有效期限、日曆，以及已確認的歷史資料。
5. 設定 OpenWiki workspace / host integration，或使用 filesystem retrieval。
6. 用 `python scripts/init_requirement.py <REQ-ID>` 建立需求 intake。
7. 讓 Agent 讀取 AGENTS.md，依相關 Skills 完成分析與 readiness review。
8. 問題解決、資料確認後執行排程：

```bash
python scripts/validate.py --requirement <REQ-ID> --planning
python scripts/schedule.py --requirement <REQ-ID> --scenario expected
python scripts/schedule.py --requirement <REQ-ID> --scenario high
```

將命令中的 `<REQ-ID>` 換成自己的需求 ID，不要保留尖括號。

## 文件與目錄

- docs/initialization-guide.zh-TW.md：完整中文導入指南。
- docs/openwiki-integration.md：OpenWiki routing、workspace、retrieval 與 source freshness。
- docs/data-contract.md：資料權威、狀態、欄位與計算限制。
- docs/skill-catalog.md：12 個 Skills；docs/hve-reference.md：官方參考元件。
- docs/prompts.md：初始化、需求評估、backlog、週報與變更的通用操作 Prompt。
- templates/：空白需求、ADR、週報與 change request。
- planning/：空白 facts 與估算規則；requirements/：建立後的需求。
- scripts/、tests/：驗證與 greedy 排程工具；測試資料只在隔離的暫存目錄內建立。
- ci/azure-pipelines.yml：可選的 artifact / tool 驗證 pipeline。

Skills 的自動發現方式由 Agent host 決定；必要時明確指示它讀指定 SKILL.md。
排程是 full-WBS greedy 可行解：每 WP 一位負責人、每人每天最多一個 WP；支援相依、淨容量、休假與
not-before gate。沒有最佳化、機率模型、actuals-aware reforecast 或外部 tracker 自動寫入。
