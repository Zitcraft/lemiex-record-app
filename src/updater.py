"""
Auto-Update Module - Checks for updates via GitHub Releases API
Portable version: Downloads update and notifies user
"""

import os
import sys
import json
import tempfile
import subprocess
from pathlib import Path
from typing import Optional, Tuple
import requests

from .logger import setup_logger

logger = setup_logger("Updater")


class Updater:
    """Manages application updates via GitHub Releases"""
    
    def __init__(self, current_version: str, github_repo: str):
        """
        Initialize Updater
        
        Args:
            current_version: Current app version (e.g., "1.0.0")
            github_repo: GitHub repository (format: "owner/repo")
        """
        self.current_version = current_version
        self.github_repo = github_repo
        self.github_api_url = f"https://api.github.com/repos/{github_repo}/releases/latest"
        
        logger.info(f"Updater initialized - Current version: {current_version}")
    
    def _parse_version(self, version_str: str) -> Tuple[int, int, int]:
        """
        Parse version string to tuple
        
        Args:
            version_str: Version string like "1.0.0" or "v1.0.0"
        
        Returns:
            Tuple of (major, minor, patch)
        """
        # Remove 'v' prefix if present
        version_str = version_str.lstrip('v')
        
        try:
            parts = version_str.split('.')
            major = int(parts[0]) if len(parts) > 0 else 0
            minor = int(parts[1]) if len(parts) > 1 else 0
            patch = int(parts[2]) if len(parts) > 2 else 0
            return (major, minor, patch)
        except (ValueError, IndexError):
            logger.error(f"Invalid version format: {version_str}")
            return (0, 0, 0)
    
    def check_for_updates(self) -> Optional[dict]:
        """
        Check if a new version is available on GitHub
        
        Returns:
            Dictionary with update info if available, None otherwise
            {
                'version': '1.1.0',
                'download_url': 'https://github.com/.../LemiexRecordApp.exe',
                'release_notes': 'What\'s new...',
                'published_at': '2025-11-25T10:00:00Z'
            }
        """
        try:
            # Try /releases/latest first (excludes prerelease)
            logger.info(f"Checking for updates from: {self.github_api_url}")
            
            response = requests.get(
                self.github_api_url,
                timeout=10,
                headers={'Accept': 'application/vnd.github.v3+json'}
            )
            
            # If 404 (no non-prerelease), try all releases
            if response.status_code == 404:
                logger.info("No stable release found, checking all releases...")
                all_releases_url = f"https://api.github.com/repos/{self.github_repo}/releases"
                response = requests.get(
                    all_releases_url,
                    timeout=10,
                    headers={'Accept': 'application/vnd.github.v3+json'}
                )
                
                if response.status_code != 200:
                    logger.warning(f"GitHub API returned status {response.status_code}")
                    return None
                
                releases = response.json()
                if not releases or not isinstance(releases, list):
                    logger.warning("No releases found")
                    return None
                
                # Get the first release (most recent)
                release_data = releases[0]
            elif response.status_code != 200:
                logger.warning(f"GitHub API returned status {response.status_code}")
                return None
            else:
                release_data = response.json()
            
            # Get latest version
            latest_version = release_data.get('tag_name', '').lstrip('v')
            
            if not latest_version:
                logger.warning("No version tag found in latest release")
                return None
            
            # Compare versions
            current = self._parse_version(self.current_version)
            latest = self._parse_version(latest_version)
            
            logger.info(f"Current version: {current}, Latest version: {latest}")
            
            if latest > current:
                # Find the .exe asset
                download_url = None
                for asset in release_data.get('assets', []):
                    if asset['name'].endswith('.exe'):
                        download_url = asset['browser_download_url']
                        break
                
                if not download_url:
                    logger.warning("No .exe file found in release assets")
                    return None
                
                update_info = {
                    'version': latest_version,
                    'download_url': download_url,
                    'release_notes': release_data.get('body', 'No release notes available'),
                    'published_at': release_data.get('published_at', ''),
                    'size_bytes': asset.get('size', 0) if asset else 0
                }
                
                logger.info(f"Update available: v{latest_version}")
                return update_info
            else:
                logger.info("Application is up to date")
                return None
                
        except requests.Timeout:
            logger.warning("Update check timed out")
            return None
        except requests.RequestException as e:
            logger.error(f"Failed to check for updates: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error checking updates: {e}")
            return None
    
    def download_update(self, download_url: str, progress_callback=None) -> Optional[str]:
        """
        Download update file
        
        Args:
            download_url: URL to download the new .exe
            progress_callback: Optional callback(bytes_downloaded, total_bytes)
        
        Returns:
            Path to downloaded file, or None if failed
        """
        try:
            logger.info(f"Downloading update from: {download_url}")
            
            # Create temp file
            temp_dir = tempfile.gettempdir()
            temp_file = os.path.join(temp_dir, "LemiexRecordApp_update.exe")
            
            # Download with streaming
            response = requests.get(download_url, stream=True, timeout=300)
            response.raise_for_status()
            
            total_size = int(response.headers.get('content-length', 0))
            downloaded = 0
            
            with open(temp_file, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        
                        if progress_callback:
                            progress_callback(downloaded, total_size)
            
            logger.info(f"Update downloaded successfully: {temp_file}")
            return temp_file
            
        except Exception as e:
            logger.error(f"Failed to download update: {e}")
            return None
    
    def apply_update(self, update_file: str) -> bool:
        """
        Apply the update (for portable version, just open folder)
        
        Args:
            update_file: Path to downloaded update .exe
        
        Returns:
            True if successful
        """
        try:
            # For portable version: Open the folder containing the update
            update_folder = os.path.dirname(update_file)
            
            logger.info(f"Update ready to apply: {update_file}")
            logger.info("Opening folder with update file...")
            
            # Open Windows Explorer at the download location
            subprocess.Popen(f'explorer /select,"{update_file}"')
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to apply update: {e}")
            return False
    
    def get_current_exe_path(self) -> str:
        """Get the path to the current executable"""
        if getattr(sys, 'frozen', False):
            # Running as compiled executable
            return sys.executable
        else:
            # Running as script
            return os.path.abspath(__file__)


if __name__ == "__main__":
    # Test updater
    updater = Updater(
        current_version="1.0.0",
        github_repo="yourusername/lemiex-record-app"  # Update this
    )
    
    print(f"Current version: {updater.current_version}")
    print(f"Checking for updates...")
    
    update_info = updater.check_for_updates()
    
    if update_info:
        print(f"\n✅ Update available: v{update_info['version']}")
        print(f"Download URL: {update_info['download_url']}")
        print(f"Size: {update_info['size_bytes'] / 1024 / 1024:.2f} MB")
        print(f"\nRelease notes:\n{update_info['release_notes']}")
    else:
        print("\n✓ Application is up to date")
