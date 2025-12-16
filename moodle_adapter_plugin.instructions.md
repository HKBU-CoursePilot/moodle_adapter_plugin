---
applyTo: "plugins/moodle_adapter_plugin/**/*.py"
---

# Moodle Adapter Plugin Instructions

## Purpose

The `moodle_adapter_plugin` provides a unified interface to Moodle course content using the **Ports and Adapters (Hexagonal Architecture)** pattern. This allows development to proceed with fake data while the real Moodle API is unavailable.

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Application Core                         │
│                         │                                   │
│                         ▼                                   │
│               IMoodlePort (Protocol)                        │
└─────────────────────────┼───────────────────────────────────┘
                          │
         ┌────────────────┼────────────────┐
         │                │                │
         ▼                ▼                ▼
   ┌──────────┐    ┌──────────┐    ┌──────────┐
   │  Stub    │    │  File    │    │  Real    │
   │ Adapter  │    │ Adapter  │    │ Adapter  │
   └──────────┘    └──────────┘    └──────────┘
         │                │                │
         ▼                ▼                ▼
   [JSON Fixtures]  [Local Files]  [Moodle API]
```

## Key Design Decisions

### 1. Course is Always Known
The student **always selects a course first** before any interaction. Therefore:
- `course_id` is required for all content queries
- No `get_courses()` method needed

### 2. Unified ContentItem Model
Moodle distinguishes between "activities" and "resources". We unify them:
- Single `ContentItem` dataclass
- `item_type` field discriminates (file, url, page, assignment, etc.)

### 3. Sections as Opaque Containers
Sections have no inherent semantic meaning (weekly vs topic vs general):
- We do NOT interpret section semantics
- Adapter passes through structure unchanged
- Pedagogical Engine decides interpretation

### 4. Visibility Future-Proofing
Fields `is_visible`, `available_from`, `available_until` exist for future-proofing:
- Unknown if Moodle API filters server-side or returns visibility flags
- Adapter passes through visibility data (does NOT filter)
- Pedagogical Engine decides what to show

### 5. Async Interface
All interface methods are `async def`:
- Real Moodle API will be I/O-bound
- Stub/File adapters work sync internally but expose async interface

## Usage

### Basic Usage

```python
from plugins.moodle_adapter_plugin import get_adapter

# Get adapter based on config (stub by default)
adapter = get_adapter()

# All methods are async
course_info = await adapter.get_course_info("COMP1001-2024")
course_content = await adapter.get_course_content("COMP1001-2024")
item_text = await adapter.get_item_content("item_001")
results = await adapter.search("functions", "COMP1001-2024")
```

### Force Specific Adapter

```python
# Override config for testing
adapter = get_adapter(force_mode="stub")
```

### Direct Adapter Instantiation

```python
from plugins.moodle_adapter_plugin import StubMoodleAdapter

adapter = StubMoodleAdapter(scenario="demo_course")
```

## Configuration

In `.config` file:

```json
{
    "module_name": "moodle_adapter_plugin",
    "adapter_mode": "stub",
    "stub": {
        "scenario": "demo_course"
    },
    "file": {
        "courses_path": "project/data/courses"
    },
    "real": {
        "api_base_url": "",
        "api_token": "${MOODLE_API_TOKEN}",
        "timeout": 30,
        "cache_ttl": 3600
    }
}
```

## Exception Handling

All exceptions inherit from `ADHDError`:

```python
from plugins.moodle_adapter_plugin import (
    CourseNotFoundError,
    ItemNotFoundError,
    MoodleUnavailableError,
)

try:
    content = await adapter.get_course_content("INVALID")
except CourseNotFoundError as e:
    print(f"Course not found: {e.course_id}")
```

## Stub Data Structure

```
data/stubs/<scenario>/
├── course_info.json      # CourseInfo metadata
├── course_content.json   # Full section/item structure
└── item_contents/        # Extracted text by item_id
    ├── item_001.txt
    ├── item_002.txt
    └── ...
```

## Adding New Stub Scenarios

1. Create directory: `data/stubs/<scenario_name>/`
2. Add `course_info.json` with course metadata
3. Add `course_content.json` with section structure
4. Add `item_contents/` with extracted text files
5. Configure in `.config`: `stub.scenario: "<scenario_name>"`

## Anti-Patterns to Avoid

- **DON'T** interpret section semantics in the adapter
- **DON'T** filter visibility in the adapter (let higher layers decide)
- **DON'T** use `print()` — use `Logger`
- **DON'T** hardcode paths — use config
