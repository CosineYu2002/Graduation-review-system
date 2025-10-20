# 規則嵌套渲染修復說明

## 問題描述

原先的 `RenderRule` 組件使用了錯誤的自我引用方式（`components: { RenderRule: this }`），導致無法正確渲染嵌套的子規則。

## 修復方案

### 1. 使用 Vue 3 的 `defineComponent` 和 `h` 函數

- 將組件定義從字符串模板改為使用渲染函數（render function）
- 使用 `h()` 函數手動創建虛擬 DOM
- 這樣可以正確地實現遞迴組件

### 2. 導入必要的依賴

```javascript
import { h, defineComponent } from 'vue'
import { QIcon, QBadge, QCard, QCardSection, QExpansionItem, QChip } from 'quasar'
```

### 3. 遞迴渲染實現

在子規則部分，使用以下代碼實現遞迴：

```javascript
h(RenderRule, { rule: subRule, level: props.level + 1 })
```

組件內部可以直接引用自己（`RenderRule`），從而實現真正的嵌套渲染。

## 功能特點

### 支持多層嵌套

- ✅ 第一層規則（主規則）
- ✅ 第二層規則（子規則）
- ✅ 第三層規則（子規則的子規則）
- ✅ 更深層次的規則...

### 視覺層次區分

- 使用 `level` prop 追蹤嵌套深度
- 不同層級使用不同的背景色：`bg-blue-2`, `bg-blue-3` 等
- 每一層都可以獨立展開/摺疊

### 完整支持的規則類型

- **RuleSet**: 顯示子規則列表和邏輯運算（AND/OR）
- **RuleAll**: 顯示課程篩選條件和課程列表

## 測試方式

1. 打開規則詳情頁面
2. 選擇一個包含子規則的規則（rule_type 為 "rule_set"）
3. 展開子規則查看內容
4. 如果子規則也是 RuleSet 類型，繼續展開其子規則
5. 驗證所有層級都能正確顯示

## 範例結構

```
主規則 (RuleSet)
├─ 子規則 1 (RuleSet)
│  ├─ 子子規則 1.1 (RuleAll) ← 可以正確顯示
│  └─ 子子規則 1.2 (RuleAll) ← 可以正確顯示
└─ 子規則 2 (RuleAll)
```

現在每一層都能正確渲染，不再只顯示最上層的規則！
