# 共同容量與剩餘工作預測

1. 讀取 vault/projects/<PROJ-ID>/project.md 的目標、範圍、成功標準、需求優先序與跨需求依賴。
2. 確認所有選定 REQ 均通過規劃審查，淨容量已扣除範圍外活動；同一份計畫只能使用容量一次。
3. 使用 schedule_project.py 的 expected/high 情境；選定集合以外的專案不會被自動預留資源。
4. 預測時使用所有 REQ 一致的 as_of、逐 WP 的實際狀態及剩餘工時。截止日含當日，排程從次日開始。
   已完成與已取消工作不重排；取消前置工作不能自動當作相依已滿足。未知剩餘工時或解除日期會拒絕預測。
5. 未知實際投入保留未知，不使用 ticket 經過時間推算人日。報告區分已知實際投入與待排剩餘工作。
6. 模型仍是單人／WP、整日保留、finish-to-start 的 greedy 可行情境；不是最佳解、機率百分位或時段排程。
7. 先 baseline.py preview，讓人類確認報表及確切輸入版本，才以 create 記錄 by/at/source/revision。
   verify 檢查保存的 bytes；它不能證明人類身分或業務決策正確。
