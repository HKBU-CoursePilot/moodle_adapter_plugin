"""
File-based adapter for Moodle content access.

Reads course data from local files for offline development.
Supports markdown and plain text files organized by course/week.
"""

import os
import sys
import yaml
from datetime import datetime
from pathlib import Path

current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.getcwd()
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from utils.logger_util import Logger

from plugins.moodle_adapter_plugin.models import (
    CourseInfo,
    ContentItem,
    Section,
    CourseContent,
    SearchResult,
)
from plugins.moodle_adapter_plugin.exceptions import (
    CourseNotFoundError,
    ItemNotFoundError,
)


class FileMoodleAdapter:
    """
    File-based implementation of IMoodlePort.
    
    Reads course data from local files for offline development.
    
    Directory structure:
        courses_path/
        ├── COMP1001/
        │   ├── _meta.yaml           # Course metadata
        │   ├── week01/
        │   │   ├── _section.yaml    # Section metadata  
        │   │   ├── lecture_slides.pdf
        │   │   ├── lecture_slides.txt  # Pre-extracted text
        │   │   └── lab_instructions.md
        │   └── week02/
        │       └── ...
        └── COMP2001/
            └── ...
    """
    
    def __init__(self, courses_path: str):
        """
        Initialize file adapter with path to course files.
        
        Args:
            courses_path: Path to the directory containing course folders
        """
        self.courses_path = Path(courses_path)
        self.logger = Logger(name="FileMoodleAdapter")
        
        # Cache for loaded data
        self._course_info_cache: dict[str, CourseInfo] = {}
        self._course_content_cache: dict[str, CourseContent] = {}
        self._item_registry: dict[str, tuple[str, Path]] = {}  # item_id -> (course_id, file_path)
        
        self._scan_courses()
    
    def _scan_courses(self) -> None:
        """Scan course directories and build cache."""
        if not self.courses_path.exists():
            self.logger.warning(f"Courses path not found: {self.courses_path}")
            return
        
        for course_dir in self.courses_path.iterdir():
            if not course_dir.is_dir() or course_dir.name.startswith("_"):
                continue
            
            self._load_course(course_dir)
    
    def _load_course(self, course_dir: Path) -> None:
        """Load a single course from directory."""
        meta_path = course_dir / "_meta.yaml"
        if not meta_path.exists():
            self.logger.warning(f"Missing _meta.yaml in {course_dir}")
            return
        
        with open(meta_path, "r", encoding="utf-8") as f:
            meta = yaml.safe_load(f)
        
        course_info = CourseInfo(
            id=meta.get("id", course_dir.name),
            code=meta.get("code", course_dir.name),
            name=meta.get("name", course_dir.name),
            instructor=meta.get("instructor", "Unknown"),
            semester=meta.get("semester", "Unknown"),
        )
        self._course_info_cache[course_info.id] = course_info
        
        # Load sections
        sections: list[Section] = []
        item_counter = 0
        
        for section_dir in sorted(course_dir.iterdir()):
            if not section_dir.is_dir() or section_dir.name.startswith("_"):
                continue
            
            section, item_count = self._load_section(
                section_dir, 
                course_info.id, 
                len(sections),
                item_counter
            )
            sections.append(section)
            item_counter += item_count
        
        self._course_content_cache[course_info.id] = CourseContent(
            course_id=course_info.id,
            sections=sections,
        )
        
        self.logger.debug(f"Loaded course: {course_info.id} with {len(sections)} sections")
    
    def _load_section(
        self, 
        section_dir: Path, 
        course_id: str, 
        position: int,
        item_start: int
    ) -> tuple[Section, int]:
        """Load a section from directory. Returns (section, item_count)."""
        section_meta_path = section_dir / "_section.yaml"
        
        if section_meta_path.exists():
            with open(section_meta_path, "r", encoding="utf-8") as f:
                section_meta = yaml.safe_load(f) or {}
        else:
            section_meta = {}
        
        section_id = section_meta.get("id", f"section_{section_dir.name}")
        section_name = section_meta.get("name", section_dir.name.replace("_", " ").title())
        
        # Load items (files in this directory)
        items: list[ContentItem] = []
        item_counter = item_start
        
        for file_path in sorted(section_dir.iterdir()):
            if file_path.is_dir() or file_path.name.startswith("_"):
                continue
            if file_path.suffix in [".yaml", ".yml"]:
                continue
            
            item = self._file_to_content_item(file_path, item_counter)
            if item:
                items.append(item)
                self._item_registry[item.id] = (course_id, file_path)
                item_counter += 1
        
        section = Section(
            id=section_id,
            name=section_name,
            summary=section_meta.get("summary", ""),
            position=position,
            depth=0,
            parent_id=None,
            items=items,
            subsections=[],  # File adapter doesn't support subsections yet
            is_visible=section_meta.get("is_visible", True),
            available_from=self._parse_datetime(section_meta.get("available_from")),
            available_until=self._parse_datetime(section_meta.get("available_until")),
        )
        
        return section, item_counter - item_start
    
    def _file_to_content_item(self, file_path: Path, counter: int) -> ContentItem | None:
        """Convert a file to a ContentItem."""
        suffix = file_path.suffix.lower()
        name = file_path.stem.replace("_", " ").title()
        
        # Determine item type based on extension
        type_mapping = {
            ".pdf": ("file", "pdf"),
            ".docx": ("file", "docx"),
            ".pptx": ("file", "pptx"),
            ".txt": ("page", None),
            ".md": ("page", None),
            ".html": ("page", None),
        }
        
        if suffix not in type_mapping:
            return None
        
        item_type, file_type = type_mapping[suffix]
        
        return ContentItem(
            id=f"file_item_{counter}",
            name=name,
            item_type=item_type,
            file_type=file_type,
            is_visible=True,
        )
    
    def _parse_datetime(self, value: str | None) -> datetime | None:
        """Parse ISO 8601 datetime string."""
        if not value:
            return None
        try:
            if isinstance(value, datetime):
                return value
            if value.endswith("Z"):
                value = value[:-1] + "+00:00"
            return datetime.fromisoformat(value)
        except ValueError:
            self.logger.warning(f"Invalid datetime format: {value}")
            return None
    
    async def get_course_info(self, course_id: str) -> CourseInfo:
        """Get course metadata."""
        if course_id not in self._course_info_cache:
            raise CourseNotFoundError(course_id)
        return self._course_info_cache[course_id]
    
    async def get_course_content(self, course_id: str) -> CourseContent:
        """Get the full structured content of a course."""
        if course_id not in self._course_content_cache:
            raise CourseNotFoundError(course_id)
        return self._course_content_cache[course_id]
    
    async def get_item_content(self, item_id: str) -> str:
        """Get the extracted text content of a content item."""
        if item_id not in self._item_registry:
            raise ItemNotFoundError(item_id)
        
        _, file_path = self._item_registry[item_id]
        
        # For text-based files, read directly
        if file_path.suffix.lower() in [".txt", ".md", ".html"]:
            with open(file_path, "r", encoding="utf-8") as f:
                return f.read()
        
        # For other files, look for companion .txt file
        txt_path = file_path.with_suffix(".txt")
        if txt_path.exists():
            with open(txt_path, "r", encoding="utf-8") as f:
                return f.read()
        
        # No content available
        return ""
    
    async def search(self, query: str, course_id: str) -> list[SearchResult]:
        """Search within a specific course's materials."""
        if course_id not in self._course_content_cache:
            raise CourseNotFoundError(course_id)
        
        results: list[SearchResult] = []
        course_content = self._course_content_cache[course_id]
        query_lower = query.lower()
        
        for section in course_content.sections:
            for item in section.items:
                # Search in item name
                if query_lower in item.name.lower():
                    results.append(SearchResult(
                        item=item,
                        section_name=section.name,
                        snippet=item.name,
                        relevance_score=0.8,
                    ))
                    continue
                
                # Search in item content
                if item.id in self._item_registry:
                    try:
                        content = await self.get_item_content(item.id)
                        if query_lower in content.lower():
                            snippet = self._create_snippet(content, query)
                            results.append(SearchResult(
                                item=item,
                                section_name=section.name,
                                snippet=snippet,
                                relevance_score=0.6,
                            ))
                    except ItemNotFoundError:
                        pass
        
        results.sort(key=lambda r: r.relevance_score, reverse=True)
        return results
    
    def _create_snippet(self, text: str, query: str, context_chars: int = 50) -> str:
        """Create a snippet with the query in context."""
        query_lower = query.lower()
        text_lower = text.lower()
        
        idx = text_lower.find(query_lower)
        if idx == -1:
            return text[:100] + "..." if len(text) > 100 else text
        
        start = max(0, idx - context_chars)
        end = min(len(text), idx + len(query) + context_chars)
        
        snippet = text[start:end]
        if start > 0:
            snippet = "..." + snippet
        if end < len(text):
            snippet = snippet + "..."
        
        return snippet
