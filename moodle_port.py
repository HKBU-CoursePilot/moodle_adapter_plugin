"""
Moodle Port interface definition.

This defines the abstract interface (Port) for Moodle content access.
All adapters must implement this interface.

Design Decisions:
- Async interface for future-proofing (real API will be I/O-bound)
- course_id is always required (student pre-selects course)
- Interface represents OUR requirements, not Moodle's capabilities
"""

import os
import sys

current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.getcwd()
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from typing import Protocol

from plugins.moodle_adapter_plugin.models import (
    CourseInfo,
    CourseContent,
    SearchResult,
)


class IMoodlePort(Protocol):
    """
    Abstract interface for Moodle content access.
    
    This defines OUR requirements, not Moodle's capabilities.
    Implementations must adapt Moodle's API to this interface.
    
    Key assumption: course_id is always known (student pre-selects course).
    """
    
    async def get_course_info(self, course_id: str) -> CourseInfo:
        """
        Get course metadata.
        
        Args:
            course_id: The course identifier (always required)
            
        Returns:
            Course metadata (code, name, instructor, semester)
            
        Raises:
            CourseNotFoundError: If course doesn't exist
        """
        ...
    
    async def get_course_content(self, course_id: str) -> CourseContent:
        """
        Get the full structured content of a course.
        
        Returns all sections (with subsections nested) and their content items.
        Does NOT include extracted text content for items - use get_item_content().
        
        Args:
            course_id: The course identifier (always required)
            
        Returns:
            Full course structure with sections and items
            
        Raises:
            CourseNotFoundError: If course doesn't exist
        """
        ...
    
    async def get_item_content(self, item_id: str) -> str:
        """
        Get the extracted text content of a content item.
        
        For files (PDF, DOCX, etc.): Returns extracted text
        For pages: Returns HTML content as text
        For URLs: Returns page title/description if available
        For assignments: Returns full description and rubric
        
        Args:
            item_id: The content item identifier
            
        Returns:
            Extracted text content (may be empty for some item types)
            
        Raises:
            ItemNotFoundError: If item doesn't exist
        """
        ...
    
    async def search(
        self, 
        query: str, 
        course_id: str  # REQUIRED - not optional
    ) -> list[SearchResult]:
        """
        Search within a specific course's materials.
        
        Args:
            query: Search query string
            course_id: The course to search within (REQUIRED)
            
        Returns:
            Ranked search results with snippets
            
        Raises:
            CourseNotFoundError: If course doesn't exist
        """
        ...
