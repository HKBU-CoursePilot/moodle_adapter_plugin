"""
Moodle Adapter Plugin - Entry point and exports.

Provides unified interface to Moodle course content via Ports and Adapters pattern.
Supports stub (fake data), file (local files), and real (Moodle API) adapters.
"""

import os
import sys

current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.getcwd()
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Main exports
from plugins.moodle_adapter_plugin.moodle_adapter_plugin import (
    get_adapter,
    reset_adapter,
    verify_protocol,
    MoodleAdapter,
)

# Domain models
from plugins.moodle_adapter_plugin.models import (
    CourseInfo,
    ContentItem,
    Section,
    CourseContent,
    SearchResult,
    ItemType,
)

# Protocol interface
from plugins.moodle_adapter_plugin.moodle_port import IMoodlePort

# Exceptions
from plugins.moodle_adapter_plugin.exceptions import (
    MoodleAdapterError,
    CourseNotFoundError,
    ItemNotFoundError,
    AccessDeniedError,
    MoodleUnavailableError,
)

# Adapters (for direct use if needed)
from plugins.moodle_adapter_plugin.stub_adapter import StubMoodleAdapter
from plugins.moodle_adapter_plugin.file_adapter import FileMoodleAdapter
from plugins.moodle_adapter_plugin.real_adapter import RealMoodleAdapter


__all__ = [
    # Factory function
    "get_adapter",
    "reset_adapter",
    "verify_protocol",
    "MoodleAdapter",
    
    # Protocol
    "IMoodlePort",
    
    # Models
    "CourseInfo",
    "ContentItem",
    "Section",
    "CourseContent",
    "SearchResult",
    "ItemType",
    
    # Exceptions
    "MoodleAdapterError",
    "CourseNotFoundError",
    "ItemNotFoundError",
    "AccessDeniedError",
    "MoodleUnavailableError",
    
    # Adapters
    "StubMoodleAdapter",
    "FileMoodleAdapter",
    "RealMoodleAdapter",
]
