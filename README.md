# Moodle Adapter Plugin

## Overview

Unified interface to Moodle course content using the **Ports and Adapters (Hexagonal Architecture)** pattern. This plugin abstracts all Moodle API interactions, allowing development to proceed with fake data while the real Moodle API is unavailable.

**Key Design Decisions:**
- Course is always known (student pre-selects before any interaction)
- Unified `ContentItem` model (no activity/resource distinction)
- Sections as opaque containers (no semantic interpretation)
- Visibility fields for future-proofing (adapter passes through, doesn't filter)
- Async interface for I/O-bound real API operations

## Features

- **StubAdapter**: Loads fake data from JSON fixtures (development/testing)
- **FileAdapter**: Reads from local markdown/files (offline development)
- **RealAdapter**: Connects to Moodle API (placeholder for future)
- Config-driven adapter switching
- Comprehensive domain models with visibility/availability fields
- Search functionality within course materials

## Usage

```python
import asyncio
from plugins.moodle_adapter_plugin import get_adapter

async def main():
    adapter = get_adapter()  # Uses config to determine adapter
    
    # Fetch course info
    course = await adapter.get_course_info("COMP1001-2024")
    print(f"Course: {course.name} by {course.instructor}")
    
    # Get course content structure
    content = await adapter.get_course_content("COMP1001-2024")
    for section in content.sections:
        print(f"Section: {section.name}")
        for item in section.items:
            print(f"  - {item.name} ({item.item_type})")
    
    # Search within course
    results = await adapter.search("functions", "COMP1001-2024")
    for result in results:
        print(f"Found: {result.item.name} in {result.section_name}")

asyncio.run(main())
```

## Module Structure

```
moodle_adapter_plugin/
├── __init__.py              # Entry point and exports
├── moodle_adapter_plugin.py # Factory function and singleton
├── models.py                # Domain models (CourseInfo, ContentItem, etc.)
├── moodle_port.py           # IMoodlePort protocol interface
├── exceptions.py            # Custom exceptions (inherit ADHDError)
├── stub_adapter.py          # Stub implementation (JSON fixtures)
├── file_adapter.py          # File-based implementation
├── real_adapter.py          # Real Moodle API (placeholder)
├── init.yaml                # Module metadata and dependencies
├── .config_template         # Default configuration
├── refresh.py               # Framework refresh logic
├── requirements.txt         # PyPI dependencies
├── moodle_adapter_plugin.instructions.md  # AI context
└── data/
    └── stubs/
        ├── demo_course/     # Full course with sections/items
        │   ├── course_info.json
        │   ├── course_content.json
        │   └── item_contents/
        └── empty_course/    # Edge case testing
```

## Configuration

```json
{
    "moodle_adapter_plugin": {
        "adapter_mode": "stub",
        "stub": { "scenario": "demo_course" },
        "file": { "courses_path": "project/data/courses" },
        "real": { "api_base_url": "", "api_token": "", "timeout": 30 }
    }
}
```