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

## 連結、模板與產物

使用相對 Markdown 連結，保留 GitHub 與一般編輯器的可讀性；關係意義寫在周邊文字。
概念身分由 bundle 內的路徑決定；FR、AC、WP 等業務 ID 仍以資料欄位保存，不因改標題而變更。
`index.md` 提供目錄入口；概念頁另外連結相關需求、證據、估算和規劃。

空白模板也有 OKF frontmatter。初始化工具替換 `{{REQ_ID}}`、建立需求與索引，拒絕覆寫已有需求。
新增筆記可從 [概念模板](../templates/concept.md) 開始。新增或搬移頁面時同步調整連結。
需求目錄及需求總目錄的索引由工具更新，手寫說明應放到概念頁。

`schedule-expected.md`、`schedule-high.md` 是衍生產物，表格與完整數據由同一結果產生。
重算會更新正文、保留未知 frontmatter 欄位，並移除舊 `verified`；重新計算本身不是重新核准。
要改日期或工時，先修改輸入再重算。人為判斷寫入 `project-plan.md`。
核准的 baseline 保存確切輸入、輸出與 hashes；不得在 baseline 副本直接重算。

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
