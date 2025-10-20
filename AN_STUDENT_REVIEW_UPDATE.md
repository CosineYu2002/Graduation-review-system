# 不分系學生審查邏輯修改說明

## 變更概述

修改了不分系 (AN) 學生的畢業審查邏輯：
- **舊版本**：不分系學生必須指定主修科系
- **新版本**：不分系學生必須至少提供一個輔系，主修科系為可選

## 修改的檔案

### 前端 (Frontend)

#### 1. `src/pages/StudentsPage.vue`

**審查對話框 UI 變更**
- 移除不分系學生必須填寫主修的強制提示
- 將主修欄位改為可選（disabled 狀態移除）
- 新增輔系必填提示（橙色 banner）
- 輔系欄位標題加上 `*` 表示必填（僅不分系學生）
- 不分系學生開啟對話框時預設添加一個輔系欄位

**驗證邏輯變更**
```javascript
// 舊版本
if (reviewStudent.value.major === 'AN' && !reviewMajor.value) {
  reviewError.value = '不分系學生必須選擇主修科系'
  return
}

// 新版本
if (reviewStudent.value.major === 'AN') {
  const validMinors = reviewMinors.value.filter((m) => m.trim())
  if (validMinors.length === 0) {
    reviewError.value = '不分系學生必須至少選擇一個輔系'
    return
  }
}
```

**參數構建變更**
```javascript
// 舊版本：不分系學生強制發送 major
if (reviewStudent.value.major === 'AN' || 
    (reviewMajor.value && reviewMajor.value !== reviewStudent.value.major)) {
  params.major = reviewMajor.value
}

// 新版本：只有當真的填寫了主修且不同於原科系時才發送
if (reviewMajor.value && reviewMajor.value !== reviewStudent.value.major) {
  params.major = reviewMajor.value
}
```

### 後端 (Backend)

#### 1. `api/crud/review_crud.py`

**驗證邏輯變更**
```python
# 舊版本
if review_dept == "AN":
    if not minor_departments:
        raise ValueError(
            "不分系學生 (AN) 必須提供 'minor_departments' 參數以進行審查"
        )

# 新版本
if review_dept == "AN":
    if not minor_departments or len(minor_departments) == 0:
        raise ValueError(
            "不分系學生 (AN) 必須提供至少一個輔系 (minor_departments) 以進行審查"
        )
```

#### 2. `api/routers/review_router.py`

**API 文檔更新**
```python
# 參數描述
major: str | None = Query(
    None, 
    description="主修科系代號（若不指定則使用學生本身科系）"  # 移除「不分系學生必填」
)

minor: list[str] | None = Query(
    None, 
    description="輔系科系代號列表（不分系學生必須至少提供一個）"  # 新增必填說明
)

# 使用範例
"""
- 不分系學生（至少一個輔系）: POST /review/A10999999?minor=B5
- 不分系學生含主修和輔系: POST /review/A10999999?major=CS&minor=B5
"""
```

#### 3. `README_REVIEW_API.md`

更新了以下內容：
- 查詢參數說明
- 使用範例
- 審查邏輯說明
- 錯誤處理說明

## UI/UX 變更

### 審查對話框（不分系學生）

#### 舊版本
```
┌─────────────────────────────────┐
│ 畢業審查                         │
├─────────────────────────────────┤
│ 學生資訊                         │
│   學號：B54106150               │
│   姓名：許毓芸                   │
│   主修科系：AN                   │
├─────────────────────────────────┤
│ ⚠️ 不分系學生必須選擇主修科系    │
│ 主修科系代號 * [B5_____]        │ ← 必填
├─────────────────────────────────┤
│ 輔系科系代號（可選）             │ ← 可選
│ [+ 新增輔系]                     │
└─────────────────────────────────┘
```

#### 新版本
```
┌─────────────────────────────────┐
│ 畢業審查                         │
├─────────────────────────────────┤
│ 學生資訊                         │
│   學號：B54106150               │
│   姓名：許毓芸                   │
│   主修科系：AN                   │
├─────────────────────────────────┤
│ ⓘ 不分系學生必須至少選擇一個輔系 │ ← 新增提示
├─────────────────────────────────┤
│ 主修科系代號（可選）             │ ← 可選
│ [B5___________]                 │
├─────────────────────────────────┤
│ 輔系科系代號 *                   │ ← 必填標記
│ [H5___________] [-]             │ ← 預設已添加
│ [+ 新增輔系]                     │
└─────────────────────────────────┘
```

## API 使用範例對比

### 舊版本
```bash
# 不分系學生（必須有 major）
POST /api/review/B54106150?major=B5

# 不分系學生含輔系
POST /api/review/B54106150?major=B5&minor=H5
```

### 新版本
```bash
# 不分系學生（只需 minor）
POST /api/review/B54106150?minor=B5

# 不分系學生含主修和輔系
POST /api/review/B54106150?major=CS&minor=B5

# 不分系學生含多個輔系
POST /api/review/B54106150?minor=B5&minor=H5
```

## 業務邏輯說明

### 為什麼要這樣修改？

1. **更符合實際情況**
   - 不分系學生可能沒有明確的主修
   - 但通常會有輔系（專長領域）
   - 輔系更能代表學生的學習方向

2. **靈活性提升**
   - 允許不分系學生只填輔系
   - 也允許同時填主修和輔系
   - 給予更多選擇空間

3. **審查邏輯不變**
   - 後端仍使用第一個輔系來調整規則
   - 審查結果計算邏輯保持一致
   - 只是參數要求改變

## 驗證測試

### 測試案例

#### 案例 1: 不分系學生只填輔系
```javascript
// 前端
reviewStudent.major = 'AN'
reviewMajor = ''
reviewMinors = ['B5']

// API 請求
POST /api/review/AN4116089?minor=B5

// 預期結果：✅ 審查成功
```

#### 案例 2: 不分系學生填主修和輔系
```javascript
// 前端
reviewStudent.major = 'AN'
reviewMajor = 'CS'
reviewMinors = ['B5']

// API 請求
POST /api/review/AN4116089?major=CS&minor=B5

// 預期結果：✅ 審查成功
```

#### 案例 3: 不分系學生未填輔系（錯誤）
```javascript
// 前端
reviewStudent.major = 'AN'
reviewMajor = 'CS'
reviewMinors = []

// 預期結果：❌ 前端驗證失敗
// 錯誤訊息：「不分系學生必須至少選擇一個輔系」
```

#### 案例 4: 一般學生（不受影響）
```javascript
// 前端
reviewStudent.major = 'E2'
reviewMajor = 'E2'
reviewMinors = []

// API 請求
POST /api/review/E24105088

// 預期結果：✅ 審查成功（行為不變）
```

## 向後兼容性

### 舊 API 調用方式仍然有效
```bash
# 舊方式（仍然可用）
POST /api/review/B54106150?major=B5&minor=H5

# 新方式（更簡潔）
POST /api/review/B54106150?minor=H5
```

### 前端舊版本
如果前端沒有更新，仍然強制填寫主修的話：
- ✅ API 仍然可以正常運作
- ✅ 審查邏輯正常執行
- ⚠️ 但用戶體驗不是最佳（要求填不必要的主修）

## 部署注意事項

1. **前後端需同步部署**
   - 建議同時更新前端和後端
   - 確保驗證邏輯一致

2. **用戶通知**
   - 通知行政人員新的審查流程
   - 強調不分系學生現在只需填輔系即可

3. **文檔更新**
   - ✅ API 文檔已更新
   - ✅ 使用說明已更新
   - ✅ 錯誤訊息已更新

## 總結

這次修改讓不分系學生的審查流程更加靈活和符合實際需求：
- ✅ 移除了主修的強制要求
- ✅ 改為要求至少一個輔系
- ✅ 主修變為可選項
- ✅ 保持向後兼容性
- ✅ 前後端邏輯一致
- ✅ 文檔完整更新
