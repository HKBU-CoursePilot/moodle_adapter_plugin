"""
Moodle Adapter Plugin.

Main plugin module providing factory function to get the appropriate adapter
based on configuration. Uses Ports and Adapters pattern for clean separation.

Usage:
    from plugins.moodle_adapter_plugin import get_adapter
    
    adapter = get_adapter()  # Uses config to determine which adapter
    course_info = await adapter.get_course_info("COMP1001-2024")
"""

import os
import sys

current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.getcwd()
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from typing import Union

from managers.config_manager import ConfigManager
from utils.logger_util import Logger

from plugins.moodle_adapter_plugin.stub_adapter import StubMoodleAdapter
from plugins.moodle_adapter_plugin.file_adapter import FileMoodleAdapter
from plugins.moodle_adapter_plugin.real_adapter import RealMoodleAdapter
from plugins.moodle_adapter_plugin.moodle_port import IMoodlePort


# Type alias for any adapter implementation
MoodleAdapter = Union[StubMoodleAdapter, FileMoodleAdapter, RealMoodleAdapter]

# Singleton adapter instance
_adapter_instance: MoodleAdapter | None = None


def get_adapter(force_mode: str | None = None) -> MoodleAdapter:
    """
    Get the configured Moodle adapter instance.
    
    Uses singleton pattern - returns same instance on subsequent calls
    unless force_mode is specified.
    
    Args:
        force_mode: Override config and force a specific adapter mode.
                    Options: "stub", "file", "real"
    
    Returns:
        An adapter implementing IMoodlePort protocol
        
    Raises:
        ValueError: If adapter_mode is not recognized
    """
    global _adapter_instance
    
    logger = Logger(name="MoodleAdapterPlugin")
    
    # Return cached instance if available and no force override
    if _adapter_instance is not None and force_mode is None:
        return _adapter_instance
    
    # Get configuration
    cm = ConfigManager()
    config = cm.config.moodle_adapter_plugin
    
    # Determine adapter mode
    mode = force_mode or config.dict_get("adapter_mode") or "stub"
    logger.debug(f"Initializing Moodle adapter in '{mode}' mode")
    
    # Create appropriate adapter
    if mode == "stub":
        stub_config = config.dict_get("stub") or {}
        scenario = stub_config.get("scenario", "demo_course")
        _adapter_instance = StubMoodleAdapter(scenario=scenario)
        logger.info(f"Using StubMoodleAdapter with scenario: {scenario}")
        
    elif mode == "file":
        file_config = config.dict_get("file") or {}
        courses_path = file_config.get("courses_path", "project/data/courses")
        _adapter_instance = FileMoodleAdapter(courses_path=courses_path)
        logger.info(f"Using FileMoodleAdapter with path: {courses_path}")
        
    elif mode == "real":
        real_config = config.dict_get("real") or {}
        _adapter_instance = RealMoodleAdapter(
            api_base_url=real_config.get("api_base_url", ""),
            api_token=real_config.get("api_token", ""),
            timeout=real_config.get("timeout", 30),
            cache_ttl=real_config.get("cache_ttl", 3600),
        )
        logger.info("Using RealMoodleAdapter")
        
    else:
        raise ValueError(
            f"Unknown adapter_mode: '{mode}'. "
            f"Valid options: stub, file, real"
        )
    
    return _adapter_instance


def reset_adapter() -> None:
    """
    Reset the adapter singleton.
    
    Useful for testing or when config changes.
    """
    global _adapter_instance
    _adapter_instance = None


# Convenience function to verify adapter implements protocol
def verify_protocol(adapter: MoodleAdapter) -> bool:
    """
    Verify an adapter implements IMoodlePort protocol.
    
    Used for testing and validation.
    """
    required_methods = [
        "get_course_info",
        "get_course_content", 
        "get_item_content",
        "search",
    ]
    
    for method in required_methods:
        if not hasattr(adapter, method):
            return False
        if not callable(getattr(adapter, method)):
            return False
    
    return True
