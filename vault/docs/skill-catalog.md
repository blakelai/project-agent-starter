---
type: Project Guide
title: 專案管理 Skills
description: 9 個 Repository-local Skills 的責任與舊名稱遷移對照。
status: draft
---

# 專案管理 Skills

這 9 個 Skills 是本 Repository 的專案工作流程，放在 `.agents/skills/`，不是安裝到個人環境的 Skills。
日常步驟及命令見 [專案工作流程](project-workflow.md)；共用原則集中於 `AGENTS.md`。
Skill 的 `SKILL.md`、隨附參考文件及 host 顯示資訊統一以英文維護；產生的專案文件仍依 `documentation_language`。
Skill 數量不等於流程步驟數量；可依目前問題只執行其一個子步驟。

| Skill | 何時使用 | 主要產物／責任 |
|---|---|---|
| `knowledge-bootstrap` | 初始化專案、加入來源、檢索失敗或證據過期 | 專案目標、來源 routing、checkout 對映、知識與 freshness |
| `requirement-analysis` | 新需求、BRD 匯入、範圍及驗收釐清 | 原始條目到 FR／AC 的追蹤、問題與需求關卡 |
| `domain-terminology` | 未知詞義、上下文衝突、譯名或定義變更 | 共用詞彙、人類問題、精確版本確認及需求影響 |
| `solution-assessment` | 行為或合約影響、需要比較方案及技術取捨 | 一份影響／方案評估；重大決策寫 ADR，簡單需求可沿用既有方案 |
| `delivery-planning` | 拆工、估算、排程或預測更新 | WBS、PD 情境、跨 REQ 共同容量排程及剩餘工作預測 |
| `risk-analysis` | 任何階段的不確定性、外部依賴或觸發條件改變 | 風險 owner、trigger、mitigation 及工作／需求對映 |
| `assessment-review` | 需求、規劃、交付及結案關卡，或恢復工作 | 一致性與證據審查；資料驗證與人類判斷分開 |
| `delivery-tracking` | Backlog 交接、進度觀測、週報、驗收與結案 | Tracker 草案、實際紀錄、AC 接受、結案與歷史回饋 |
| `change-control` | 範圍、容量、相依或基準假設變更 | 差異、受影響階段、決策與新基準，不覆寫已核准歷史 |

Skills 自動發現方式依 Agent host 而異；必要時明確要求讀取 `.agents/skills/<名稱>/SKILL.md`。
本地原生 SKILL.md / agents/openai.yaml 保持 host 格式；產出的專案文件放在 OKF Vault。

## 舊名稱對照

原工作流程已有 12 個 Skills，加入領域詞彙後為 13 個；這次整併為 9 個。
合併的是操作入口，詳細工作方法保留為 references，按需載入。

| 舊 Skill | 新 Skill | 保留的子步驟 |
|---|---|---|
| `impact-analysis`、`architecture-review` | `solution-assessment` | 影響檢查、重大架構取捨 |
| `work-breakdown`、`effort-estimation`、`project-planning` | `delivery-planning` | 拆工、估算、共同容量與預測 |
| `backlog-handoff`、`progress-reporting` | `delivery-tracking` | Backlog 對映、成果與報告、驗收結案 |
| 其餘 6 個 | 名稱保留 | 知識、需求、領域詞彙、風險、審查、變更 |

更新既有 prompts 中的舊 Skill 名稱即可；既有 impact-analysis、architecture-options、decisions 等文件
仍可保留引用，不必只為遷移而重寫。新的需求預設僅建立四份核心頁，後續文件按階段加入。
外部設計參考見 [HVE Core](hve-reference.md)，本 Repository 未 vendor 上游 Skills。

[工作流程](project-workflow.md) · [回到目錄](index.md)
