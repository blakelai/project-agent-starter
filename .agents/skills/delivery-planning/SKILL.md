---
name: delivery-planning
description: Build traceable work packages, estimate effort, and plan shared capacity across requirements. Use for decomposition, estimation updates, project schedules, or evidence-based remaining-work forecasts; invoke only the needed substep.
---

# 交付規劃

1. 讀取 AGENTS.md、vault/docs/project-workflow.md、vault/docs/planning-and-delivery.md，以及需求與相關方案。
   遵守共用語言、OKF、證據與權責規則。先用 requirements 關卡，未釐清的依賴保持阻擋。
2. 執行 `python scripts/workflow.py --requirement <REQ-ID> --stage planning`；此動作只補文件，不核准或改狀態。
3. 需要拆工時讀 [工作分解](references/work-breakdown.md)，建立 WP、AC 對映與相依；不混入工時猜測。
4. 需要估算時讀 [工時估算](references/effort-estimation.md)，保留依據與低／預期／高情境。
   依 risk-analysis 更新風險處置，避免把同一風險同時計入估算與額外緩衝。
5. 用 `python scripts/validate.py --requirement <REQ-ID> --stage planning` 檢查規劃內容，再交 assessment-review。
   通過審查後才能設定 ready_for_planning；建立草稿與預測情境不等於對外交付承諾。
6. 排程時讀 [共同容量與預測](references/project-planning.md)。多份 REQ 必須放進同一個 project.md，
   明確列出優先序、跨 REQ 依賴，以及此次共同分配容量的完整範圍。
7. 執行 `python scripts/schedule_project.py --project <PROJ-ID> --scenario expected`，再執行 high 情境。
   schedule.py 保留為單一 REQ 的隔離情境，不能用多份獨立結果推論容量沒有衝突。
8. 更新執行後的預測時，要求 delivery-tracking 提供同一截止日的進度、實際紀錄及明確估計的剩餘工時。
   使用 `schedule_project.py --project <PROJ-ID> --as-of <YYYY-MM-DD>`；不可把原估算減掉投入時間當作剩餘估算。
9. 解釋資源與外部等待對日期的影響。人類確認具體版本後，依 baseline.py preview/create 保存基準。
   保留先前基準與實際紀錄；變更的承諾由 change-control 處理。
