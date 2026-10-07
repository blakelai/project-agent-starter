---
type: Project Guide
title: 規劃與交付資料契約
description: 專案範圍、阻塞關卡、進度預測、驗收與不可覆寫基準的欄位規則。
status: draft
---

# 規劃與交付資料契約

本頁補充 [資料契約](data-contract.md)，完整操作順序見 [工作流程](project-workflow.md)。
所有下列欄位均位於各 Markdown 文件唯一的 `project-data` 區塊，維持 `schema_version: 1`。

## 專案範圍與共同容量

`init_project.py <PROJ-ID>` 建立 `vault/projects/<PROJ-ID>/project.md`。
Repository 的 `vault/config/project.md` 是共用設定，這份 project.md 是本次排程的範圍選擇及專案目標。

| 欄位 | 型別與規則 |
|---|---|
| `id` | PROJ- 開頭，與資料夾一致 |
| `name`、`owner`、`goal` | 非空字串，基於實際專案決策 |
| `success_criteria`、`scope`、`non_goals` | 字串清單；排程時前兩者不可為空 |
| `requirements` | 每筆 `{id, priority}`；REQ ID 不可重複，priority 為整數，越小越優先 |
| `dependencies` | 每筆 `{predecessor, successor}`；兩端各含 `requirement_id`、`work_package_id`，須屬選定範圍內的 WP |

REQ 內相依仍寫在 WBS 的 `depends_on`；跨 REQ 的相依放在專案 dependencies。
計算時以 `REQ-ID/WP-ID` 區別不同需求中相同的 WP ID，將兩種相依合併檢查循環。
所有選定需求共用 `vault/planning/capacity.md` 及 calendar；先按 REQ priority，再按 WP priority 和 ID 排序。
這些 priority 是候選工作選擇順序，不能越過相依、日期與容量限制。

不同 PROJ 的獨立執行不會自動保留或扣除彼此資源。同一資源池的所有競爭工作，應選入同一份排程；
範圍外固定工作必須已從淨容量扣除。工具不進行組織級資源預約或最佳化。

## 按階段阻塞的問題

requirement.questions 保留既有 `id`、`question`、`owner`、`blocking`、`status`，可增加：

| 欄位 | 行為 |
|---|---|
| `blocks` | 非空關卡清單：requirements、planning、delivery、closure；未提供時涵蓋四者 |
| `affected_work` | 可選 WP ID 清單；有值時必須存在，作影響說明，不會自動移除排程工作 |
| `answer`、`source` | status=resolved 時必填；保留回答內容和來源 |

開啟且 blocking=true 的問題，從 blocks 指定的最早關卡起，連同之後的關卡均受阻。
例如只影響估算的問題可以 blocks=[planning]，使需求語義審查先完成；未知業務詞義仍必須阻擋 requirements。
工具仍獨立檢查 BRD／術語，不能靠更改 blocks 或標為 background 繞過真正的語義依賴。
問題可按影響安排獨立分析，但一份 REQ 通過規劃前，其適用的阻塞必須解除。

## 階段與狀態

| requirement 的資料狀態 | 至少檢查到 |
|---|---|
| `intake` | 核心檔案及已填資料的結構 |
| `clarified` | requirements：需求、來源、術語及語義阻塞；不要求完整拆工／估算 |
| `assessed`、`baseline` | planning：WBS、估算、風險對映、完整 AC 追蹤及規劃資料 |
| `in-progress` | delivery：上述條件及進度覆蓋與紀錄 |
| `closed` | closure：上述條件及工作、AC、阻塞、人類結案決策 |

`--stage` 提高最低關卡；`--planning` 另要求 `ready_for_planning: true`、review metadata 和 assumptions。
readiness=true 本身也強制完整規劃檢查。狀態不會因為建立文件而自動前進。
assessment 的 `status: draft|baseline` 是另一個欄位；frontmatter 的 `status: draft|stable|deprecated` 則是知識生命週期。

需求關卡只需要 requirement、evidence、assessment、traceability。
規劃關卡增加 work-breakdown、estimation、risks；workflow 指令也會建立易讀的 project-plan 和 assessment-review。
solution-assessment 是可選敘述頁；重大決策另寫 ADR。
早期風險可用 `affected_requirements` 指向 FR、`affected_work: []`、`treatment: monitor-only`；
進入規劃時必須映射受影響 WP，並選擇實際風險處置。

## 進度紀錄

`progress.md` 包含 `as_of`（YYYY-MM-DD）、`work`、`blockers`、`closure`。
work 必須一對一涵蓋目前全部 WP；觀測截至 as_of 當日結束。

| work 每筆欄位 | 要求 |
|---|---|
| `id` | 本 REQ 的 WP ID，不加 REQ 前綴 |
| `status` | not-started、in-progress、blocked、done、cancelled |
| `actual_effort_pd` | 有限且非負數；未知用 null，另填 `actual_unknown_reason` |
| `remaining_effort_pd` | `{low, expected, high}`；有限、非負且依序不減；一般紀錄可為 null，預測時不得未知 |
| `completed_on`、`completion_evidence` | done 必填；完成日不可晚於 as_of |
| `cancellation` | cancelled 必填 `{by, at, source, reason}`，不得由 Agent 默認取消 |
| `resume_on`、`resume_source` | blocked 要做預測時必填；解除日期必須晚於 as_of，並保留日期依據 |

done／cancelled 的三個剩餘工時均須為 0；要排程的工作三個值均須大於 0。
not-started 的實際投入可記已確認的 0，不能把未知 actuals 補成 0。
狀態、實際投入及剩餘量的來源或估算理由寫在同頁正文；計算工具不判斷數字是否合理。

blockers 每筆含唯一 `id`、`description`、`owner`、`status: open|resolved`、`work_packages`。
解除時增加 `resolution`。記錄工作阻塞時也要把受影響 work 狀態設為 blocked，以供預測辨識；
預測時 open blockers 必須列明受影響 WP，且它們的工作狀態必須為 blocked；
只有報告文字不能自動推導可開工日期。

## 剩餘工作預測

`schedule_project.py --as-of <YYYY-MM-DD>` 要求所有選定 REQ 的 progress.as_of 完全相同，
並通過 delivery 和排程 readiness 檢查。預測從截止日次日開始，保留原始 progress；
排程工作量採各 WP 明確估計的 remaining_effort_pd，不用原估算扣 actuals。
完成及取消的 WP 不再消耗未來容量，已完成的前置工作視為滿足；
取消的前置工作必須先明確調整相依，不能當作已完成。

報表記錄 `mode: remaining-work`、`as_of`、`observed_work`、`actual_effort_known_pd`、
`actual_effort_unknown`、選定需求及輸入 hashes。未知 actuals 可以保留，但未知剩餘量或阻塞解除日期不能產生預測。
所有工作均完成／取消時，輸出 `no_remaining_work: true`、零剩餘工時及空 tasks；報表日期為截止日，
並非自行認定實際完成日或已驗收。

情境仍採 full-day、single-assignee greedy 模型，不插入歷史 actuals 到未來 allocations；
同日尾端剩餘容量不挪給另一 WP，沒有搶占、多人協作拆分、資源最佳化或機率信賴度計算。
報告分開比較基準日期、範圍及目前情境差異；不得將 high 情境稱為 project P80。

## 人類驗收與結案

在 `traceability.md` 的每個 links 項目增加 `acceptance`；結案時每個 AC 只能有一筆紀錄，
多個 WP 合併列在同一筆 work_packages，不建立重複 AC rows。

| 欄位 | 規則 |
|---|---|
| `acceptance.status` | accepted 或 waived |
| `acceptance.by`、`acceptance.at`、`acceptance.source` | 實際人類決策者、含時區 ISO 時間及可追溯來源 |
| `acceptance.reason` | waived 必填，說明人類接受的例外或取消範圍 |
| `test_status`、`test_evidence` | accepted 要求 passed 及證據；waived 不把原本 planned／failed 偽改為 passed |

progress.closure 由 null 改為 `{by, at, source, summary}`；summary 說明交付範圍、結果、限制與教訓。
通過 closure 還要求每個 WP done／有理由的 cancelled、所有 delivery blockers resolved。
`close_requirement.py` 在這些條件通過後才改 status；不建立核准、不修改測試結果。
回填歷史資料時，只有確實量測且可比較的投入可當 actual PD，不能用週期長度或預估數字替代。

## 基準與可重現性

`baseline.py preview` 核對報表的 input_sha256 是否仍吻合，輸出整組輸入加指定報表的 revision。
人類須確認這個版本；`create --revision ... --by ... --at ... --source ...` 保存記錄、
原始 bytes 與 SHA-256 清單到 `baseline/<版本>/snapshot/`，拒絕覆寫或保存已變更的輸入。
`verify` 檢查 manifest、缺檔、額外檔案和內容 hashes。

快照包含選定需求的輸入文件、同目錄下的附件及巢狀決策文件、共用規劃／設定／sources、引用的 BRD／術語及其附件，以及指定的一份排程報表。
Source Repository 程式碼仍依 evidence 中的 revision 定位，不複製整個外部 Repository。
Live 需求可保持 assessed／in-progress，基準用獨立快照凍結；create 不會把 live status 自動改成 baseline。
舊的 baseline／closed 需求仍受來源 refresh 保護，需另立經授權的變更評估。

SHA-256 是一致性檢查，不是人類身分驗證或數位簽章；能直接改檔者也能改 hashes。
Git 保護、review 與核准來源由團隊管理。`validate.py --all` 做通用筆記及需求檢查；
專案排程範圍與跨需求相依由 schedule_project 檢查，基準 bytes 完整性須另跑 baseline verify。

[工作流程](project-workflow.md) · [資料契約](data-contract.md) · [回到目錄](index.md)
