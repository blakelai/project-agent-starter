---
type: Project Guide
title: 領域詞彙、釐清與確認
description: 以共用詞彙定義、上下文及人類確認版本管理需求理解。
status: draft
---

# 領域詞彙、釐清與確認

本專案以 [領域詞彙庫](../knowledge/glossary/index.md) 保存共用概念。需求引用確切版本，
不明確的用語先登錄問題，交由人類補充；Agent 不自行猜測含義或翻譯。
檔案均為本專案的 OKF Markdown，能以 Obsidian、一般編輯器或 GitHub 閱讀與修改。

## 目錄

- [文件與權責](#文件與權責)
- [建立與釐清](#建立與釐清)
- [記錄人類確認](#記錄人類確認)
- [連結需求與準備度](#連結需求與準備度)
- [定義變更](#定義變更)
- [資料契約](#資料契約)
- [限制與遷移](#限制與遷移)

## 文件與權責

| 位置 | 內容 |
|---|---|
| `vault/knowledge/glossary/TERM-*.md` | 一個概念一頁；穩定 ID 不隨顯示名稱改變 |
| `vault/knowledge/glossary/contexts.md` | 上下文 ID、名稱與業務邊界 |
| `vault/knowledge/glossary/assets/<TERM-ID>/` | 該概念定義引用的本地圖片 |
| `vault/knowledge/glossary/index.md` | 由工具彙整的原始用語、中英文、別名及上下文索引 |
| `vault/knowledge/glossary/clarification-queue.md` | 由工具彙整的未解問題、確認錯誤與需求影響 |
| `vault/templates/term.md` | 空白術語模板 |

同一上下文內應維持一致定義。不同上下文可使用同一字詞表示不同概念，必須使用不同 TERM ID。
工具會阻止同一上下文中兩個已確認概念占用同語言的正式名稱或別名；它不判斷兩段定義是否語意相同。
未定義上下文時保持 null，不因專案只有一個 Repository 就推定只有一個業務上下文。

業務定義由領域負責人確認。系統對應是獨立的實作／設計證據，不構成定義核准。
原始 BRD 保留不動；引用使用原始字詞，分析正文依 [文件語言設定](okf-profile.md#文件預設語言) 撰寫。
中英文正式名稱、別名及縮寫逐項記錄已確認用語，不因文件語言切換而自動重譯。

## 建立與釐清

命令在 Repository 根目錄執行。下列尖括號均需替換成自己的輸入；不是可原樣執行的 shell 參數。

```bash
python scripts/terminology.py init <TERM-ID> --label "原文中的用語"
```

若上下文已明確，可加 `--context <CTX-ID>`；先在 contexts.md 的 `contexts` 陣列登錄該上下文。
每筆需有 `id`（CTX- 開頭）、`name`、`definition`。只依人類提供的邊界填寫。
工具不會填入業務定義、正式名稱、譯名或確認人，只保留 observed_labels 並建立 TQ-01 開放問題。

Agent 應搜尋原始用語、名稱及別名，讀取完整條目與上下文。遇到歧義時，在術語頁記錄：

- `sources`：來源路徑或 URL、確切來源版本、逐字引文；BRD 用文件路徑加 br- 錨點及擷取版本。
- `questions`：需要人類補充的具體問題、是否影響定義、實際負責人；未知負責人留 null。
- 若圖片中的用語不明，引用實際圖片並記錄無法確定之處。Agent 需真正開啟圖片，不以檔名猜內容。

定義與未知譯名保持空白。查到的 Wiki／程式碼可以作為有出處的線索，不自動成為業務定義。
收到人類說明或人類明確指定採用的權威定義後，才整理為 `proposed`；記錄支持它的 sources。
人類補完的定義放在唯一的 `term-definition:start/end` 標記內，可有標題、文字、表格、圖片及程式碼。
關鍵業務含義不要放在該區塊外或只靠外部超連結表示，因為那不在定義確認範圍內。

正式名稱放在 `names` 的語言代碼欄位；未提供的語言保持 null。縮寫放在 aliases，標記語言與用語。
補完共用問題時，將 status 設為 resolved，填 answer、source、answered_by、answered_at。
所有時間戳使用含時區的 ISO 8601。答案不自動代表定義已獲核准。

## 記錄人類確認

先取得目前內容的定義版本：

```bash
python scripts/terminology.py revision <TERM-ID>
```

向人類呈現該版本完整的定義、名稱、上下文與附件。取得明確確認後，記錄對應版本：

```bash
python scripts/terminology.py confirm <TERM-ID> --revision "sha256:..." --by "實際確認人" --at "含時區的確認時間" --source "可定位人類確認的紀錄"
```

confirm 是**記錄既有的人類確認**，不是請工具代替人類核准。Agent 不得虛構 by、at 或 source，
也不得將自己整理的候選文字視為已被人類接受。命令必須使用人類審閱的版本；內容已變就拒絕。

確認要求非空定義、至少一個正式名稱、明確上下文，以及沒有未解的 affects_definition 問題。
正式英文譯名可以稍後補充：若中文含義已清楚，英文問題可明確標為不影響定義。
前一次確認會保留在 confirmation_history；舊版完整內容仍由 Git 及 baseline 快照保存。

定義版本涵蓋業務正文、正式名稱／別名、來源、相關概念 ID、上下文內容、圖片 bytes，以及未知業務擴充欄位。
不涵蓋工作流程狀態、observed_labels、questions、system_mappings、confirmation 或 confirmation_history。
因此補充系統對應不會悄悄改變業務定義的確認結果。

## 連結需求與準備度

```bash
python scripts/terminology.py link <REQ-ID> <TERM-ID> --fr <FR-ID> --source-item <BRD-ID>/<br-ID>
```

`--fr` 與 `--source-item` 可以重複；兩者皆可省略，以記錄適用整份需求的概念。
BRD 條目必須已由該需求擷取。工具建立 term_refs、來源版本及 pending review，並將術語中尚未解決的
共用問題連結至需求 questions。共用答案維護於術語頁，需求只記錄本需求的影響與處理依據。
連結新術語會撤回草稿準備度，不改寫 FR、AC、估算或原文。

預設 `usage: meaning`：使用該概念解釋需求，必須先有有效人類確認。
只有純背景且不影響行為的用語才可用 `--usage background --reason "不影響本需求的具體理由"`，
此類引用不能連到 FR。不得以 background、non-blocking 或 ASSUMED 規避未釐清的實際業務含義。
不相關術語的未解問題不阻擋其他需求。

完成影響分析後，逐筆更新 term_refs.review 與整體 terminology_review：status=reviewed，
by=實際檢閱者，at=含時區時間，notes=檢閱範圍、結論與限制。這是分析紀錄，可以由執行分析的 Agent 填寫；
它與僅限人類的 definition confirmation 不同。沒有發現領域術語的需求也要記錄整體檢閱結論。

共用問題解決後，需求問題仍保持 open。檢閱對該需求的影響後才能 resolved：填寫本需求的 answer，
source 指向術語問題，term_revision 填該 term_ref 的 source_revision。不要複製另一份共用答案。
新增的需求問題可以使用其他實際 ID，但 term_question 必須引用已連結術語中存在的問題。

`validate.py --stage requirements` 起的關卡、`--planning` 與 assessment.ready_for_planning 檢查會阻擋未確認的 meaning、
失效確認、過期引用、未檢閱項目、懸空問題及尚未解決的阻擋問題。
只有所有既有評估條件也符合後，assessment-review 才能重新標示 ready_for_planning。

## 定義變更

```bash
python scripts/terminology.py report
python scripts/terminology.py refresh <REQ-ID>
```

report 更新索引與影響清單，不修改術語或需求。refresh 只處理草稿，重新擷取引用版本與上下文，
保留既有分析及未知欄位；將受影響引用／整體術語檢閱改回 pending，重新開啟相關需求問題並撤回準備度。
已刪除的共用問題引用不自動移除，保留供人類／Agent 明確檢查。

definition_revision 綁定業務定義；source_revision 綁定整份術語文件、其上下文及定義圖片。
第一版採保守策略：引用文件任何變動（包含問題、確認或系統對應），都要求受影響需求刷新並檢閱。
只有已確認的業務內容改動，才需要新的領域人類確認；狀態維持 confirmed 也不能沿用舊 hash。
refresh 不確認定義、不關閉問題，也不代表分析已完成。

baseline／closed 需求拒絕 link 與 refresh。建立基準時，須保存所引用術語、上下文、圖片、確認紀錄
與 hashes 的完整快照；Git commit 可協助追溯，hash 本身不能還原原始內容。
舊基準依其快照解讀；後續定義變更依 change-control 建立新的評估，不在基準副本直接重算。
排程產物包含引用的術語頁、contexts.md 與定義附件 hashes；來源失效時排程拒絕覆寫既有產物。
BRD 重新擷取也會撤回術語檢閱，因為新原文可能引入新概念或改變使用情境。

## 資料契約

| 欄位 | 規則 |
|---|---|
| term.id | 與 TERM- 開頭檔名一致，永久保留 |
| term.status | needs-clarification / proposed / confirmed / deprecated；不同於 OKF 頁首 status |
| observed_labels | 原文用語陣列；不代表正式別名已被確認 |
| context_id | 已登錄的 CTX ID；未知為 null |
| names / aliases | names 為語言代碼對應名稱或 null；aliases 每筆含 language、value |
| sources | 每筆 path、revision、quote；引用的是該版本原文，不宣稱外部來源永遠最新 |
| related_terms | 其他現有 TERM ID；僅為導覽，不自動引入對方含義或形成版本依賴 |
| questions | id、question、affects_definition、status、owner；resolved 另需 answer/source/answered_by/answered_at |
| system_mappings | 每筆 id、kind、path、revision、description；current 另需 evidence/verified_by/verified_at，proposed 另需 decision_ref |
| confirmation | by、at、source、revision；必須對應確切的 definition_revision |
| term_refs | term_id、context_id、usage、non_blocking_reason、functional_requirement_ids、source_refs、definition_revision、source_revision、review |
| term_question | 需求問題中的 term_id 與 question_id；答案源於術語頁 |

若分析同時依賴多個概念，將每個概念都列在需求 term_refs；related_terms 的導覽連結不代替明確引用。
系統對應沒有資料可以留空；業務確認不要求已有實作。proposed 的 decision_ref 只是設計依據，不能證明決策已核准。
維持已確認的業務定義，另把實作差異放在 system_mappings 與需求問題中，不以現況程式碼改寫定義。

## 限制與遷移

- 既有需求若沒有 terminology_review，在下一次 requirements 關卡／readiness／planning 前需補做；空白 intake 仍可驗證。
- 第一版不自動擷取所有名詞、不做 OCR、不做語意相似搜尋。Agent 需閱讀文字、表格、圖片並主動登錄歧義。
- 圖片只支援 `![說明](assets/<TERM-ID>/file.png)` 等本地行內格式；空白需 URL 編碼。
  遠端圖片、Wiki embeds、reference-style 圖片、HTML 圖片與超出專屬附件目錄的路徑會拒絕。
- 業務定義中引用外部文件時，關鍵含義需整理進確認區塊並保存出處。工具不追蹤外部 URL 的內容變化。
- hash 可驗證內容是否改變，不能證明定義正確、圖已被讀懂、文字無歧義，或核准者身分真實。
- report 是可重建的靜態 Markdown 檢視，需手動或由 Agent 執行，不是 Obsidian 即時監看外掛。
- CLI 複製模板及報表固定用語維持內建語言；Agent 敘述仍遵守 documentation_language。

[詞彙庫](../knowledge/glossary/index.md) · [BRD 匯入](brd-intake.md) · [資料契約](data-contract.md) · [回到目錄](index.md)
