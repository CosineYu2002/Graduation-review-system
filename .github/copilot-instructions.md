# NCKU 畢業審查系統 - AI Coding Agent Instructions

## Project Overview
This is a graduation credit validation system for NCKU (National Cheng Kung University) that evaluates student course completion against department-specific graduation rules. The system consists of a Python FastAPI backend with a rule engine, and a Vue 3/Quasar frontend.

**Primary Language**: Traditional Chinese (繁體中文) - all comments, documentation, and UI strings should use Traditional Chinese.

## Architecture

### Backend Structure (`/backend`)
- **Rule Engine** (`rule_engine/`): Core evaluation logic using Pydantic models
  - `models/`: Type-safe models for students, courses, rules, and results
  - `evaluator.py`: Evaluator registry pattern with decorators (`@register_evaluator`)
  - `factory.py`: Factory classes for creating domain objects from JSON/Excel/dict
  - `utils.py`: Course matching logic based on criteria

- **API Layer** (`api/`): FastAPI REST endpoints
  - `main.py`: FastAPI app with router includes
  - `routers/students.py`: Student CRUD operations and Excel upload
  - `crud/`: Data access logic for students
  - `models/`: API request/response models (separate from domain models)

- **Data Layer** (`data/`):
  - `rules/<dept_code>/<year>.json`: Department-specific graduation rules by admission year
  - `departments_info.json`: Department metadata (codes, names, colleges)
  - `students/`: JSON files for persisted student data

- **Additional Components**:
  - `crawler/`: Web scraping for NCKU course data
  - `rule_updater/`: Interactive CLI tool for generating new rule files
  - `cli.py`: Full-featured CLI for student data management and evaluation

### Frontend Structure (`/frontend`)
- **Framework**: Vue 3 + Quasar Framework (Material Design)
- **State**: Pinia stores
- **Routing**: Vue Router with lazy-loaded pages

## Critical Concepts

### 1. Rule Engine Pattern
The system uses a **registry-based evaluator pattern**:
```python
# In evaluator.py
evaluator_registry = EvaluatorRegistry()

@register_evaluator("rule_all")
class RuleAllEvaluator:
    def evaluate(self, rule: RuleAll, student_courses) -> Result:
        # Evaluation logic
```

- Each rule type (`rule_all`, `rule_set`) has a corresponding evaluator
- Rules are hierarchical: `RuleSet` contains `sub_rules` with AND/OR logic
- Use `evaluator_registry.create_evaluator(rule_type)` to instantiate evaluators

### 2. Course Recognition System
Student courses have a `recognized` flag that prevents double-counting:
```python
class StudentCourse:
    recognized: bool = False  # Marks if already counted in evaluation
```
- Evaluators must set `course.recognized = True` after matching
- Sorting by `(course_name, year_taken, semester_taken, grade)` ensures consistent ordering
- Special handling for failed courses with external substitutes (see `allow_external_substitute_after_fail`)

### 3. Grade Status Codes
Use `UtilFunctions.get_status(grade)` for human-readable status:
- `999`: 修課中 (In progress)
- `555`: 抵免 (Transfer credit)
- `60-100`: 及格 (Pass)
- `0-59`: 不及格 (Fail)

### 4. Rule JSON Structure
Rules in `data/rules/<dept>/<year>.json` follow this schema:
```json
{
  "admission_year": 110,
  "department_code": "E2",
  "rules": [
    {
      "type": "list_selected",  // Maps to rule_type in Pydantic models
      "description": "選修表中課程至少x學分",
      "min_credits": 28,
      "course_list": [...]
    }
  ]
}
```

### 5. Student ID Pattern
Student IDs follow format: `^[A-Z][A-Z0-9][0-9]{7}$`
- Admission year extracted via `int(id[3:5]) + 100` (e.g., "A1110001" → year 111)

### 6. Department Code "AN" Special Case
`major: "AN"` = 不分系 (Undecided major)
- CLI prompts for 專長系 (specialization department) selection
- Frontend should handle similar logic for AN students

## Developer Workflows

### Backend Development
```bash
# Install dependencies
cd backend
pip install -r requirements.txt

# Run API server (development with hot reload)
python run.py --reload

# Run CLI tool
python cli.py

# Run tests
pytest tests/
```

### Frontend Development
```bash
cd frontend
npm install          # or yarn

# Development server
quasar dev           # NOT npm run dev

# Build for production
quasar build

# Linting/Formatting
npm run lint
npm run format
```

### Testing Rule Evaluation
1. Use `cli.py` for interactive testing:
   - Load students from Excel (`data/students/`)
   - System auto-selects rules based on `admission_year` and `major`
2. Add new rules via `rule_updater/generator.py` interactive mode

## Project-Specific Conventions

### Pydantic Usage
- **Type safety everywhere**: All data models use Pydantic with validation
- **TypeAdapter pattern** for polymorphic types:
  ```python
  adapter = TypeAdapter(Rule)  # Rule is a discriminated union
  rule = adapter.validate_json(json_str)
  ```
- **Field annotations** with `Annotated[Type, Field(...)]` for rich metadata

### Factory Pattern
- **Never instantiate models directly from raw data**
- Use factories: `StudentFactory.from_json_file()`, `RuleFactory.from_dict()`, `CourseFactory.from_excel_row()`
- Factories handle validation errors with contextual messages

### Error Handling
- Custom exceptions in `rule_engine/exception.py` and `crawler/exceptions.py`
- API returns `APIResponse[T]` wrapper with `success`, `message`, `data` fields
- Use HTTP 500 with detail messages for internal errors

### File Organization
- **Separate API models from domain models**: `api/models/` vs `rule_engine/models/`
- **Co-locate tests with code**: `tests/unit/rule_engine/` mirrors `rule_engine/`
- **JSON data is the source of truth**: No database, all rules/students in JSON files

### Naming Conventions
- **Python**: `snake_case` for functions/variables, `PascalCase` for classes
- **Vue**: `PascalCase` for component files, `camelCase` for props/methods
- **JSON fields**: Match Python model field names exactly (e.g., `course_name`, not `courseName`)

## Integration Points

### Frontend ↔ Backend API
- Base URL: `http://127.0.0.1:8000` (configured in `frontend/src/boot/axios.js`)
- Key endpoints:
  - `GET /students/` - List all students
  - `GET /students/{id}` - Student details with courses
  - `POST /students/upload-excel` - Upload student data from Excel
  - `POST /students/{id}/evaluate` - Run graduation evaluation

### Rule Loading
- Auto-select rule file: `data/rules/{dept_code}/{admission_year}.json`
- If missing, system prompts for manual selection or rule creation
- `RuleFactory.from_json_file()` handles parsing and validation

### Course Crawler
- Scrapes NCKU course catalog: `https://class-qry.acad.ncku.edu.tw/`
- Used by `rule_updater/generator.py` to populate course lists
- Returns course codes and credits for validation

## Key Files Reference
- `backend/cli.py` - Full CLI workflow example (547 lines)
- `backend/rule_engine/evaluator.py` - Evaluator registry and implementations
- `backend/rule_engine/models/rule.py` - Comprehensive rule model definitions
- `backend/api/routers/students.py` - REST API patterns
- `backend/data/rules/E2/110.json` - Example rule structure
- `frontend/src/pages/IndexPage.vue` - Currently minimal, needs implementation

## When Adding Features
1. **New rule type**: Create Pydantic model in `rule.py`, add evaluator with `@register_evaluator` decorator
2. **New API endpoint**: Add to appropriate router in `api/routers/`, define models in `api/models/`
3. **New course criteria**: Extend `CourseCriteria` model and update `UtilFunctions.match_criteria()`
4. **New department**: Add entry to `data/departments_info.json`, create `data/rules/<code>/` directory

## Common Pitfalls
- **Don't forget `course.recognized = True`** after matching in evaluators
- **Check `if not course.recognized`** before matching to avoid double-counting
- **Use `UtilFunctions.match_criteria()`** for all course filtering (don't reimplement)
- **Remember grade codes**: 999=in progress, 555=transfer credit
- **Auto-reload requires string path**: `uvicorn.run("api.main:app", reload=True)`, not `app` object
- **Quasar CLI commands**: Use `quasar dev/build`, not `npm run dev/build`
