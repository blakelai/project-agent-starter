---
type: Project Format Contract
title: OKF 專案資料規約
description: OKF v0.2 的本地專案資料儲存、編輯與驗證規則。
status: draft
---

# OKF 專案資料規約

`vault/` 是一個 **OKF v0.2 bundle**。知識與專案管理內容以 UTF-8 Markdown 保存。
本地擴充 **`project-agent/v1`** 定義可計算資料在頁面內的存放方式；它不是 OKF 官方的專案管理 schema。
一般 OKF reader 可以閱讀內容和連結；執行本專案的驗證與排程仍需隨附的 Python 工具。

## 頁面與欄位

一般概念頁有 YAML frontmatter，至少含非空 `type`；本骨架另填 `title`、`description`、`status`。
正文使用標題、段落、表格、標準 Markdown 連結與程式碼區塊。自訂欄位應保留。

| 欄位或檔案 | 本 Repository 的用途 |
|---|---|
| frontmatter `type` | 頁面種類：Project Data、Project Guide、Project Schedule 等 |
| frontmatter `status` | 知識生命週期：draft、stable、deprecated |
| `project_profile: project-agent/v1` | 此頁含有本地工具讀取的結構化資料 |
| 資料區塊內的 `status` | 需求或評估流程狀態，依 [data contract](data-contract.md) 定義 |
| `sources`、`generated`、`verified` | 使用時遵守 OKF provenance 定義；不能自動當作業務核准 |
| 根目錄 `index.md` | 導覽入口；frontmatter 只宣告 `okf_version: "0.2"` |
| 子目錄 `index.md` | 無 frontmatter 的導覽頁 |
| `log.md` | 無 frontmatter、以日期分組的變更紀錄 |

OKF 時間戳需帶明確時區；業務日期遵循本地 data contract。
Repository registry 的 `sources` 放在資料區塊；頁首 `sources` 若使用，每筆需有 OKF `resource`。
不要混用兩者，也不要把需求的 `intake` 或 `baseline` 填入 frontmatter `status`。

## 一份可編輯資料

Project Data 頁面的結構化內容放在唯一一組 `<!-- project-data:start -->` 與
`<!-- project-data:end -->` 標記之間，使用標準 `yaml` fenced code block，內含 `schema_version: 1`。
標記是本地 parser 的定位契約；編輯時保留標記、fence 與欄位名稱。
程式直接讀取這個區塊，不從敘述段落或表格猜測數值，也不讀取另一份平行的 `.yaml` 原稿。

Obsidian Properties 適合標題、種類等簡單屬性。巢狀 WBS、容量、估算資料放在正文區塊，
可於閱讀模式查看完整內容，並在編輯模式修改。這些資料不是 Obsidian 表單欄位，也不會自動成為 Bases 欄位。
敘述段落補充背景、理由、假設與證據；涉及 ID、工時、日期等 authoritative 值時，以資料區塊為準。

`write_data` 更新既有資料頁時只取代該區塊，保留 frontmatter 和其餘正文。
呼叫端必須載入原資料、修改後一起保存，保留未知資料欄位。重複 YAML key 與多個資料區塊會被拒絕。

## 文件預設語言

Agent 產生文件前，讀取 [專案設定](../config/project.md) 資料區塊中的 `documentation_language`。
語言選擇依序為：本次任務明確指定的語言、專案設定、`zh-TW` 預設值。
設定省略、`null` 或空白時使用預設值；可填 `zh-TW`、`en`、`ja` 等明確語言代碼，不限定這三種。
使用者以另一種語言聊天，不代表要求切換文件語言；單次覆寫也不改動專案設定。

新增或整份重新產生文件時，標題、frontmatter 的 `title` / `description`、章節、段落、表格標籤，
以及資料區塊內的自然語言敘述（例如 goal、statement、rationale），均依選定語言撰寫。
欄位名稱、`type` / 狀態等 schema 值、ID、檔名、路徑、連結、命令、程式碼與專有名稱保持原樣。
原文證據與引用保留原語言；補充譯文需明確標示。

局部維護既有文件時沿用該文件語言；使用者要求翻譯或整份重新產生時再套用上述優先序。
修改設定不會批次翻譯既有文件，也不會改寫已核准 baseline。Skill 或模板本身的語言不是輸出語言設定。
`.agents/skills/` 下的 Skill 定義、參考文件與 host 顯示資訊統一以英文維護，不受專案文件語言設定影響。
這是 Agent 撰寫規則；CLI 初始化仍複製既有模板，排程與索引工具的固定文字維持內建語言。
Agent 填寫模板時套用本設定；對工具產生的排程另寫指定語言的 project-plan 解讀，保留可重算產物。

## 連結、模板與產物

領域詞彙採 [術語規約](domain-terminology.md)：業務正文放在單一 `term-definition` 標記區塊內，
以支援 Markdown 表格、圖片與確切版本確認；結構化資料仍放在同一頁的唯一 `project-data`。
`confirmed` 是資料區塊的業務確認狀態，不可用 OKF frontmatter 的 stable/verified 代替人類確認。

使用者原始 BRD 依 [BRD 規約](brd-intake.md) 保存在 `intake/`，只需要 OKF frontmatter 與一般 Markdown
正文，不要求將原文轉成 project-data。引用的圖片維持二進位附件；分析快照與涵蓋資料才使用 project-data。

使用相對 Markdown 連結，保留 GitHub 與一般編輯器的可讀性；關係意義寫在周邊文字。
概念身分由 bundle 內的路徑決定；FR、AC、WP 等業務 ID 仍以資料欄位保存，不因改標題而變更。
`index.md` 提供目錄入口；概念頁另外連結相關需求、證據、估算和規劃。

空白模板也有 OKF frontmatter。初始化工具替換 `{{REQ_ID}}`、建立四份核心頁及索引，拒絕覆寫已有需求。
workflow.py 依階段加入 solution、planning 或 delivery 文件，只建立缺少的頁面；既有舊版模板保留以便沿用。
project.md 模板的 `{{PROJECT_ID}}` 由 init_project.py 替換。詳見 [工作流程](project-workflow.md)。
新增筆記可從 [概念模板](../templates/concept.md) 開始。新增或搬移頁面時同步調整連結。
需求目錄及需求總目錄的索引由工具更新，手寫說明應放到概念頁。

`schedule-*.md`、`forecast-*.md` 是衍生產物，表格與完整數據由同一結果產生。
重算會更新正文、保留未知 frontmatter 欄位，並移除舊 `verified`；重新計算本身不是重新核准。
要改日期或工時，先修改輸入再重算。人為判斷寫入 `project-plan.md`。
核准的 baseline 由 baseline.py 保存確切輸入、指定報表與 hashes；不得在 baseline 副本直接重算。
snapshot 中保存原檔 bytes 及原路徑，不改寫已核准的正文或連結；未納入快照的外部連結仍需回到 live Vault／來源檢索。

## 格式範圍與驗證

Repository 外層的 Agent、Skill、Python、CI 與相依套件檔案保留工具原生格式。
Source Repository 的既有 OpenWiki 仍由原 owner 流程維護，此轉換不修改來源 Wiki。
`.local/sources.md` 是不提交的本機對映，可沿用同一資料規約。

從 Repository 根目錄執行 `python scripts/validate.py --all`，檢查此 profile、常用 OKF metadata、
資料語法與需求關聯。這是本專案的檢查器，未涵蓋全部 OKF 條款或 Attested Computation 執行。
通過檢查不代表證據真實、人類核准或預測已校準。

## 來源

- [OKF v0.2 規格](https://github.com/GoogleCloudPlatform/knowledge-catalog/blob/main/okf/SPEC.md)，查閱於 2026-10-07。
- [Obsidian Properties](https://obsidian.md/help/properties)，包含巢狀 properties 的限制。
- [資料契約](data-contract.md) · [Obsidian 操作](obsidian-guide.md) · [導覽](../index.md)

[回到目錄](index.md)
