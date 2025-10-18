# 畢業審查系統 API 文檔

## 啟動後端服務器

```bash
cd backend
python run.py --reload
```

服務器將在 `http://127.0.0.1:8000` 啟動

## API 端點

### 學生管理 API

#### 1. 取得所有學生列表
```
GET /students/
```

**回應範例：**
```json
{
  "success": true,
  "message": "成功取得 3 位學生的基本資訊",
  "data": [
    {
      "id": "A1110001",
      "name": "張三",
      "major": "E2"
    }
  ]
}
```

#### 2. 取得特定學生詳細資料
```
GET /students/{student_id}
```

**回應範例：**
```json
{
  "success": true,
  "message": "成功取得學生 A1110001 的詳細資訊",
  "data": {
    "id": "A1110001",
    "name": "張三",
    "major": "E2",
    "admission_year": 111,
    "courses": [
      {
        "course_name": "微積分（一）",
        "course_codes": ["E215611"],
        "credit": 3.0,
        "grade": 85,
        "category": "",
        "course_type": 1,
        "tag": [],
        "year_taken": 111,
        "semester_taken": 1,
        "recognized": false
      }
    ]
  }
}
```

#### 3. 上傳 Excel 檔案批量新增學生
```
POST /students/upload-excel
Content-Type: multipart/form-data
```

**參數：**
- `file`: Excel 檔案 (.xlsx 格式)
- `major`: 主修科系代號（例如：E2、AN）

**Excel 檔案格式要求：**

必須包含以下欄位（中文欄位名）：
- `學號`: 學生學號，格式如 A1110001
- `姓名`: 學生姓名
- `課程名稱`: 課程名稱
- `課程碼`: 課程代碼
- `學分數`: 課程學分數
- `成績`: 課程成績（數字）
  - 999: 修課中
  - 555: 抵免
  - 60-100: 及格
  - 0-59: 不及格
- `承抵課程別`: 承抵類別
- `選必修`: 課程類型（0或1為必修，2為選修）
- `學年`: 修課學年度
- `學期`: 修課學期

**回應範例：**
```json
{
  "success": true,
  "message": "成功從 Excel 檔案匯入 3 位學生資料",
  "data": [
    {
      "id": "A1110001",
      "name": "張三",
      "major": "E2"
    }
  ]
}
```

#### 4. 刪除特定學生
```
DELETE /students/{student_id}
```

**回應範例：**
```json
{
  "success": true,
  "message": "成功刪除學生 A1110001 的資料",
  "data": null
}
```

#### 5. 刪除所有學生
```
DELETE /students/
```

**回應範例：**
```json
{
  "success": true,
  "message": "成功刪除 3 位學生的資料",
  "data": null
}
```

## 錯誤處理

所有 API 在發生錯誤時會回傳相應的 HTTP 狀態碼和錯誤訊息：

```json
{
  "detail": "錯誤訊息說明"
}
```

常見錯誤碼：
- `400 Bad Request`: 請求參數錯誤
- `404 Not Found`: 資源不存在
- `413 Request Entity Too Large`: 檔案過大（限制 10MB）
- `500 Internal Server Error`: 伺服器內部錯誤

## 資料存儲

學生資料以 JSON 格式存儲在 `backend/data/students/` 目錄下，每個學生一個檔案，檔名為學號（例如：`A1110001.json`）。
