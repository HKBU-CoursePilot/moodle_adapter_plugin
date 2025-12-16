"""
Real Moodle adapter (placeholder).

This adapter will connect to the actual Moodle API when available.
Currently a placeholder that raises NotImplementedError.
"""

import os
import sys

current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.getcwd()
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from utils.logger_util import Logger

from plugins.moodle_adapter_plugin.models import (
    CourseInfo,
    CourseContent,
    SearchResult,
)
from plugins.moodle_adapter_plugin.exceptions import MoodleUnavailableError


class RealMoodleAdapter:
    """
    Real implementation of IMoodlePort.
    
    Connects to Moodle's Web Services API for live course data.
    
    NOTE: This is a placeholder. Implementation will be added when
    the Moodle API becomes available and endpoints are documented.
    
    Expected Moodle endpoints:
    - core_course_get_courses_by_field: Get course metadata
    - core_course_get_contents: Get sections and modules
    - core_search_get_results: Search course content (if Global Search enabled)
    """
    
    def __init__(
        self,
        api_base_url: str,
        api_token: str,
        timeout: int = 30,
        cache_ttl: int = 3600,
    ):
        """
        Initialize real adapter with API credentials.
        
        Args:
            api_base_url: Base URL for Moodle API
            api_token: Moodle Web Services API token
            timeout: Request timeout in seconds
            cache_ttl: Cache TTL in seconds (0 = no cache)
        """
        self.api_base_url = api_base_url
        self.api_token = api_token
        self.timeout = timeout
        self.cache_ttl = cache_ttl
        self.logger = Logger(name="RealMoodleAdapter")
        
        if not api_base_url or not api_token:
            self.logger.warning("Real Moodle adapter initialized without credentials")
    
    async def get_course_info(self, course_id: str) -> CourseInfo:
        """Get course metadata from Moodle API."""
        raise MoodleUnavailableError(
            "Real Moodle adapter is not yet implemented. "
            "Use 'stub' or 'file' adapter_mode in config."
        )
    
    async def get_course_content(self, course_id: str) -> CourseContent:
        """Get course content from Moodle API."""
        raise MoodleUnavailableError(
            "Real Moodle adapter is not yet implemented. "
            "Use 'stub' or 'file' adapter_mode in config."
        )
    
    async def get_item_content(self, item_id: str) -> str:
        """Get item content from Moodle API."""
        raise MoodleUnavailableError(
            "Real Moodle adapter is not yet implemented. "
            "Use 'stub' or 'file' adapter_mode in config."
        )
    
    async def search(self, query: str, course_id: str) -> list[SearchResult]:
        """Search course content via Moodle API."""
        raise MoodleUnavailableError(
            "Real Moodle adapter is not yet implemented. "
            "Use 'stub' or 'file' adapter_mode in config."
        )
