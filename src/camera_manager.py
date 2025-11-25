"""
Camera Manager Module - Handles webcam operations
Manages camera detection, preview, recording with timestamp overlay
"""

import cv2
import numpy as np
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Tuple
import yaml
import os
import threading
from .logger import setup_logger

# Suppress OpenCV warnings
os.environ['OPENCV_VIDEOIO_PRIORITY_MSMF'] = '0'
os.environ['OPENCV_LOG_LEVEL'] = 'ERROR'

logger = setup_logger("CameraManager")


class CameraManager:
    """Manages webcam operations including preview and recording"""
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize Camera Manager
        
        Args:
            config_path: Path to config.yaml file
        """
        if config_path is None:
            config_path = Path(__file__).parent.parent / "config" / "config.yaml"
        
        with open(config_path, 'r', encoding='utf-8') as f:
            self.config = yaml.safe_load(f)
        
        self.camera_config = self.config['camera']
        self.storage_config = self.config['storage']
        
        self.cap: Optional[cv2.VideoCapture] = None
        self.writer: Optional[cv2.VideoWriter] = None
        self.is_recording = False
        self.current_camera_index = self.camera_config['default_index']
        self._lock = threading.Lock()
        self._is_switching = False
        
        # Camera settings
        self.flip_horizontal = self.camera_config.get('flip_horizontal', False)
        self.brightness = self.camera_config.get('brightness', 50)
        
        # Create temp videos directory
        self.temp_dir = Path(__file__).parent.parent / self.storage_config['local_temp_dir']
        self.temp_dir.mkdir(exist_ok=True)
        
        logger.info("CameraManager initialized")
    
    def list_available_cameras(self, max_test: int = 3) -> List[Tuple[int, str]]:
        """
        List all available cameras
        
        Args:
            max_test: Maximum number of camera indices to test (default 3 for faster startup)
            
        Returns:
            List of tuples (index, name)
        """
        available_cameras = []
        logger.info(f"Scanning for cameras (testing indices 0-{max_test-1})")
        
        # Remember if current camera was open
        current_was_open = self.cap is not None and self.cap.isOpened()
        current_index = self.current_camera_index if current_was_open else None
        
        for i in range(max_test):
            # Skip current camera if it's open to avoid disrupting it
            if current_was_open and i == current_index:
                # Use existing info
                width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
                height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
                camera_name = f"Camera {i} ({width}x{height})"
                available_cameras.append((i, camera_name))
                logger.info(f"Found: {camera_name} (currently active)")
                continue
            
            cap = cv2.VideoCapture(i, cv2.CAP_DSHOW)  # Use DirectShow on Windows
            if cap.isOpened():
                # Try to read a frame
                ret, _ = cap.read()
                if ret:
                    backend = cap.getBackendName()
                    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
                    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
                    camera_name = f"Camera {i} ({width}x{height})"
                    available_cameras.append((i, camera_name))
                    logger.info(f"Found: {camera_name} using {backend}")
                cap.release()
        
        if not available_cameras:
            logger.warning("No cameras found")
        
        return available_cameras
    
    def start_camera(self, camera_index: int = 0) -> bool:
        """
        Start camera preview
        
        Args:
            camera_index: Index of camera to use
            
        Returns:
            True if successful, False otherwise
        """
        with self._lock:
            try:
                self._is_switching = True
                
                if self.cap is not None:
                    self.cap.release()
                    self.cap = None
                
                logger.info(f"Starting camera {camera_index}")
                self.cap = cv2.VideoCapture(camera_index, cv2.CAP_DSHOW)
                
                if not self.cap.isOpened():
                    logger.error(f"Failed to open camera {camera_index}")
                    self._is_switching = False
                    return False
                
                # Set resolution (same for preview and recording to avoid switching)
                self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.camera_config['preview_width'])
                self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.camera_config['preview_height'])
                self.cap.set(cv2.CAP_PROP_FPS, self.camera_config['fps'])
                
                # Apply camera settings
                self._apply_camera_settings()
                
                self.current_camera_index = camera_index
                logger.info(f"Camera {camera_index} started successfully at {self.camera_config['preview_width']}x{self.camera_config['preview_height']}")
                
                self._is_switching = False
                return True
                
            except Exception as e:
                logger.error(f"Error starting camera: {str(e)}")
                self._is_switching = False
                return False
    
    def stop_camera(self):
        """Stop camera preview and recording"""
        with self._lock:
            if self.is_recording:
                self.stop_recording()
            
            if self.cap is not None:
                self.cap.release()
                self.cap = None
                logger.info("Camera stopped")
    
    def get_frame(self) -> Optional[np.ndarray]:
        """
        Get current frame from camera for recording (no flip applied)
        
        Returns:
            Frame as numpy array or None if failed
        """
        # Skip frame read if camera is being switched
        if self._is_switching:
            return None
            
        if self.cap is None or not self.cap.isOpened():
            return None
        
        ret, frame = self.cap.read()
        if not ret:
            # Only log warning if not switching (to avoid spam during camera changes)
            if not self._is_switching:
                logger.warning("Failed to read frame")
            return None
        
        # Apply camera settings as image processing
        frame = self._apply_image_adjustments(frame)
        
        # Add timestamp overlay if configured
        if self.camera_config['timestamp_overlay']:
            frame = self._add_timestamp(frame)
        
        # NO flip applied - recording uses original orientation
        
        return frame
    
    def get_frame_for_preview(self) -> Optional[np.ndarray]:
        """
        Get current frame for preview (with flip applied if enabled)
        
        Returns:
            Frame as numpy array or None if failed
        """
        frame = self.get_frame()
        
        if frame is not None and self.flip_horizontal:
            # Flip horizontally for preview only (mirror effect)
            frame = cv2.flip(frame, 1)
        
        return frame
    
    def _add_timestamp(self, frame: np.ndarray) -> np.ndarray:
        """
        Add timestamp overlay to frame
        
        Args:
            frame: Input frame
            
        Returns:
            Frame with timestamp overlay
        """
        timestamp = datetime.now().strftime(self.camera_config['timestamp_format'])
        
        # Add black rectangle background for text
        cv2.rectangle(frame, (10, 10), (350, 50), (0, 0, 0), -1)
        
        # Add white text
        cv2.putText(
            frame,
            timestamp,
            (20, 38),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (255, 255, 255),
            2,
            cv2.LINE_AA
        )
        
        return frame
    
    def start_recording(self, order_id: str) -> Tuple[bool, Optional[str]]:
        """
        Start recording video
        
        Args:
            order_id: Order ID for filename
            
        Returns:
            Tuple of (success, output_filepath)
        """
        if self.cap is None or not self.cap.isOpened():
            logger.error("Camera not started")
            return False, None
        
        if self.is_recording:
            logger.warning("Already recording")
            return False, None
        
        try:
            # Generate filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = self.storage_config['filename_format'].format(
                order_id=order_id,
                timestamp=timestamp
            )
            output_path = self.temp_dir / filename
            
            # Setup video writer
            fourcc = cv2.VideoWriter_fourcc(*self.camera_config['codec'])
            self.writer = cv2.VideoWriter(
                str(output_path),
                fourcc,
                self.camera_config['fps'],
                (self.camera_config['recording_width'], self.camera_config['recording_height'])
            )
            
            if not self.writer.isOpened():
                logger.error("Failed to create video writer")
                return False, None
            
            # No need to change resolution - already at 1920x1080
            
            self.is_recording = True
            self.current_output_path = str(output_path)
            logger.info(f"Recording started: {output_path}")
            
            return True, str(output_path)
            
        except Exception as e:
            logger.error(f"Error starting recording: {str(e)}")
            return False, None
    
    def stop_recording(self) -> Optional[str]:
        """
        Stop recording video
        
        Returns:
            Path to recorded video file or None
        """
        if not self.is_recording:
            logger.warning("Not recording")
            return None
        
        try:
            output_path = self.current_output_path
            
            if self.writer is not None:
                self.writer.release()
                self.writer = None
            
            self.is_recording = False
            
            # No need to change resolution - preview and recording use same resolution
            
            logger.info(f"Recording stopped: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"Error stopping recording: {str(e)}")
            return None
    
    def write_frame(self, frame: np.ndarray) -> bool:
        """
        Write frame to video file during recording
        Frame should be unflipped (original orientation)
        
        Args:
            frame: Frame to write (unflipped)
            
        Returns:
            True if successful
        """
        if not self.is_recording or self.writer is None:
            return False
        
        try:
            # Resize frame to recording resolution if needed
            h, w = frame.shape[:2]
            target_w = self.camera_config['recording_width']
            target_h = self.camera_config['recording_height']
            
            if w != target_w or h != target_h:
                frame = cv2.resize(frame, (target_w, target_h))
            
            # Write original orientation (no flip) to video file
            self.writer.write(frame)
            return True
            
        except Exception as e:
            logger.error(f"Error writing frame: {str(e)}")
            return False
    
    def _apply_camera_settings(self):
        """Apply camera quality settings (hardware level - may not work on all cameras)"""
        if self.cap is None or not self.cap.isOpened():
            return
        
        # Try to apply hardware brightness, but don't rely on it
        # Most webcams don't support this, so we apply it in software instead
        try:
            self.cap.set(cv2.CAP_PROP_BRIGHTNESS, self.brightness / 100.0)
        except:
            pass  # Silently ignore - we handle this in software
    
    def _apply_image_adjustments(self, frame: np.ndarray) -> np.ndarray:
        """Apply camera settings as image processing
        
        Args:
            frame: Input frame
            
        Returns:
            Adjusted frame
        """
        # Apply brightness (shift pixel values)
        if self.brightness != 50:
            # Map 0-100 to -50 to +50
            brightness_value = int((self.brightness - 50) * 1.0)
            if brightness_value != 0:
                frame = cv2.convertScaleAbs(frame, alpha=1, beta=brightness_value)
        
        return frame
    
    def update_camera_setting(self, setting: str, value: int):
        """
        Update camera setting in real-time
        
        Args:
            setting: Setting name ('brightness', 'flip_horizontal')
            value: Value (0-100 for brightness)
        """
        if setting == 'brightness':
            self.brightness = value
        elif setting == 'flip_horizontal':
            self.flip_horizontal = bool(value)
        
        logger.debug(f"Updated {setting} to {value}")
    
    def __del__(self):
        """Cleanup resources"""
        self.stop_camera()


if __name__ == "__main__":
    # Test camera manager
    manager = CameraManager()
    cameras = manager.list_available_cameras()
    print(f"Found {len(cameras)} camera(s):")
    for idx, name in cameras:
        print(f"  {idx}: {name}")
