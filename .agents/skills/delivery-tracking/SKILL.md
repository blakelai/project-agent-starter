---
name: delivery-tracking
description: Track delivery from backlog handoff through progress, acceptance and closure. Use for tracker mappings, status reports, actual and remaining effort updates, milestone reviews, acceptance evidence, or closing completed/cancelled scope.
---

# 交付追蹤

1. 讀取 AGENTS.md、vault/docs/project-workflow.md、vault/docs/planning-and-delivery.md、計畫與基準。
   遵守共用語言、OKF、證據及外部操作權限。執行 `workflow.py --requirement <REQ-ID> --stage delivery` 補上交付文件。
2. 交接工作時讀 [Backlog 對映](references/backlog-handoff.md)，保留 REQ/WP 到 tracker 的穩定對映。
   外部 ID 未查到就保持未知；不自行建立工單、改 sprint、指派他人或發送訊息。
3. 更新進度時讀 [成果與報告](references/progress-reporting.md)，以同一 as_of 日期記錄每個 WP 的狀態、
   實際投入、剩餘工時情境與阻擋。完成需日期及證據，未知實際投入保留 null 並說明原因。
4. 區分開發完成、測試通過及業務接受。人類的 AC 接受或豁免紀錄寫入 traceability.md；
   不以 PR、commit、已花工時或 Agent 檢查通過替代人類驗收。
5. 用 `validate.py --requirement <REQ-ID> --stage delivery` 驗證進度；把剩餘工作交 delivery-planning 計算。
   未知剩餘工時、未定解除日期的阻擋不產生假精準的完成日。容量／範圍變更交 change-control。
6. 關閉前要求完整的驗收或具理由的人類豁免、工作完成／取消紀錄，以及人類結案決策。
   用 `validate.py --requirement <REQ-ID> --stage closure`，通過後執行 `close_requirement.py --requirement <REQ-ID>`。
7. 記錄實際範圍、測量方法與經驗；只把可比較且已測量的結果回填歷史資料。不修改歷史基準。
