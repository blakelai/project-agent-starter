---
type: Project Playbook
title: BRD 原始需求匯入與分析
description: 手動整理原始需求、附加圖片、引用來源並檢查分析涵蓋情況。
status: draft
---

# BRD 原始需求匯入與分析

BRD 保存使用者的原始需求。Agent 在 `requirements/` 產生分析，並以文件 ID 和條目 ID 引用原文。
本流程接受手動整理的 OKF Markdown；所有命令從 Repository 根目錄執行。

## 建立 BRD

```bash
python scripts/init_brd.py <BRD-ID> --title "原始需求標題"
```

以自己的 `BRD-` 開頭文件 ID 取代 `<BRD-ID>`。工具建立 `vault/intake/<BRD-ID>/brd.md`、
`assets/` 與導覽索引，拒絕覆寫既有資料。骨架不預填任何真實或範例需求。
也可從 [BRD 模板](../templates/brd.md) 手動建立同樣的路徑，將 frontmatter `id` 設為資料夾名稱。
`type` 固定為 `Business Requirements Document`，`title` 填入標題，`status` 使用 OKF 知識生命週期值。
BRD 不需要 `project-data` 區塊，需求直接寫在 Markdown 正文。

每個原始條目用獨立、全小寫的二級標題 `## br-001`，下一行填 `**標題：**` 與名稱，再寫原文。
可用任意穩定的 `br-` 加小寫英數字與連字號編號；不要把需求名稱接在編號標題後，也不要隨排序重新編號。
一般背景章節不必編號。文件中的 fenced code、inline code 和 HTML comments 不當作需求條目。
含有重複編號、不合法編號或未關閉 code fence 的文件會被拒絕；空白 BRD 可保存，尚不能匯入評估。

## 表格與圖片

可直接加入 Markdown 表格。圖片原檔放在該 BRD 的 `assets/`，使用 `![圖號與圖說](assets/檔名.png)`。
附上文字圖說，讓閱讀者知道圖的用途；不能用圖說代替實際判讀。
檔名中的空白請以 `%20` 表示，或採用不含空白、括弧的檔名。

第一版收集 inline Markdown 圖片與其雜湊。Obsidian `![[...]]`、reference-style image、raw HTML 圖片，
以及外部圖片網址會明確報錯；請轉成上述本機圖片格式。相對路徑不能離開此 BRD 的 `assets/`。
這是本地來源匯入工具，不會下載外部圖片、執行文件指令、OCR 或判讀圖片。
BRD 內需要分析的其他附件也請先整理成文字／表格或圖片；一般超連結不會自動當成已讀附件。

圖片是 OKF 筆記引用的二進位附件，維持 PNG、JPEG 等原格式。使用者原文與圖片均不被匯入工具重寫。

## 建立有來源的需求評估

```bash
python scripts/init_requirement.py <REQ-ID> --source vault/intake/<BRD-ID>/brd.md
```

`--source` 可重複指定多份文件，路徑相對於 Repository 根目錄。一份 BRD 可供多個 REQ 評估引用。
無 `--source` 時保留既有空白 intake 流程。工具會：

1. 檢查文件 ID、條目 ID 與圖片路徑，保留 BRD 和附件的原始位元組。
2. 在 `knowledge/sources.md` 登錄 `kind: brd`、文件 `id` 與 Repository-relative `path`。
3. 在 `requirement.md` 的 `source_documents` 保存來源快照、條目清單與圖片待判讀紀錄。
4. 在 `traceability.md` 的 `source_coverage` 為所有原始條目建立 `pending` 紀錄。
5. 在需求正文加入可點擊的來源連結，保持 intake 和未就緒狀態。

這些動作只表示來源已登錄，不表示需求已分析、圖片已看過或使用者已批准。
在 Obsidian 可從需求頁直接開啟 BRD。引用個別條目時，於該相對路徑加上 `#br-001`。

## 資料契約

所有新增的分析欄位都放在原有 Project Data 頁面的唯一資料區塊中。

| 欄位 | 意義 |
|---|---|
| `requirement.source_documents[].id / path` | 文件 ID 與 Repository-relative BRD 路徑 |
| `sha256 / item_ids / assets` | BRD 原文 bytes 雜湊、原始條目清單、正文引用的圖片清單 |
| `source_revision` | BRD 路徑、bytes hash、所有引用圖片路徑與 bytes hashes 的 manifest SHA-256 |
| `captured_at / git_commit` | 實際擷取時間與當時 Project Repository HEAD；未有 Git commit 時為 null |
| `assets[].path / sha256` | 個別圖片位置與 bytes 雜湊 |
| `assets[].review_status` | pending、reviewed 或 unreadable |
| `reviewed_by / reviewed_at / notes / question_ids` | 圖片判讀者、時間、觀察／限制與待解問題 |
| `functional_requirements[].source_refs` | 每筆含 `document_id` 和 `item_id`，可引用多個原始條目 |
| `traceability.source_coverage` | 每筆以 `document_id` 和 `item_id` 識別原始條目 |

`git_commit` 只提供背景，可能尚未包含工作區中的 BRD 修改；精確內容以 bytes hashes 為準。
每個 FR 的 `source_refs` 都需指向已擷取文件的真實條目。Agent 推導出的功能也要引用支持它的原文，
並在敘述中標示推導理由，不得聲稱使用者已明確提出所有實作細節。

`source_coverage` 的每筆紀錄都有 `disposition`、`functional_requirement_ids`、`question_ids`、`reason`、`decision_ref`：

| disposition | 必要內容／排程條件 |
|---|---|
| pending | 尚待分析；阻擋 planning readiness |
| analyzed | 至少一個 FR；與該 FR 的 `source_refs` 雙向一致 |
| needs-clarification | 指向存在的 question；阻擋 planning readiness |
| deferred | 說明延後原因，無本次 FR 對應；排程前需有 `decision_ref` |
| excluded | 說明不納入本次 REQ 的原因，無本次 FR 對應；排程前需有 `decision_ref` |

每份引用 BRD 的全部原始條目都要且只能出現一次。拆成多個 REQ 時，每個 REQ 都記錄自己的範圍；
其他 REQ 處理的條目可列 excluded，原因與決策連結指向該分工紀錄。這不表示整個專案已取消該需求。
工具檢查引用完整性與一致性，不能驗證決策是否真的由所述人員批准。

來源證據仍放在 `evidence.md`。BRD evidence 使用文件 ID 作為 `source_id`，`path` 為完整 Repository-relative
BRD 路徑（可加條目 anchor）或其中圖片路徑，`source_revision` 必須匹配本次快照的 manifest revision。
`observed_at`、`claim`、`state` 沿用原契約。原文證明「使用者提出這項需求」，不直接證明現行系統已如此運作。

## 圖片判讀與分析

Agent 必須實際開啟相關圖片，才可改成 reviewed，並填入判讀者、時間及具體觀察。
看不到、不清楚或工具不支援時標為 unreadable，填寫原因及 question IDs。未完成判讀會阻擋排程。
表格或圖中無法確認的規則需保留問題，不能從圖片檔名或圖說補成事實。
BRD 維持原始語言，Agent 新寫的分析依 `documentation_language`；原文引用保留原語言。

## 來源更新與重新評估

修改 BRD 或引用圖片後，驗證器會提示快照過期。先保留可追溯的 Git 版本，再執行：

```bash
python scripts/refresh_brd.py --requirement <REQ-ID>
python scripts/validate.py --requirement <REQ-ID>
```

refresh 只處理草案：重新擷取已變更文件、將其條目改回 pending、重設圖片判讀，並清除排程準備度與舊審查。
既有 FR、AC、問題、證據與來源引用都保留。新增條目補入涵蓋表；已刪除條目的舊引用仍留下，
驗證器會指出懸空引用，需由分析流程明確處理。舊 evidence revision 也需在重新閱讀後更新。
未變更來源保持原快照，重複 refresh 不會抹除未受影響的判讀紀錄。
baseline 或 closed 的需求會拒絕 refresh，應先經 change-control 建立新的變更評估。

完成分析後執行 `python scripts/validate.py --requirement <REQ-ID> --planning`。
原始條目未處理、圖像未判讀、來源過期或引用不一致時不能排程。排程輸出另保存 BRD 與圖片輸入 hashes。

[原始需求目錄](../intake/index.md) · [資料契約](data-contract.md) · [文件目錄](index.md)
