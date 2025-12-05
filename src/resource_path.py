"""
Resource Path Helper - Gets correct paths for PyInstaller executables
"""

import sys
import shutil
from pathlib import Path


def get_resource_path(relative_path: str) -> Path:
    """Resolve resource path, mirroring configs outside the bundle when frozen."""

    app_dir = get_app_dir()
    external_candidate = app_dir / relative_path

    if hasattr(sys, "_MEIPASS"):
        base_path = Path(getattr(sys, "_MEIPASS"))
    else:
        base_path = Path(__file__).parent.parent

    # When running as an EXE, allow editing config by copying bundled default
    if getattr(sys, 'frozen', False):
        if relative_path.startswith(("config/", "config\\")):
            if not external_candidate.exists():
                source_path = base_path / relative_path
                external_candidate.parent.mkdir(parents=True, exist_ok=True)
                try:
                    shutil.copy2(source_path, external_candidate)
                except Exception:
                    pass
            if external_candidate.exists():
                return external_candidate

    if external_candidate.exists():
        return external_candidate

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
