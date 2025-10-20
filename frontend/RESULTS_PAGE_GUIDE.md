# 審查結果管理頁面

## 功能概述

`ResultsPage.vue` 是審查結果管理頁面，提供查看、刪除審查結果的完整功能。

## 主要功能

### 1. 結果列表

- 顯示所有已保存的審查結果
- 表格欄位：
  - 檔案名稱
  - 學號
  - 姓名
  - 操作按鈕（查看、刪除）
- 支援排序和分頁

### 2. 查看詳細結果

- 點擊「查看詳細」按鈕開啟詳細對話框
- 顯示學生基本資訊：
  - 姓名
  - 學號
  - 科系
  - 入學年度
- 使用 `ReviewResultTree` 元件展示審查結果樹狀結構
- 完整顯示規則檢查結果、學分統計、已修課程列表

### 3. 刪除功能

- **刪除單一結果**：點擊刪除按鈕，確認後刪除指定檔案
- **刪除所有結果**：頁面右上角按鈕，可一次刪除所有審查記錄
- 刪除前都會顯示確認對話框

## API 調用

頁面使用以下 API 端點（定義於 `results_router.py`）：

```javascript
// 1. 取得所有結果列表
GET http://localhost:8000/api/results/

// 2. 取得特定檔案的詳細資訊
GET http://localhost:8000/api/results/file/{filename}

// 3. 刪除特定檔案
DELETE http://localhost:8000/api/results/file/{filename}

// 4. 刪除所有結果
DELETE http://localhost:8000/api/results/
```

## 元件結構

```vue
ResultsPage.vue ├── 結果列表表格 (q-table) │ ├── 檔案名稱欄位 │ ├── 學號欄位 │ ├── 姓名欄位 │ └──
操作欄位 │ ├── 查看按鈕 │ └── 刪除按鈕 ├── 詳細結果對話框 (q-dialog) │ ├── 學生資訊橫幅 (q-banner) │
└── 審查結果樹 (ReviewResultTree) └── 刪除確認對話框 (q-dialog)
```

## 資料流程

### 載入結果列表

1. 頁面掛載時自動調用 `loadResults()`
2. 向後端發送 GET 請求至 `/api/results/`
3. 接收 `ResultBasicInfo[]` 列表
4. 更新表格顯示

### 查看詳細

1. 使用者點擊「查看詳細」按鈕
2. 調用 `viewResult(result)` 方法
3. 向後端發送 GET 請求至 `/api/results/file/{filename}`
4. 接收完整的審查結果 JSON 資料
5. 開啟全螢幕對話框顯示詳細內容
6. 使用 `ReviewResultTree` 元件遞迴渲染結果樹

### 刪除結果

1. 使用者點擊刪除按鈕
2. 開啟確認對話框顯示警告訊息
3. 確認後調用 `executeDelete()`
4. 向後端發送 DELETE 請求
5. 成功後重新載入結果列表

## 資料結構範例

### 結果列表項目 (ResultBasicInfo)

```json
{
  "file_name": "AN4116089_20_Oct_2025_13_10.json",
  "student_id": "AN4116089",
  "student_name": "黃品瑞"
}
```

### 詳細結果資料

詳細資料結構參考 `AN4116089_20_Oct_2025_13_10.json`，包含：

- 學生基本資訊（name, id, major, admission_year）
- main: 主要審查結果樹
  - 規則名稱、描述
  - 是否通過 (is_valid)
  - 獲得學分 (earned_credits)
  - 子規則 (sub_results)
  - 已修課程列表 (finished_course_list)

## 元件復用

頁面重複使用了審查功能的展示元件：

- **ReviewResultTree.vue**：遞迴顯示審查結果樹狀結構
  - 支援 RuleSet（規則組合）和 RuleAll（課程列表）兩種類型
  - 自動展開/收合子規則
  - 顯示課程表格，包含課程名稱、學分、狀態、修課學期

## 使用說明

1. **訪問頁面**：在側邊欄點擊「審查結果」或訪問 `/results` 路徑
2. **查看列表**：自動載入所有已保存的審查結果
3. **查看詳細**：點擊眼睛圖示查看完整審查報告
4. **刪除記錄**：
   - 單一刪除：點擊刪除圖示，確認後刪除
   - 批量刪除：點擊「刪除所有結果」按鈕，確認後清空所有記錄

## 注意事項

- 刪除操作無法復原，執行前請謹慎確認
- 結果檔案存儲在後端 `data/evaluation_results/` 目錄
- 檔案命名格式：`{學號}_{日期}_{時間}.json`
- 頁面使用全螢幕對話框顯示詳細結果，提供更好的閱讀體驗

## 相關檔案

- 前端頁面：`frontend/src/pages/ResultsPage.vue`
- 結果樹元件：`frontend/src/components/ReviewResultTree.vue`
- 後端路由：`backend/api/routers/results_router.py`
- 後端 CRUD：`backend/api/crud/result_crud.py`
- 資料模型：`backend/api/models/result_models.py`
- 路由配置：`frontend/src/router/routes.js`
- 主佈局：`frontend/src/layouts/MainLayout.vue`
