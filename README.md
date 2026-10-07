# OpenWiki Project Agent Starter

用既有 Repository Wiki、9 個 Repository-local Skills 與可重算的排程工具，管理需求評估和交付。
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

## 初始化與專案管理

完整的 [專案管理工作流程](vault/docs/project-workflow.md) 包含流程圖、14 個步驟的 Skill／指令／完成條件，
以及術語釐清、基準、預測與驗收操作。詳細欄位見 [規劃與交付契約](vault/docs/planning-and-delivery.md)。

1. 設定 [專案設定](vault/config/project.md)、[來源登錄](vault/knowledge/sources.md) 和本機 `.local/sources.md`。
2. 填寫 [規劃資料](vault/planning/index.md) 的真實人員、技能、淨容量、有效期限與日曆；接上既有 OpenWiki。
3. 建立 project.md，填寫目標、成功標準、owner，以及一起排程的 REQ 與優先序。
4. 建立需求 intake，分析原文、領域詞彙、FR 與 AC；通過需求關卡後再補上規劃文件。
5. 依 Skills 完成拆工、估算與審查，通過 readiness 後跨需求共用容量排程。

```bash
python scripts/init_project.py <PROJ-ID>
python scripts/init_requirement.py <REQ-ID>
python scripts/validate.py --requirement <REQ-ID> --stage requirements
python scripts/workflow.py --requirement <REQ-ID> --stage planning
python scripts/validate.py --requirement <REQ-ID> --stage planning
python scripts/validate.py --requirement <REQ-ID> --planning
python scripts/schedule_project.py --project <PROJ-ID> --scenario expected
python scripts/schedule_project.py --project <PROJ-ID> --scenario high
```

將 `<...>` 換成實際 ID；各關卡之間需要填寫資料及完成審查，這不是可空跑的批次腳本。
新需求只建立四份核心頁及 index，後續用 workflow.py 按階段補檔，保留已有內容。
排程位於 `vault/projects/<PROJ-ID>/`；人類核准後可用 baseline.py 保存不可覆寫的快照。

執行期間以 `delivery-tracking` 記錄同一截止日的進度與明確剩餘工時，再執行：

```bash
python scripts/schedule_project.py --project <PROJ-ID> --as-of <YYYY-MM-DD> --scenario expected
```

驗收和結案使用 `--stage closure` 檢查與 close_requirement.py；完整核准／結案命令見工作流程。

## 文件預設語言

在 [專案設定](vault/config/project.md) 的結構化資料區塊設定 `documentation_language: zh-TW`。
可改成 `en`、`ja` 或其他明確語言代碼，讓 Agent 依此撰寫新文件；單次任務明確指定語言時優先採用。
規則涵蓋文件敘述，保留 schema 欄位、ID、程式碼與原文引用。CLI 的固定文字維持內建語言。

## 使用原始需求 BRD

先建立空白 BRD，在 Obsidian 中填入原始條目、表格與圖片，再引用它建立需求評估：

```bash
python scripts/init_brd.py <BRD-ID> --title "原始需求標題"
python scripts/init_requirement.py <REQ-ID> --source vault/intake/<BRD-ID>/brd.md
```

以自己的 ID 取代尖括號。BRD 使用 `## br-001` 等穩定編號，圖片放在同目錄 `assets/`。
支援重複 `--source` 引用多份 BRD；原文、圖片與分析以來源 hashes 和涵蓋表追蹤。
資料更新後，可用 `python scripts/refresh_brd.py --requirement <REQ-ID>` 重設草案的來源與準備度。
詳見 [BRD 操作與資料契約](vault/docs/brd-intake.md)。

## 文件與目錄

- [領域詞彙庫](vault/knowledge/glossary/index.md) 與 [術語操作指南](vault/docs/domain-terminology.md)：
  中英名稱、上下文、詳細定義、系統對應、人類釐清及版本確認；未知詞義不由 Agent 推測。

- [初始化指南](vault/docs/initialization-guide.zh-TW.md)：完整中文導入流程。
- [OpenWiki 串接](vault/docs/openwiki-integration.md)：routing、workspace、retrieval 與 freshness。
- [Skills](vault/docs/skill-catalog.md) 與 [HVE 參考](vault/docs/hve-reference.md)。
- [操作 Prompt](vault/docs/prompts.md)：初始化、需求評估、backlog、週報與變更。
- [模板](vault/templates/index.md)、[規劃](vault/planning/index.md)、[需求](vault/requirements/index.md)。
- `scripts/`、`tests/`：驗證與 greedy 排程工具；測試資料只在隔離的暫存目錄內建立。
- `ci/azure-pipelines.yml`：可選的 artifact / tool 驗證 pipeline。

Skills 的自動發現方式由 Agent host 決定；必要時明確指示它讀指定 SKILL.md。
排程是 full-WBS greedy 可行解：每 WP 一位負責人、每人每天最多一個 WP；支援相依、淨容量、休假與
not-before gate。專案工具另外支援同一截止日的剩餘工作預測；沒有最佳化、機率模型或外部 tracker 自動寫入。
不同 PROJ 的獨立排程不會互相保留容量，共用資源應在同一規劃集合中一起計算。
