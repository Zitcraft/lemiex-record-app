"""
Resource Path Helper - Gets correct paths for PyInstaller executables
"""

import sys
import os
from pathlib import Path


def get_resource_path(relative_path: str) -> Path:
    """
    Get absolute path to resource, works for dev and for PyInstaller
    
    Args:
        relative_path: Relative path from project root
        
    Returns:
        Absolute path to resource
    """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = Path(sys._MEIPASS)
    except AttributeError:
        # Running in normal Python environment
        base_path = Path(__file__).parent.parent
    
    return base_path / relative_path


def get_app_dir() -> Path:
    """
    Get application directory (where .exe or main.py is located)
    For writable files like .env, logs, temp_videos
    
    Returns:
        Application directory path
    """
    if getattr(sys, 'frozen', False):
        # Running as compiled executable
        return Path(sys.executable).parent
    else:
        # Running as script
        return Path(__file__).parent.parent
