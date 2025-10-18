# 前後端連接配置總結

## ✅ 已完成的配置

### 1. 後端配置 (`backend/api/main.py`)

添加了 CORS 中間件，允許前端訪問：

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:9000",
        "http://127.0.0.1:9000",
        "http://localhost:8080",
        "http://127.0.0.1:8080",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### 2. 前端 Axios 配置 (`frontend/src/boot/axios.js`)

配置了開發和生產環境的 API URL：

```javascript
const api = axios.create({ 
  baseURL: process.env.DEV ? '/api' : (process.env.API_URL || 'http://127.0.0.1:8000'),
  timeout: 30000,
})
```

### 3. Quasar 開發服務器配置 (`frontend/quasar.config.js`)

添加了 proxy 代理和必要的插件：

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

framework: {
  plugins: ['Notify', 'Dialog'],
}
```

### 4. 前端學生頁面 (`frontend/src/pages/StudentsPage.vue`)

已實現的 API 對接：

- ✅ `GET /students/` - 載入學生列表
- ✅ `GET /students/{id}` - 查看學生詳細資料
- ✅ `POST /students/upload-excel` - 上傳 Excel 檔案
- ✅ `DELETE /students/{id}` - 刪除學生資料

### 5. 後端 API 端點 (`backend/api/routers/students.py`)

已實現的功能：

- ✅ 取得所有學生基本資訊
- ✅ 取得特定學生詳細資訊（包含修課列表）
- ✅ 上傳 Excel 批量新增學生
- ✅ 刪除特定學生
- ✅ 刪除所有學生

## 🚀 啟動步驟

### 終端 1 - 啟動後端

```bash
cd backend
python run.py --reload
```

### 終端 2 - 啟動前端

```bash
cd frontend
quasar dev
```

## 🧪 測試流程

1. **訪問應用**
   - 前端：`http://localhost:9000`
   - 後端 API 文檔：`http://127.0.0.1:8000/docs`

2. **測試學生資料頁面**
   - 點擊側邊欄「學生資料」
   - 應該看到空的學生列表

3. **上傳 Excel 測試**
   - 點擊「上傳 Excel」按鈕
   - 選擇 Excel 檔案
   - 輸入主修科系代號（例如：E2）
   - 點擊上傳
   - 應該看到成功通知並重新載入學生列表

4. **查看學生詳細資料**
   - 點擊學生列表中的「眼睛」圖標
   - 應該彈出對話框顯示學生的基本資訊和修課記錄

5. **刪除學生測試**
   - 點擊學生列表中的「垃圾桶」圖標
   - 確認刪除
   - 應該看到成功通知並重新載入學生列表

## 📊 API 資料流

```
前端請求流程：
┌──────────────┐
│ StudentsPage │
└──────┬───────┘
       │ api.get('/students/')
       ↓
┌──────────────┐
│   Axios      │ (baseURL: /api 或 http://127.0.0.1:8000)
└──────┬───────┘
       │
       ↓ (開發環境通過 Vite proxy)
┌──────────────┐
│ Backend API  │ GET http://127.0.0.1:8000/students/
└──────┬───────┘
       │
       ↓
┌──────────────┐
│ StudentCRUD  │ 讀取 data/students/*.json
└──────┬───────┘
       │
       ↓
┌──────────────┐
│   Response   │ { success: true, data: [...] }
└──────────────┘
```

## 🎯 API 響應格式

所有 API 都遵循統一的響應格式：

```typescript
interface APIResponse<T> {
  success: boolean
  message: string
  data: T
}
```

**成功響應範例：**
```json
{
  "success": true,
  "message": "成功取得 3 位學生的基本資訊",
  "data": [...]
}
```

**錯誤響應範例：**
```json
{
  "detail": "獲取學生列表失敗: 錯誤訊息"
}
```

## 🔍 除錯建議

### 檢查後端是否運行
```bash
curl http://127.0.0.1:8000/health
# 應返回：{"status":"healthy"}
```

### 檢查學生列表 API
```bash
curl http://127.0.0.1:8000/students/
# 應返回：{"success":true,"message":"...","data":[...]}
```

### 檢查前端 Network 請求
1. 打開瀏覽器開發者工具（F12）
2. 切換到 Network 標籤
3. 重新載入學生資料頁面
4. 查看請求：
   - Request URL 應該是 `/api/students/`（開發環境）
   - Status 應該是 200
   - Response 應該包含 JSON 資料

## 📝 下一步

前後端連接已完成，可以繼續開發：

1. ✅ 學生資料頁面已完成
2. ⏳ 規則資料頁面（待開發）
3. ⏳ 開始審查頁面（待開發）
4. ⏳ 審查結果頁面（待開發）

## 📚 相關文件

- `CONNECTION_GUIDE.md` - 完整的連接指南
- `backend/README_API.md` - 後端 API 詳細文檔
- `.github/copilot-instructions.md` - AI 協作指南
