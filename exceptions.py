"""
Custom exceptions for Moodle adapter.

Following ADHD exception policy:
- Tier 2 (Application & Service Errors) → Use ADHDError hierarchy
- All adapter exceptions inherit from ADHDError for consistent error handling
"""

import os
import sys

current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.getcwd()
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from cores.exceptions_core.adhd_exceptions import ADHDError


class MoodleAdapterError(ADHDError):
    """Base error for Moodle adapter operational failures."""
    pass


class CourseNotFoundError(MoodleAdapterError):
    """Raised when a course doesn't exist or is inaccessible."""
    
    def __init__(self, course_id: str, message: str | None = None):
        self.course_id = course_id
        msg = message or f"Course not found: {course_id}"
        super().__init__(msg)


class ItemNotFoundError(MoodleAdapterError):
    """Raised when a content item doesn't exist or is inaccessible."""
    
    def __init__(self, item_id: str, message: str | None = None):
        self.item_id = item_id
        msg = message or f"Content item not found: {item_id}"
        super().__init__(msg)


class AccessDeniedError(MoodleAdapterError):
    """Raised when user lacks permission to access a resource."""
    
    def __init__(self, resource: str, message: str | None = None):
        self.resource = resource
        msg = message or f"Access denied to resource: {resource}"
        super().__init__(msg)


class MoodleUnavailableError(MoodleAdapterError):
    """Raised when Moodle API is unreachable or experiencing issues."""
    
    def __init__(self, message: str | None = None):
        msg = message or "Moodle API is currently unavailable"
        super().__init__(msg)
