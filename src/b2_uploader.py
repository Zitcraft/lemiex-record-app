"""
Backblaze B2 Uploader Module - Handles video upload to B2 cloud storage
Manages authentication, upload with progress tracking, and retry logic
"""

import os
from pathlib import Path
from typing import Optional, Callable
from datetime import datetime
import yaml
from dotenv import load_dotenv
from b2sdk.v2 import B2Api, InMemoryAccountInfo, exception
from .logger import setup_logger

logger = setup_logger("B2Uploader")


class B2Uploader:
    """Manages video uploads to Backblaze B2"""
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize B2 Uploader
        
        Args:
            config_path: Path to config.yaml file
        """
        if config_path is None:
            config_path = Path(__file__).parent.parent / "config" / "config.yaml"
        
        # Load configuration
        with open(config_path, 'r', encoding='utf-8') as f:
            self.config = yaml.safe_load(f)
        
        self.b2_config = self.config['backblaze']
        
        # Load environment variables
        env_path = Path(__file__).parent.parent / ".env"
        load_dotenv(env_path)
        
        self.key_id = os.getenv('B2_APPLICATION_KEY_ID')
        self.app_key = os.getenv('B2_APPLICATION_KEY')
        
        # Initialize B2 API
        self.info = InMemoryAccountInfo()
        self.b2_api = B2Api(self.info)
        self.bucket = None
        self.is_authenticated = False
        
        logger.info("B2Uploader initialized")
    
    def authenticate(self) -> bool:
        """
        Authenticate with Backblaze B2
        
        Returns:
            True if authentication successful
        """
        if not self.key_id or not self.app_key:
            logger.error("B2 credentials not found in .env file")
            return False
        
        try:
            logger.info("Authenticating with Backblaze B2...")
            self.b2_api.authorize_account("production", self.key_id, self.app_key)
            
            # Get bucket
            bucket_name = self.b2_config['bucket_name']
            self.bucket = self.b2_api.get_bucket_by_name(bucket_name)
            
            self.is_authenticated = True
            logger.info(f"Authenticated successfully. Bucket: {bucket_name}")
            return True
            
        except exception.NonExistentBucket:
            logger.error(f"Bucket '{self.b2_config['bucket_name']}' not found")
            return False
        except exception.InvalidAuthToken:
            logger.error("Invalid B2 credentials")
            return False
        except Exception as e:
            logger.error(f"Authentication error: {str(e)}")
            return False
    
    def upload_video(
        self,
        file_path: str,
        order_id: str,
        progress_callback: Optional[Callable[[int, int], None]] = None
    ) -> Optional[str]:
        """
        Upload video file to B2
        
        Args:
            file_path: Path to video file
            order_id: Order ID for organizing files
            progress_callback: Callback function (bytes_uploaded, total_bytes)
            
        Returns:
            Public URL of uploaded file or None if failed
        """
        if not self.is_authenticated:
            if not self.authenticate():
                return None
        
        try:
            file_path_obj = Path(file_path)
            
            if not file_path_obj.exists():
                logger.error(f"File not found: {file_path}")
                return None
            
            # Generate B2 file path - upload directly to video/ folder
            b2_file_name = f"video/{order_id}_{file_path_obj.name}"
            
            file_size = file_path_obj.stat().st_size
            logger.info(f"Uploading {file_path_obj.name} ({file_size} bytes) to {b2_file_name}")
            
            # Create progress listener compatible with B2 SDK
            progress_listener = None
            if progress_callback:
                from b2sdk.v2 import AbstractProgressListener
                
                class ProgressListener(AbstractProgressListener):
                    def __init__(self, callback):
                        self.callback = callback
                    
                    def set_total_bytes(self, total_bytes):
                        self.total_bytes = total_bytes
                    
                    def bytes_completed(self, bytes_completed):
                        if self.callback and hasattr(self, 'total_bytes'):
                            self.callback(bytes_completed, self.total_bytes)
                
                progress_listener = ProgressListener(progress_callback)
            
            # Upload file
            file_info = self.bucket.upload_local_file(
                local_file=str(file_path),
                file_name=b2_file_name,
                content_type='video/mp4',
                file_infos={
                    'order_id': order_id,
                    'upload_date': datetime.now().isoformat()
                },
                progress_listener=progress_listener
            )
            
            # Get download URL
            download_url = self.b2_api.get_download_url_for_file_name(
                bucket_name=self.b2_config['bucket_name'],
                file_name=b2_file_name
            )
            
            logger.info(f"Upload successful: {download_url}")
            return download_url
            
        except exception.B2Error as e:
            logger.error(f"B2 error during upload: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Error uploading file: {str(e)}")
            return None
    
    def delete_local_file(self, file_path: str) -> bool:
        """
        Delete local video file after upload
        
        Args:
            file_path: Path to file to delete
            
        Returns:
            True if deleted successfully
        """
        try:
            file_path_obj = Path(file_path)
            
            if file_path_obj.exists():
                file_path_obj.unlink()
                logger.info(f"Deleted local file: {file_path}")
                return True
            else:
                logger.warning(f"File not found for deletion: {file_path}")
                return False
                
        except Exception as e:
            logger.error(f"Error deleting file: {str(e)}")
            return False
    
    def upload_json_metadata(
        self,
        json_path: str,
        order_id: str
    ) -> Optional[str]:
        """
        Upload JSON metadata file to B2
        
        Args:
            json_path: Path to JSON file
            order_id: Order ID
            
        Returns:
            Public URL of uploaded file or None if failed
        """
        if not self.is_authenticated:
            if not self.authenticate():
                return None
        
        try:
            # Get file info
            file_path_obj = Path(json_path)
            if not file_path_obj.exists():
                logger.error(f"JSON file not found: {json_path}")
                return None
            
            # Create B2 file path: json/order_id_timestamp.json
            b2_file_name = f"json/{file_path_obj.name}"
            
            logger.info(f"Uploading JSON to B2: {b2_file_name}")
            
            # Upload file
            uploaded_file = self.bucket.upload_local_file(
                local_file=json_path,
                file_name=b2_file_name,
                content_type='application/json'
            )
            
            # Get public URL
            download_url = self.b2_api.get_download_url_for_file_name(
                bucket_name=self.b2_config['bucket_name'],
                file_name=b2_file_name
            )
            
            logger.info(f"JSON uploaded successfully: {download_url}")
            return download_url
            
        except Exception as e:
            logger.error(f"Error uploading JSON: {e}")
            return None
    
    def upload_with_cleanup(
        self,
        file_path: str,
        order_id: str,
        progress_callback: Optional[Callable[[int, int], None]] = None
    ) -> Optional[str]:
        """
        Upload video and optionally delete local file
        
        Args:
            file_path: Path to video file
            order_id: Order ID
            progress_callback: Progress callback function
            
        Returns:
            Public URL or None if failed
        """
        url = self.upload_video(file_path, order_id, progress_callback)
        
        if url and self.config['storage']['auto_delete_after_upload']:
            self.delete_local_file(file_path)
        
        return url


if __name__ == "__main__":
    # Test B2 uploader
    uploader = B2Uploader()
    
    if uploader.authenticate():
        print("✓ Authentication successful")
    else:
        print("✗ Authentication failed")
