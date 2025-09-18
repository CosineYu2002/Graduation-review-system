# 畢業審查系統 (Graduation review system)
這是一個基於 Python 和 Pydantic 的畢業審查系統，能夠自由的添加畢業規則還有學生的修課記錄來判斷是否符合畢業要求。
## 功能特色
- **智能規則匹配**： 根據學生的主修科系還有入學年度自動匹配使用的畢業規則
- **靈活的規則定義**： 支援復雜的畢業條件設定，包括必修，選修，黑名單，白名單等等
- **多種數據來源**： 支援從 Excel 或是 JSON 載入學生資料
- **詳細審查報告**： 提供完整的畢業條件檢查結果還有學分統計
- **交互式 CLI 界面**： 有好的命令行操作界面
- **可擴展架構**： 基於註冊工廠模式的可擴展設計
## 技術棧
- Python 3.12+
- Pydantic v2 數據驗證及序列化
- Type Hints 完整的型別提示
- Factory Pattern 可擴展的設計模式
## 安裝
1. clone
   ```
   git clone https://github.com/CosineYu2002/Graduation-review-system.git
    cd graduation-review-system
    ```
2. 安裝必要套件
   ```
   pip install -r requirements.txt
   ```
3. 準備數據目錄
   ```
   mkdir -p students data rules
## 使用說明
### CLI 操作流程
1. 載入學生資料
   - 選擇選項1：從 EXCEL 載入
   - 選擇選項2：載入已存在的 JSON 資料
2. 查看學生列表
   - 選擇選項3：顯示已載入的學生
3. 執行畢業審查
   - 選擇選項4：選擇學生進行審查
   - 系統會自動選擇適合的規則，如果是不分系的同學則需要自行選擇主修系的輔系規則
   - 顯示詳細的結果
### 規則類型
#### RuleSet （規則集）
- 包含多個字規則
- 支援 AND / OR 邏輯組合
- 適用於復雜的畢業條件
#### RuleALL （單一規則）
- 針對特定課程或條件的檢查
- 支援學分、課程數量等要求
- 可設定課程篩選條件
#### CourseCriteria （課程條件）
- 課程名稱或是代碼匹配
- 系所代碼限制
- 課程類型限制
- 黑名單、白名單
- 成績要求
- 等等
## 開發指南
添加新的規則類型（不建議，希望能在現有的規則下進行修改，實在不想再添加新的規則類型）
1. 定義規則模型
   ```python
   class CustomRule(BaseRule):
       rule_type: Literal["custom_rule"]
       custom_field: str
   ```
2. 實現評估器
    ```python
    @register_evaluator("custom_rule")
    class CustomRuleEvaluator:
        def evaluate(self, rule, student_courses): ...
            # 實現評估器
    ```
3. 定義結果模型
   ```python
   class CustomResult(BaseEvaluationResult):
       rule_type: Literal["custom_rule"]
   ```
## 文件結構說明
### 規則文件命名規範
- `rules/{系所代碼}/{年度}.json`：標準畢業規則
- `rules/{系所代碼}/{年度}_minor.json`：輔系規則
- 系統只會自動匹配純數字年度文件
### 學生資料格式
- Excel： 標準化列名格式
- JSON： Pydantic 模型格式
