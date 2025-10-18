# 🎓 成功大學畢業審查系統

一個用於驗證學生課程是否符合系所畢業要求的自動化審查系統。

## 📖 專案概述

本系統包含：
- **後端：** Python FastAPI + Pydantic 規則引擎
- **前端：** Vue 3 + Quasar Framework
- **資料：** JSON 檔案存儲（學生資料、畢業規則）

## 🚀 快速開始

### 前置需求

- Python 3.10+
- Node.js 20+
- npm 或 yarn

### 安裝依賴

```bash
# 後端
cd backend
pip install -r requirements.txt

# 前端
cd frontend
npm install
```

### 啟動開發環境

**方法 1：使用啟動腳本（推薦）**

```bash
./start-dev.sh
```

**方法 2：手動啟動**

```bash
# 終端 1 - 後端
cd backend
python run.py --reload

# 終端 2 - 前端
cd frontend
quasar dev
```

### 訪問應用

- **前端應用：** http://localhost:9000
- **後端 API：** http://127.0.0.1:8000
- **API 文檔：** http://127.0.0.1:8000/docs

## 📁 專案結構

```
Graduation-review-system/
├── backend/                 # Python FastAPI 後端
│   ├── api/                # API 路由和模型
│   │   ├── routers/        # API 端點
│   │   ├── crud/           # 資料庫操作
│   │   └── models/         # API 模型
│   ├── rule_engine/        # 規則引擎核心
│   │   ├── models/         # 領域模型
│   │   ├── evaluator.py    # 評估器註冊系統
│   │   ├── factory.py      # 工廠模式
│   │   └── utils.py        # 工具函數
│   ├── data/               # 資料存儲
│   │   ├── students/       # 學生 JSON 檔案
│   │   ├── rules/          # 畢業規則檔案
│   │   └── departments_info.json
│   ├── crawler/            # 課程爬蟲
│   ├── rule_updater/       # 規則生成器
│   ├── cli.py              # CLI 工具
│   └── run.py              # 啟動腳本
│
├── frontend/               # Vue 3 + Quasar 前端
│   ├── src/
│   │   ├── pages/          # 頁面組件
│   │   ├── layouts/        # 佈局組件
│   │   ├── router/         # 路由配置
│   │   ├── boot/           # 啟動檔案（axios）
│   │   └── stores/         # Pinia 狀態管理
│   └── quasar.config.js    # Quasar 配置
│
└── [文檔檔案]
    ├── CONNECTION_GUIDE.md        # 前後端連接指南
    ├── TESTING_GUIDE.md           # 測試指南
    ├── COMPLETION_REPORT.md       # 完成報告
    └── .github/
        └── copilot-instructions.md # AI 協作指南
```

## 🎯 功能特性

### ✅ 已實現功能

#### 學生資料管理
- 上傳 Excel 批量匯入學生資料
- 查看學生列表（學號、姓名、主修科系）
- 搜尋學生（學號或姓名）
- 查看學生詳細資料（包含完整修課記錄）
- 刪除學生資料
- 成績狀態顯示（及格/不及格/修課中/抵免）

#### 規則引擎（CLI）
- 規則評估器註冊系統
- 課程匹配與認證
- 學分計算
- 畢業要件檢查

### 🚧 開發中功能

- 規則資料管理頁面
- 開始審查頁面
- 審查結果頁面

## 🔌 API 端點

### 學生管理

| 方法 | 端點 | 說明 |
|------|------|------|
| GET | `/students/` | 取得所有學生列表 |
| GET | `/students/{id}` | 取得特定學生詳細資料 |
| POST | `/students/upload-excel` | 上傳 Excel 批量匯入 |
| DELETE | `/students/{id}` | 刪除特定學生 |
| DELETE | `/students/` | 刪除所有學生 |

詳細 API 文檔請見：`backend/README_API.md`

## 📊 Excel 檔案格式

上傳的 Excel 檔案需包含以下欄位：

| 欄位 | 說明 | 範例 |
|------|------|------|
| 學號 | 學生學號 | A1110001 |
| 姓名 | 學生姓名 | 張三 |
| 課程名稱 | 課程名稱 | 微積分（一） |
| 課程碼 | 課程代碼 | E215611 |
| 學分數 | 課程學分 | 3.0 |
| 成績 | 課程成績 | 85 / 999（修課中）/ 555（抵免） |
| 承抵課程別 | 承抵類別 | - |
| 選必修 | 0或1=必修，2=選修 | 1 |
| 學年 | 修課年度 | 111 |
| 學期 | 修課學期 | 1 |

## 🧪 測試

請參考 `TESTING_GUIDE.md` 進行完整的功能測試。

簡易測試：

```bash
# 測試後端健康狀態
curl http://127.0.0.1:8000/health

# 測試學生 API
curl http://127.0.0.1:8000/students/
```

## 🛠️ 開發工具

### CLI 工具

```bash
# 使用互動式 CLI
cd backend
python cli.py
```

功能包括：
- 從 Excel 載入學生資料
- 選擇學生進行畢業審查
- 自動選擇適用規則
- 生成審查報告

### 規則生成器

```bash
cd backend
python -m rule_updater.generator
```

用於創建新的畢業規則檔案。

## 📚 技術文檔

- **前後端連接：** `CONNECTION_GUIDE.md`
- **API 文檔：** `backend/README_API.md`
- **測試指南：** `TESTING_GUIDE.md`
- **整合總結：** `INTEGRATION_SUMMARY.md`
- **完成報告：** `COMPLETION_REPORT.md`
- **AI 協作：** `.github/copilot-instructions.md`

## 🔧 配置

### 環境變數

前端（`frontend/.env`）：
```bash
API_URL=http://127.0.0.1:8000
```

### 開發配置

- **前端端口：** 9000
- **後端端口：** 8000
- **代理：** `/api` → `http://127.0.0.1:8000`

## 🐛 問題排查

### CORS 錯誤

確認後端 CORS 設置（`backend/api/main.py`）包含前端 URL。

### 連接失敗

1. 確認後端服務器運行中
2. 檢查端口是否被占用
3. 查看瀏覽器開發者工具 Network 標籤

詳細排查步驟請見 `TESTING_GUIDE.md`。

## 📖 系統架構

### 規則引擎

使用**評估器註冊模式**：

```python
@register_evaluator("rule_all")
class RuleAllEvaluator:
    def evaluate(self, rule, student_courses) -> Result:
        # 評估邏輯
```

### 資料流程

```
使用者 → 前端 Vue → Axios → Proxy → FastAPI → CRUD → JSON 檔案
```

## 🤝 貢獻

本專案使用繁體中文進行開發：
- 所有註解使用繁體中文
- API 訊息使用繁體中文
- UI 文字使用繁體中文

## 📝 授權

[待補充]

## 👥 作者

YU jin-xuan <xzyujinxuan@gmail.com>

## 🙏 致謝

- Quasar Framework
- FastAPI
- Pydantic
- 成功大學

---

**最後更新：** 2025-10-17  
**版本：** 1.0.0  
**狀態：** 開發中 🚧
