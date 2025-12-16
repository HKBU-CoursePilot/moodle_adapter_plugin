"""
Stub adapter for Moodle content access.

Loads fake course data from JSON fixtures for development and testing.
This allows development to proceed without access to the real Moodle API.
"""

import os
import sys
import json
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


class StubMoodleAdapter:
    """
    Stub implementation of IMoodlePort.
    
    Loads course data from JSON fixtures in data/stubs/<scenario>/.
    Useful for development and testing without real Moodle access.
    """
    
    def __init__(self, scenario: str = "demo_course"):
        """
        Initialize stub adapter with a specific scenario.
        
        Args:
            scenario: Name of the stub scenario folder (e.g., "demo_course")
        """
        self.scenario = scenario
        self.logger = Logger(name="StubMoodleAdapter")
        self._data_path = Path(current_dir) / "data" / "stubs" / scenario
        
        if not self._data_path.exists():
            self.logger.warning(f"Stub scenario not found: {scenario}, using demo_course")
            self._data_path = Path(current_dir) / "data" / "stubs" / "demo_course"
        
        # Cache for loaded data
        self._course_info_cache: dict[str, CourseInfo] = {}
        self._course_content_cache: dict[str, CourseContent] = {}
        self._item_contents: dict[str, str] = {}
        
        self._load_stub_data()
    
    def _load_stub_data(self) -> None:
        """Load all stub data from JSON files."""
        self.logger.debug(f"Loading stub data from: {self._data_path}")
        
        # Load course info
        course_info_path = self._data_path / "course_info.json"
        if course_info_path.exists():
            with open(course_info_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                course_info = CourseInfo(
                    id=data["id"],
                    code=data["code"],
                    name=data["name"],
                    instructor=data["instructor"],
                    semester=data["semester"],
                )
                self._course_info_cache[course_info.id] = course_info
                self.logger.debug(f"Loaded course info: {course_info.id}")
        
        # Load course content
        course_content_path = self._data_path / "course_content.json"
        if course_content_path.exists():
            with open(course_content_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                course_content = self._parse_course_content(data)
                self._course_content_cache[course_content.course_id] = course_content
                self.logger.debug(f"Loaded course content: {course_content.course_id}")
        
        # Load item contents
        item_contents_path = self._data_path / "item_contents"
        if item_contents_path.exists():
            for txt_file in item_contents_path.glob("*.txt"):
                item_id = txt_file.stem
                with open(txt_file, "r", encoding="utf-8") as f:
                    self._item_contents[item_id] = f.read()
            self.logger.debug(f"Loaded {len(self._item_contents)} item contents")
    
    def _parse_datetime(self, value: str | None) -> datetime | None:
        """Parse ISO 8601 datetime string."""
        if not value:
            return None
        try:
            # Handle both with and without timezone
            if value.endswith("Z"):
                value = value[:-1] + "+00:00"
            return datetime.fromisoformat(value)
        except ValueError:
            self.logger.warning(f"Invalid datetime format: {value}")
            return None
    
    def _parse_content_item(self, data: dict) -> ContentItem:
        """Parse a ContentItem from JSON data."""
        return ContentItem(
            id=data["id"],
            name=data["name"],
            item_type=data["item_type"],
            url=data.get("url"),
            content=data.get("content"),
            file_type=data.get("file_type"),
            due_date=self._parse_datetime(data.get("due_date")),
            metadata=data.get("metadata", {}),
            is_visible=data.get("is_visible", True),
            available_from=self._parse_datetime(data.get("available_from")),
            available_until=self._parse_datetime(data.get("available_until")),
        )
    
    def _parse_section(self, data: dict) -> Section:
        """Parse a Section from JSON data (recursively handles subsections)."""
        items = [self._parse_content_item(item) for item in data.get("items", [])]
        subsections = [self._parse_section(sub) for sub in data.get("subsections", [])]
        
        return Section(
            id=data["id"],
            name=data["name"],
            summary=data.get("summary", ""),
            position=data["position"],
            depth=data.get("depth", 0),
            parent_id=data.get("parent_id"),
            items=items,
            subsections=subsections,
            is_visible=data.get("is_visible", True),
            available_from=self._parse_datetime(data.get("available_from")),
            available_until=self._parse_datetime(data.get("available_until")),
        )
    
    def _parse_course_content(self, data: dict) -> CourseContent:
        """Parse CourseContent from JSON data."""
        sections = [self._parse_section(sec) for sec in data.get("sections", [])]
        return CourseContent(
            course_id=data["course_id"],
            sections=sections,
        )
    
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
        if item_id not in self._item_contents:
            raise ItemNotFoundError(item_id)
        return self._item_contents[item_id]
    
    async def search(self, query: str, course_id: str) -> list[SearchResult]:
        """
        Search within a specific course's materials.
        
        Simple text-based search for stub implementation.
        Real implementation would use Moodle's search API.
        """
        if course_id not in self._course_content_cache:
            raise CourseNotFoundError(course_id)
        
        results: list[SearchResult] = []
        course_content = self._course_content_cache[course_id]
        query_lower = query.lower()
        
        def search_in_section(section: Section) -> None:
            """Recursively search items in a section."""
            for item in section.items:
                # Search in item name
                if query_lower in item.name.lower():
                    snippet = self._create_snippet(item.name, query)
                    results.append(SearchResult(
                        item=item,
                        section_name=section.name,
                        snippet=snippet,
                        relevance_score=0.8,
                    ))
                # Search in item content if available
                elif item.id in self._item_contents:
                    content = self._item_contents[item.id]
                    if query_lower in content.lower():
                        snippet = self._create_snippet(content, query)
                        results.append(SearchResult(
                            item=item,
                            section_name=section.name,
                            snippet=snippet,
                            relevance_score=0.6,
                        ))
            
            # Search subsections
            for subsection in section.subsections:
                search_in_section(subsection)
        
        for section in course_content.sections:
            search_in_section(section)
        
        # Sort by relevance score
        results.sort(key=lambda r: r.relevance_score, reverse=True)
        return results
    
    def _create_snippet(self, text: str, query: str, context_chars: int = 50) -> str:
        """Create a snippet with the query highlighted in context."""
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
