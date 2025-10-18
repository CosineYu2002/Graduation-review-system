# 畢業審查系統 - 前後端連接指南

## 🚀 快速啟動

### 1. 啟動後端 API 服務器

```bash
cd backend
python run.py --reload
```

後端將在 `http://127.0.0.1:8000` 運行

### 2. 啟動前端開發服務器

```bash
cd frontend
npm install  # 首次運行需要安裝依賴
quasar dev
```

前端將在 `http://localhost:9000` 運行（默認端口）

## 🔗 前後端連接配置

### 開發環境

前端通過 Vite proxy 連接後端，避免 CORS 問題：

**配置位置：** `frontend/quasar.config.js`

```javascript
devServer: {
  proxy: {
    '/api': {
      target: 'http://127.0.0.1:8000',
      changeOrigin: true,
      rewrite: (path) => path.replace(/^\/api/, ''),
    },
  },
}
```

**前端請求示例：**
```javascript
// 實際請求 /api/students/
// 會被代理到 http://127.0.0.1:8000/students/
await api.get('/students/')
```

### 後端 CORS 設置

**配置位置：** `backend/api/main.py`

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:9000",
        "http://127.0.0.1:9000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## 📝 測試連接

1. 確保後端服務器運行中
2. 訪問 `http://127.0.0.1:8000/docs` 查看 API 文檔（Swagger UI）
3. 訪問 `http://127.0.0.1:8000/health` 確認健康狀態
4. 在前端應用中點擊「學生資料」頁面
5. 嘗試上傳 Excel 或查看學生列表

## 📊 Excel 檔案格式

上傳的 Excel 檔案需要包含以下欄位：

| 欄位名稱 | 說明 | 範例 |
|---------|------|------|
| 學號 | 學生學號 | A1110001 |
| 姓名 | 學生姓名 | 張三 |
| 課程名稱 | 課程名稱 | 微積分（一） |
| 課程碼 | 課程代碼 | E215611 |
| 學分數 | 課程學分 | 3.0 |
| 成績 | 課程成績 | 85 或 999（修課中）或 555（抵免） |
| 承抵課程別 | 承抵類別 | - |
| 選必修 | 0或1=必修，2=選修 | 1 |
| 學年 | 修課年度 | 111 |
| 學期 | 修課學期 | 1 |

## 🐛 常見問題

### 1. CORS 錯誤
**錯誤訊息：** `Access to XMLHttpRequest has been blocked by CORS policy`

**解決方法：**
- 確認後端 CORS 設置正確
- 確認前端 proxy 配置正確
- 重啟前後端服務器

### 2. 連接被拒絕
**錯誤訊息：** `net::ERR_CONNECTION_REFUSED`

**解決方法：**
- 確認後端服務器正在運行
- 檢查端口是否被占用
- 確認防火牆設置

### 3. 上傳檔案失敗
**錯誤訊息：** `只支援 .xlsx 格式檔案`

**解決方法：**
- 確保檔案格式為 .xlsx（不是 .xls 或 .csv）
- 檢查檔案大小是否超過 10MB
- 確認 Excel 檔案包含所有必需欄位

### 4. 學生資料顯示為空
**可能原因：**
- `backend/data/students/` 目錄不存在或為空
- JSON 檔案格式錯誤

**解決方法：**
- 先上傳 Excel 檔案創建學生資料
- 檢查 `backend/data/students/` 目錄權限

## 📁 資料存儲位置

- **學生資料：** `backend/data/students/*.json`
- **畢業規則：** `backend/data/rules/<系所代碼>/<入學年度>.json`
- **系所資訊：** `backend/data/departments_info.json`

## 🔧 開發工具

### API 測試工具

1. **Swagger UI:** `http://127.0.0.1:8000/docs`
2. **ReDoc:** `http://127.0.0.1:8000/redoc`

### 瀏覽器開發者工具

- **Network Tab:** 查看 API 請求和響應
- **Console Tab:** 查看前端錯誤訊息

## 📚 更多資訊

- 後端 API 文檔：`backend/README_API.md`
- 前端使用說明：`frontend/README.md`
- AI 協作指南：`.github/copilot-instructions.md`
