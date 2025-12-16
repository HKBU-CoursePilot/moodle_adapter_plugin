"""
Refresh script for moodle_adapter_plugin.

Re-runnable setup logic. Called by `adhd_framework.py refresh`.
"""

import os
import sys

current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.getcwd()
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from utils.logger_util import Logger


def refresh() -> None:
    """
    Refresh the moodle_adapter_plugin module.
    
    Called during framework refresh to ensure module is properly configured.
    This plugin doesn't require special refresh logic beyond verification.
    """
    logger = Logger(name="MoodleAdapterRefresh")
    logger.info("Refreshing moodle_adapter_plugin...")
    
    # Verify data directories exist
    data_path = os.path.join(current_dir, "data", "stubs")
    if os.path.exists(data_path):
        scenarios = [d for d in os.listdir(data_path) 
                     if os.path.isdir(os.path.join(data_path, d))]
        logger.debug(f"Found stub scenarios: {scenarios}")
    else:
        logger.warning(f"Stub data directory not found: {data_path}")
    
    logger.info("moodle_adapter_plugin refresh complete")


if __name__ == "__main__":
    refresh()
