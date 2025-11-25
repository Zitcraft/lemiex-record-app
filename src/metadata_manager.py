"""
Metadata Manager Module - Handles recording metadata JSON files
Saves recording information for system integration
"""

import json
from pathlib import Path
from datetime import datetime
from typing import Optional
import yaml
from .logger import setup_logger

logger = setup_logger("MetadataManager")


class MetadataManager:
    """Manages recording metadata JSON files"""
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize MetadataManager
        
        Args:
            config_path: Optional path to config.yaml file
        """
        try:
            # Load configuration
            if config_path is None:
                config_path = Path(__file__).parent.parent / "config" / "config.yaml"
            else:
                config_path = Path(config_path)
            
            with open(config_path, 'r', encoding='utf-8') as f:
                self.config = yaml.safe_load(f)
            
            # Setup metadata directory
            self.metadata_dir = Path(__file__).parent.parent / "metadata"
            self.metadata_dir.mkdir(exist_ok=True)
            
            logger.info(f"MetadataManager initialized. Metadata directory: {self.metadata_dir}")
            
        except Exception as e:
            logger.error(f"Failed to initialize MetadataManager: {e}")
            raise
    
    def save_metadata(self, order_id: str, username: str, video_url: str, json_b2_url: Optional[str] = None, user_id: Optional[str] = None, duration: Optional[int] = None) -> bool:
        """
        Save recording metadata as JSON file
        
        Args:
            order_id: Order ID
            username: Username who made the recording
            video_url: B2 upload URL
            json_b2_url: B2 JSON URL (optional)
            user_id: User ID (optional)
            duration: Recording duration in seconds (optional)
            
        Returns:
            True if saved successfully, False otherwise
        """
        try:
            # Get current timestamp
            now = datetime.now()
            timestamp = now.strftime("%Y%m%d_%H%M%S")
            
            # Create metadata structure
            metadata = {
                "id": order_id,
                "date": now.strftime("%Y-%m-%d"),
                "time": now.strftime("%H:%M:%S"),
                "user": username,
                "url_upload": video_url,
                "duration": duration if duration is not None else 0
            }
            
            # Add optional fields
            if user_id:
                metadata["id_user"] = user_id
            if json_b2_url:
                metadata["url_json"] = json_b2_url
            
            # Create filename
            filename = f"{order_id}_{timestamp}.json"
            filepath = self.metadata_dir / filename
            
            # Save JSON with pretty formatting
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Metadata saved successfully: {filename}")
            logger.debug(f"Metadata content: {metadata}")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to save metadata for order {order_id}: {e}")
            return False
    
    def get_metadata(self, order_id: str) -> Optional[dict]:
        """
        Get metadata for an order (returns most recent if multiple exist)
        
        Args:
            order_id: Order ID to search for
            
        Returns:
            Dictionary containing metadata, or None if not found
        """
        try:
            # Search for files matching the order_id
            matching_files = list(self.metadata_dir.glob(f"{order_id}_*.json"))
            
            if not matching_files:
                logger.warning(f"No metadata found for order {order_id}")
                return None
            
            # Get the most recent file
            latest_file = max(matching_files, key=lambda p: p.stat().st_mtime)
            
            # Load and return the metadata
            with open(latest_file, 'r', encoding='utf-8') as f:
                metadata = json.load(f)
            
            logger.info(f"Metadata retrieved for order {order_id}: {latest_file.name}")
            return metadata
            
        except Exception as e:
            logger.error(f"Failed to get metadata for order {order_id}: {e}")
            return None
    
    def get_all_metadata(self, order_id: str) -> list:
        """
        Get all metadata files for an order
        
        Args:
            order_id: Order ID to search for
            
        Returns:
            List of metadata dictionaries, sorted by timestamp (newest first)
        """
        try:
            # Search for files matching the order_id
            matching_files = list(self.metadata_dir.glob(f"{order_id}_*.json"))
            
            if not matching_files:
                logger.warning(f"No metadata found for order {order_id}")
                return []
            
            # Load all metadata files
            metadata_list = []
            for file in matching_files:
                try:
                    with open(file, 'r', encoding='utf-8') as f:
                        metadata = json.load(f)
                        metadata['_filename'] = file.name  # Add filename for reference
                        metadata_list.append(metadata)
                except Exception as e:
                    logger.error(f"Failed to load metadata file {file.name}: {e}")
            
            # Sort by filename (which includes timestamp) in reverse order
            metadata_list.sort(key=lambda x: x.get('_filename', ''), reverse=True)
            
            logger.info(f"Retrieved {len(metadata_list)} metadata files for order {order_id}")
            return metadata_list
            
        except Exception as e:
            logger.error(f"Failed to get all metadata for order {order_id}: {e}")
            return []
    
    def list_all_metadata(self) -> list:
        """
        List all metadata files in the directory
        
        Returns:
            List of all metadata dictionaries, sorted by timestamp (newest first)
        """
        try:
            all_files = list(self.metadata_dir.glob("*.json"))
            
            if not all_files:
                logger.info("No metadata files found")
                return []
            
            # Load all metadata files
            metadata_list = []
            for file in all_files:
                try:
                    with open(file, 'r', encoding='utf-8') as f:
                        metadata = json.load(f)
                        metadata['_filename'] = file.name
                        metadata_list.append(metadata)
                except Exception as e:
                    logger.error(f"Failed to load metadata file {file.name}: {e}")
            
            # Sort by filename (timestamp) in reverse order
            metadata_list.sort(key=lambda x: x.get('_filename', ''), reverse=True)
            
            logger.info(f"Retrieved {len(metadata_list)} total metadata files")
            return metadata_list
            
        except Exception as e:
            logger.error(f"Failed to list all metadata: {e}")
            return []
    
    def delete_metadata(self, order_id: str, timestamp: Optional[str] = None) -> bool:
        """
        Delete metadata file(s) for an order
        
        Args:
            order_id: Order ID
            timestamp: Optional specific timestamp. If None, deletes all files for order_id
            
        Returns:
            True if deleted successfully
        """
        try:
            if timestamp:
                # Delete specific file
                filename = f"{order_id}_{timestamp}.json"
                filepath = self.metadata_dir / filename
                
                if filepath.exists():
                    filepath.unlink()
                    logger.info(f"Deleted metadata file: {filename}")
                    return True
                else:
                    logger.warning(f"Metadata file not found: {filename}")
                    return False
            else:
                # Delete all files for the order_id
                matching_files = list(self.metadata_dir.glob(f"{order_id}_*.json"))
                
                if not matching_files:
                    logger.warning(f"No metadata files found for order {order_id}")
                    return False
                
                for file in matching_files:
                    file.unlink()
                    logger.info(f"Deleted metadata file: {file.name}")
                
                return True
                
        except Exception as e:
            logger.error(f"Failed to delete metadata for order {order_id}: {e}")
            return False


if __name__ == "__main__":
    # Test the MetadataManager
    manager = MetadataManager()
    
    # Save test metadata
    success = manager.save_metadata(
        order_id="12345",
        username="john_doe",
        video_url="https://f005.backblazeb2.com/file/LemiexEmbroidery/test_video.mp4"
    )
    
    print(f"Save metadata: {'Success' if success else 'Failed'}")
    
    # Retrieve metadata
    metadata = manager.get_metadata("12345")
    if metadata:
        print(f"Retrieved metadata: {json.dumps(metadata, indent=2)}")
