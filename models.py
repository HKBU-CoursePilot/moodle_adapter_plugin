"""
Domain models for Moodle adapter.

All domain models are defined in this single file as the source of truth.
These models represent OUR view of course content, not Moodle's raw structures.

Design Philosophy:
- Sections are opaque containers (no semantic interpretation)
- ContentItem unifies activities and resources
- Visibility fields future-proof for unknown Moodle API behavior
"""

import os
import sys

current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.getcwd()
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from dataclasses import dataclass, field
from datetime import datetime
from typing import Literal


# Item type literals for ContentItem
ItemType = Literal[
    # P0 - MVP
    "file", "url", "page", "assignment",
    # P1 - Near-term
    "folder", "quiz", "forum",
    # P2 - Future
    "book", "panopto", "video",
    # Fallback
    "unknown"
]


@dataclass
class CourseInfo:
    """
    Basic course information.
    
    Represents metadata about a course without its content structure.
    """
    id: str
    code: str              # e.g., "COMP1001"
    name: str              # e.g., "Introduction to Programming"
    instructor: str
    semester: str          # e.g., "2024-25 Sem 1"


@dataclass
class ContentItem:
    """
    A unified content item (activity OR resource).
    
    This model intentionally unifies Moodle's activity/resource distinction
    into a single type with an item_type discriminator.
    
    Item Type Priority:
    - P0 (MVP): file, url, page, assignment
    - P1 (Near-term): folder, quiz, forum
    - P2 (Future): book, panopto, video
    - Fallback: unknown
    """
    id: str
    name: str
    item_type: ItemType
    url: str | None = None
    content: str | None = None      # Extracted text content
    file_type: str | None = None    # For file: "pdf", "docx", "pptx", etc.
    due_date: datetime | None = None  # For assignment, quiz
    metadata: dict = field(default_factory=dict)  # Flexible for unknown attributes
    
    # Visibility/Availability (future-proofing for unknown API behavior)
    is_visible: bool = True                      # False if teacher manually hid this item
    available_from: datetime | None = None       # Item not available before this datetime
    available_until: datetime | None = None      # Item not available after this datetime


@dataclass
class Section:
    """
    A section within a course (opaque container).
    
    Sections are purely structural - we do NOT interpret their semantic
    meaning (weekly vs topic vs general). Teachers use them differently.
    
    Supports one level of subsections (depth=0 for sections, depth=1 for subsections).
    """
    id: str
    name: str
    summary: str              # HTML description (may be empty)
    position: int             # Order: 0, 1, 2...
    depth: int                # 0 = section, 1 = subsection
    parent_id: str | None     # None for top-level sections
    items: list[ContentItem] = field(default_factory=list)
    subsections: list['Section'] = field(default_factory=list)  # Max depth = 1
    
    # Visibility/Availability (future-proofing for unknown API behavior)
    is_visible: bool = True                      # False if teacher manually hid this section
    available_from: datetime | None = None       # Section not available before this datetime
    available_until: datetime | None = None      # Section not available after this datetime


@dataclass
class CourseContent:
    """
    Full structured content of a course.
    
    Contains all sections (with subsections nested) for a course.
    """
    course_id: str
    sections: list[Section]   # Top-level sections only (subsections are nested)


@dataclass
class SearchResult:
    """
    A search result from course content.
    
    Contains the matched item, context about where it was found,
    and a relevance score.
    """
    item: ContentItem
    section_name: str         # Context: which section this came from
    snippet: str              # Highlighted text snippet
    relevance_score: float    # 0.0 to 1.0
