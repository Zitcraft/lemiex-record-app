"""
API Client Module - Handles communication with backend API
Manages user info retrieval, order validation, and metadata logging
"""

import os
import requests
from typing import Optional, Dict, Any
from pathlib import Path
from datetime import datetime
import yaml
from dotenv import load_dotenv
from .logger import setup_logger

logger = setup_logger("APIClient")


class APIClient:
    """Manages API communication with backend server"""
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize API Client
        
        Args:
            config_path: Path to config.yaml file
        """
        if config_path is None:
            from .resource_path import get_resource_path
            config_path = get_resource_path("config/config.yaml")
        
        # Load configuration
        with open(str(config_path), 'r', encoding='utf-8') as f:
            self.config = yaml.safe_load(f)
        
        self.api_config = self.config['api']
        
        # Load environment variables
        from .resource_path import get_app_dir
        env_path = get_app_dir() / ".env"
        load_dotenv(env_path)
        
        self.api_key = os.getenv('API_KEY')
        self.api_secret = os.getenv('API_SECRET')
        
        # Use custom base URL from env if available
        self.base_url = os.getenv('API_BASE_URL', self.api_config['base_url'])
        
        # Setup session with default headers
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'User-Agent': 'LemiexRecordApp/1.0'
        })
        
        if self.api_key:
            self.session.headers['X-API-Key'] = self.api_key
        
        logger.info(f"APIClient initialized with base URL: {self.base_url}")
    
    def _make_request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict] = None,
        params: Optional[Dict] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Make HTTP request to API
        
        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint
            data: Request body data
            params: URL parameters
            
        Returns:
            Response JSON or None if failed
        """
        url = f"{self.base_url}{endpoint}"
        
        try:
            logger.debug(f"{method} {url}")
            
            response = self.session.request(
                method=method,
                url=url,
                json=data,
                params=params,
                timeout=self.api_config['timeout']
            )
            
            response.raise_for_status()
            
            logger.debug(f"Response status: {response.status_code}")
            return response.json()
            
        except requests.exceptions.HTTPError as e:
            logger.error(f"HTTP error: {e.response.status_code} - {e.response.text}")
            return None
        except requests.exceptions.ConnectionError:
            logger.error(f"Connection error: Unable to connect to {url}")
            return None
        except requests.exceptions.Timeout:
            logger.error(f"Request timeout: {url}")
            return None
        except requests.exceptions.RequestException as e:
            logger.error(f"Request error: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}")
            return None
    
    def get_user_info(self, user_id: str) -> Optional[Dict[str, Any]]:
        """
        Get user information from API
        
        Args:
            user_id: User ID to lookup
            
        Returns:
            User info dict or None if failed
        """
        endpoint = self.api_config['endpoints']['user_info'].format(user_id=user_id)
        
        logger.info(f"Fetching user info for: {user_id}")
        result = self._make_request('GET', endpoint)
        
        if result:
            logger.info(f"Retrieved user info: {result.get('name', 'Unknown')}")
        
        return result
    
    def validate_order(self, order_id: str) -> Optional[Dict[str, Any]]:
        """
        Validate order ID with API
        
        Args:
            order_id: Order ID to validate
            
        Returns:
            Order info dict or None if invalid
        """
        endpoint = self.api_config['endpoints']['order_validate'].format(order_id=order_id)
        
        logger.info(f"Validating order: {order_id}")
        result = self._make_request('GET', endpoint)
        
        if result:
            logger.info(f"Order validated: {order_id}")
        else:
            logger.warning(f"Order validation failed: {order_id}")
        
        return result
    
    def upload_recording_metadata(
        self,
        order_id: str,
        user_id: str,
        video_url: str,
        duration: Optional[float] = None,
        file_size: Optional[int] = None,
        additional_data: Optional[Dict] = None
    ) -> bool:
        """
        Upload recording metadata to API
        
        Args:
            order_id: Order ID
            user_id: User ID who recorded
            video_url: URL of uploaded video
            duration: Video duration in seconds
            file_size: File size in bytes
            additional_data: Additional metadata
            
        Returns:
            True if successful
        """
        endpoint = self.api_config['endpoints']['upload_metadata']
        
        metadata = {
            'order_id': order_id,
            'user_id': user_id,
            'video_url': video_url,
            'recorded_at': datetime.now().isoformat(),
            'duration': duration,
            'file_size': file_size
        }
        
        if additional_data:
            metadata.update(additional_data)
        
        logger.info(f"Uploading metadata for order: {order_id}")
        result = self._make_request('POST', endpoint, data=metadata)
        
        if result:
            logger.info("Metadata uploaded successfully")
            return True
        else:
            logger.error("Failed to upload metadata")
            return False
    
    def get_staff_list(self) -> Optional[list]:
        """
        Get list of staff members from API
        
        Returns:
            List of staff dicts with id, username, full_name or None
        """
        endpoint = self.api_config['endpoints']['staff_list']
        
        logger.info("Fetching staff list")
        result = self._make_request('GET', endpoint)
        
        if result and isinstance(result, list):
            # Filter out staff with null full_name
            filtered_staff = [staff for staff in result if staff.get('full_name')]
            
            # Apply blacklist if configured
            blacklist = self.api_config.get('staff_blacklist', [])
            if blacklist:
                filtered_staff = [staff for staff in filtered_staff if staff['id'] not in blacklist]
            
            logger.info(f"Retrieved {len(filtered_staff)} staff member(s)")
            return filtered_staff
        
        logger.warning("Failed to fetch staff list or invalid format")
        return None
    
    def search_user_by_name(self, name: str) -> Optional[list]:
        """
        Search users by name (if API supports it)
        
        Args:
            name: User name to search
            
        Returns:
            List of matching users or None
        """
        endpoint = "/users/search"
        params = {'q': name}
        
        logger.info(f"Searching users with name: {name}")
        result = self._make_request('GET', endpoint, params=params)
        
        if result and isinstance(result, dict) and 'users' in result:
            logger.info(f"Found {len(result['users'])} user(s)")
            return result['users']
        
        return None
    
    def ping(self) -> bool:
        """
        Test API connectivity
        
        Returns:
            True if API is reachable
        """
        try:
            response = requests.get(
                f"{self.base_url}/health",
                timeout=5
            )
            is_healthy = response.status_code == 200
            
            if is_healthy:
                logger.info("API is reachable")
            else:
                logger.warning(f"API returned status: {response.status_code}")
            
            return is_healthy
            
        except Exception as e:
            logger.error(f"API ping failed: {str(e)}")
            return False


if __name__ == "__main__":
    # Test API client
    client = APIClient()
    
    print(f"Base URL: {client.base_url}")
    print(f"Testing connectivity...")
    
    if client.ping():
        print("✓ API is reachable")
    else:
        print("✗ API is not reachable")
