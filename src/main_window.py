"""
Main Window Module - GUI application using CustomTkinter
Provides interface for camera preview, scanner input, and recording control
"""

import customtkinter as ctk
from tkinter import messagebox
import cv2
from PIL import Image, ImageTk
import threading
import os
from pathlib import Path
from typing import Optional
import yaml
import pygame

from .camera_manager import CameraManager
from .scanner_manager import ScannerManager
from .b2_uploader import B2Uploader
from .api_client import APIClient
from .metadata_manager import MetadataManager
from .updater import Updater
from .logger import setup_logger

logger = setup_logger("MainWindow")


class MainWindow(ctk.CTk):
    """Main application window"""
    
    def __init__(self):
        super().__init__()
        
        # Load configuration
        from .resource_path import get_resource_path
        config_path = get_resource_path("config/config.yaml")
        with open(str(config_path), 'r', encoding='utf-8') as f:
            self.config = yaml.safe_load(f)
        
        app_config = self.config['app']
        
        # Configure window
        self.title(app_config['name'])
        self.geometry(f"{app_config['window_width']}x{app_config['window_height']}")
        
        # Set theme
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        # Initialize sound system
        try:
            pygame.mixer.init()
            from .resource_path import get_resource_path
            self.voice_dir = get_resource_path("voice")
            logger.info(f"Sound system initialized: {self.voice_dir}")
        except Exception as e:
            logger.error(f"Failed to initialize sound system: {e}")
            self.voice_dir = None
        
        # Initialize managers as None - will be loaded later
        self.camera_manager = None
        self.scanner_manager = None
        self.b2_uploader = None
        self.api_client = None
        self.metadata_manager = None
        
        # State variables
        self.is_recording = False
        self.current_video_path: Optional[str] = None
        self.current_recording_order: Optional[str] = None
        self.update_preview_running = False
        self.staff_data = {}  # Map display name to staff dict
        self.scanner_ports = {}  # Map scanner display name to port
        self.camera_indices = {}  # Map camera display name to index
        
        # Recording timer
        self.recording_start_time = None
        self.timer_running = False
        
        # Auto-delete setting
        storage_config = self.config.get('storage', {})
        self.auto_delete_var = ctk.BooleanVar(value=storage_config.get('auto_delete_after_upload', True))
        
        # Setup UI first for fast startup
        self.setup_ui()
        
        # Show window immediately
        self.update()
        
        logger.info("MainWindow UI loaded, initializing components...")
        
        # Load components in background
        self.after(50, self._initialize_managers)
        
    def _initialize_managers(self):
        """Initialize all managers after UI is shown"""
        # Initialize managers
        self.camera_manager = CameraManager()
        self.scanner_manager = ScannerManager()
        self.b2_uploader = B2Uploader()
        self.api_client = APIClient()
        self.metadata_manager = MetadataManager()
        
        # Initialize updater
        app_config = self.config['app']
        self.updater = Updater(
            current_version=app_config['version'],
            github_repo=app_config.get('github_repo', 'yourusername/lemiex-record-app')
        )
        
        # Update UI with camera settings
        self.brightness_slider.set(self.camera_manager.brightness)
        if self.camera_manager.flip_horizontal:
            self.flip_checkbox.select()
        
        # Initialize camera list
        self.refresh_camera_list()
        
        # Start camera preview
        self.start_camera_preview()
        
        # Defer scanner and staff list to further improve perceived speed
        self.after(100, self.refresh_scanner_list)
        self.after(200, self.refresh_staff_list)
        
        # Check for updates if enabled
        if app_config.get('check_updates_on_startup', False):
            self.after(1000, self._check_for_updates_background)
        
        logger.info("All components initialized")
    
    def setup_ui(self):
        """Setup user interface"""
        
        # Configure grid
        self.grid_columnconfigure(0, weight=2)
        self.grid_columnconfigure(1, weight=2)
        self.grid_rowconfigure(0, weight=1)
        
        # Left panel - Camera preview
        self.left_frame = ctk.CTkFrame(self, corner_radius=10)
        self.left_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        
        # Camera preview label
        self.camera_label = ctk.CTkLabel(
            self.left_frame,
            text="Camera Preview",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        self.camera_label.pack(pady=(10, 5))
        
        # Canvas for video preview
        self.preview_canvas = ctk.CTkLabel(
            self.left_frame,
            text="No camera feed",
            width=640,
            height=360
        )
        self.preview_canvas.pack(pady=10, padx=0)
        
        # Right panel - Controls
        self.right_frame = ctk.CTkFrame(self, corner_radius=10)
        self.right_frame.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
        
        # Create scrollable frame for controls
        self.scrollable_frame = ctk.CTkScrollableFrame(
            self.right_frame,
            corner_radius=10
        )
        self.scrollable_frame.pack(fill="both", expand=True, padx=0, pady=0)
        
        # Title
        title_label = ctk.CTkLabel(
            self.scrollable_frame,
            text="Điều khiển",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        title_label.pack(pady=(20, 10))
        
        # Camera selection
        camera_label = ctk.CTkLabel(self.scrollable_frame, text="Chọn Camera:", anchor="w")
        camera_label.pack(pady=(10, 5), padx=20, fill="x")
        
        self.camera_combobox = ctk.CTkComboBox(
            self.scrollable_frame,
            values=["Đang tải..."],
            command=self.on_camera_changed
        )
        self.camera_combobox.pack(pady=5, padx=20, fill="x")
        
        # Refresh camera button
        refresh_cam_btn = ctk.CTkButton(
            self.scrollable_frame,
            text="🔄 Làm mới",
            command=self.refresh_camera_list,
            width=100
        )
        refresh_cam_btn.pack(pady=5)

        # Camera Settings Section
        settings_label = ctk.CTkLabel(
            self.scrollable_frame,
            text="Cài đặt Camera:",
            font=ctk.CTkFont(size=14, weight="bold"),
            anchor="w"
        )
        settings_label.pack(pady=(20, 10), padx=20, fill="x")
        
        # Brightness
        brightness_label = ctk.CTkLabel(self.scrollable_frame, text="Độ sáng:", anchor="w")
        brightness_label.pack(pady=(5, 2), padx=20, fill="x")
        
        self.brightness_slider = ctk.CTkSlider(
            self.scrollable_frame,
            from_=0,
            to=100,
            number_of_steps=100,
            command=lambda v: self.on_camera_setting_changed('brightness', int(v))
        )
        self.brightness_slider.pack(pady=(0, 10), padx=20, fill="x")
        self.brightness_slider.set(50)  # Default value, will be updated when manager loads
        
        # Flip camera checkbox
        self.flip_checkbox = ctk.CTkCheckBox(
            self.scrollable_frame,
            text="Lật camera (mirror)",
            command=self.on_flip_changed
        )
        self.flip_checkbox.pack(pady=(10, 5), padx=20, fill="x")
        # Flip state will be set when manager loads
        
        # Auto-delete checkbox
        self.auto_delete_checkbox = ctk.CTkCheckBox(
            self.scrollable_frame,
            text="Tự động xóa video local sau khi upload",
            variable=self.auto_delete_var
        )
        self.auto_delete_checkbox.pack(pady=(5, 5), padx=20, fill="x")
        
        # Scanner selection
        scanner_label = ctk.CTkLabel(self.scrollable_frame, text="Chọn Scanner:", anchor="w")
        scanner_label.pack(pady=(20, 5), padx=20, fill="x")
        
        self.scanner_combobox = ctk.CTkComboBox(
            self.scrollable_frame,
            values=["Đang tải..."],
            command=self.on_scanner_changed
        )
        self.scanner_combobox.pack(pady=5, padx=20, fill="x")
        
        # Refresh scanner button
        refresh_scanner_btn = ctk.CTkButton(
            self.scrollable_frame,
            text="🔄 Làm mới",
            command=self.refresh_scanner_list,
            width=100
        )
        refresh_scanner_btn.pack(pady=5)
        
        # Order ID input
        order_label = ctk.CTkLabel(self.scrollable_frame, text="Mã đơn:", anchor="w")
        order_label.pack(pady=(20, 5), padx=20, fill="x")
        
        self.order_entry = ctk.CTkEntry(
            self.scrollable_frame,
            placeholder_text="Nhập hoặc scan mã đơn"
        )
        self.order_entry.pack(pady=5, padx=20, fill="x")
        
        # User selection
        user_label = ctk.CTkLabel(self.scrollable_frame, text="Người sử dụng:", anchor="w")
        user_label.pack(pady=(20, 5), padx=20, fill="x")
        
        self.user_combobox = ctk.CTkComboBox(
            self.scrollable_frame,
            values=["Đang tải..."],
            command=self.on_user_changed
        )
        self.user_combobox.pack(pady=5, padx=20, fill="x")
        
        # Refresh staff button
        refresh_staff_btn = ctk.CTkButton(
            self.scrollable_frame,
            text="🔄 Làm mới",
            command=self.refresh_staff_list,
            width=100
        )
        refresh_staff_btn.pack(pady=5)
        
        # Recording timer label
        self.timer_label = ctk.CTkLabel(
            self.scrollable_frame,
            text="00:00",
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color="#666666"
        )
        self.timer_label.pack(pady=(30, 5), padx=20)
        
        # Record button
        self.record_button = ctk.CTkButton(
            self.scrollable_frame,
            text="⏺ Bắt đầu ghi hình",
            command=self.toggle_recording,
            height=50,
            font=ctk.CTkFont(size=16, weight="bold"),
            fg_color="#DC2626",
            hover_color="#991B1B"
        )
        self.record_button.pack(pady=(5, 10), padx=20, fill="x")
        
        # Status label
        self.status_label = ctk.CTkLabel(
            self.scrollable_frame,
            text="Sẵn sàng",
            font=ctk.CTkFont(size=12),
            text_color="green"
        )
        self.status_label.pack(pady=10)
        
        # Progress bar
        self.progress_bar = ctk.CTkProgressBar(self.scrollable_frame)
        self.progress_bar.pack(pady=10, padx=20, fill="x")
        self.progress_bar.set(0)
        self.progress_bar.pack_forget()  # Hidden by default
        
        
    
    def refresh_camera_list(self):
        """Refresh list of available cameras"""
        if self.camera_manager is None:
            return
            
        logger.info("Refreshing camera list")
        
        # Remember current camera if any
        current_camera_idx = self.camera_manager.current_camera_index if self.camera_manager.cap is not None else None
        
        cameras = self.camera_manager.list_available_cameras()
        
        if cameras:
            camera_names = [name for idx, name in cameras]
            self.camera_combobox.configure(values=camera_names)
            self.camera_combobox.set(camera_names[0])
            self.camera_indices = {name: idx for idx, name in cameras}
            
            # Restart camera if it was running
            if current_camera_idx is not None:
                # Find the camera name for current index
                for name, idx in self.camera_indices.items():
                    if idx == current_camera_idx:
                        self.camera_combobox.set(name)
                        self.camera_manager.start_camera(current_camera_idx)
                        break
        else:
            self.camera_combobox.configure(values=["Không tìm thấy camera"])
            self.camera_combobox.set("Không tìm thấy camera")
            self.camera_indices = {}
    
    def refresh_scanner_list(self):
        """Refresh list of available scanners"""
        if self.scanner_manager is None:
            return
            
        logger.info("Refreshing scanner list")
        ports = self.scanner_manager.list_available_ports()
        
        if ports:
            port_names = [f"{port} - {desc}" for port, desc, hwid in ports]
            self.scanner_combobox.configure(values=port_names)
            
            # Create scanner_ports mapping first
            self.scanner_ports = {name: port for (port, desc, hwid), name in zip(ports, port_names)}
            
            # Try auto-detect
            auto_port = self.scanner_manager.auto_detect_scanner()
            if auto_port:
                for i, (port, desc, hwid) in enumerate(ports):
                    if port == auto_port:
                        self.scanner_combobox.set(port_names[i])
                        # Auto-connect to detected scanner
                        self.on_scanner_changed(port_names[i])
                        break
            else:
                self.scanner_combobox.set(port_names[0])
        else:
            self.scanner_combobox.configure(values=["Không tìm thấy cổng COM"])
            self.scanner_combobox.set("Không tìm thấy cổng COM")
            self.scanner_ports = {}
    
    def on_camera_changed(self, choice: str):
        """Handle camera selection change"""
        if self.camera_manager is None:
            return
            
        if choice in self.camera_indices:
            camera_idx = self.camera_indices[choice]
            logger.info(f"Switching to camera: {choice}")
            
            # Disable camera selection during switch
            self.camera_combobox.configure(state="disabled")
            self.status_label.configure(text="Đang chuyển camera...", text_color="orange")
            
            def switch_camera():
                # Capture manager reference
                if self.camera_manager is None:
                    return
                    
                # Stop current camera
                self.camera_manager.stop_camera()
                # Small delay to ensure camera is released
                import time
                time.sleep(0.3)
                # Start new camera
                success = self.camera_manager.start_camera(camera_idx)
                
                # Update UI in main thread
                def update_ui():
                    self.camera_combobox.configure(state="normal")
                    if success:
                        self.status_label.configure(text=f"Đã chuyển: {choice}", text_color="green")
                    else:
                        self.status_label.configure(text="Lỗi chuyển camera", text_color="red")
                
                self.after(0, update_ui)
            
            # Run in background thread to prevent UI freeze
            threading.Thread(target=switch_camera, daemon=True).start()
    
    def on_scanner_changed(self, choice: str):
        """Handle scanner selection change"""
        if self.scanner_manager is None:
            return
            
        if choice in self.scanner_ports:
            port = self.scanner_ports[choice]
            logger.info(f"Connecting to scanner: {port}")
            
            if self.scanner_manager.connect(port):
                self.status_label.configure(text=f"Scanner kết nối: {port}", text_color="green")
                # Start listening for scans
                self.scanner_manager.start_listening(self.on_barcode_scanned)
            else:
                self.status_label.configure(text="Lỗi kết nối scanner", text_color="red")
    
    def on_barcode_scanned(self, order_id: str):
        """Handle barcode scan event"""
        logger.info(f"Barcode scanned: {order_id}")
        
        current_order = self.order_entry.get().strip()
        
        # Case 1: Not recording - start recording with new order
        if not self.is_recording:
            self.order_entry.delete(0, 'end')
            self.order_entry.insert(0, order_id)
            self.status_label.configure(text=f"Đã scan: {order_id}", text_color="blue")
            # Auto start recording
            self.after(100, self.start_recording)
        
        # Case 2: Recording same order - stop recording
        elif current_order == order_id:
            logger.info(f"Scanned same order {order_id} - stopping recording")
            self.status_label.configure(text=f"Scan lại mã {order_id} - Dừng ghi", text_color="orange")
            self.stop_recording(auto_mode=False)
        
        # Case 3: Recording different order - stop current, start new
        else:
            logger.info(f"Scanned different order {order_id} - switching recording")
            self.status_label.configure(text=f"Chuyển sang mã {order_id}", text_color="orange")
            # Stop current recording (auto mode - no popup)
            self.stop_recording(auto_mode=True)
            # Update order ID
            self.order_entry.delete(0, 'end')
            self.order_entry.insert(0, order_id)
            # Start new recording after a short delay
            self.after(500, self.start_recording)
    
    def refresh_staff_list(self):
        """Refresh list of staff members"""
        if self.api_client is None:
            return
            
        logger.info("Refreshing staff list")
        
        def fetch():
            if self.api_client is None:
                return
            staff_list = self.api_client.get_staff_list()
            
            if staff_list:
                # Create display names: "full_name (username)"
                staff_names = [f"{staff['full_name']} ({staff['username']})" for staff in staff_list]
                staff_data = {name: staff for name, staff in zip(staff_names, staff_list)}
                
                # Update UI in main thread
                def update_ui():
                    self.staff_data = staff_data
                    self.user_combobox.configure(values=staff_names)
                    if staff_names:
                        self.user_combobox.set(staff_names[0])
                        self.status_label.configure(
                            text=f"Đã tải {len(staff_names)} nhân viên",
                            text_color="green"
                        )
                
                self.after(0, update_ui)
            else:
                def update_ui_error():
                    self.user_combobox.configure(values=["Không tải được danh sách"])
                    self.user_combobox.set("Không tải được danh sách")
                    self.status_label.configure(
                        text="Lỗi tải danh sách nhân viên",
                        text_color="red"
                    )
                    self.staff_data = {}
                
                self.after(0, update_ui_error)
        
        threading.Thread(target=fetch, daemon=True).start()
    
    def on_user_changed(self, choice: str):
        """Handle user selection change"""
        if choice in self.staff_data:
            staff = self.staff_data[choice]
            logger.info(f"Selected user: {staff['username']} (ID: {staff['id']})")
            self.status_label.configure(
                text=f"Đã chọn: {staff['full_name']}",
                text_color="blue"
            )
    
    def on_camera_setting_changed(self, setting: str, value: int):
        """Handle camera setting slider change"""
        if self.camera_manager is None:
            return
        self.camera_manager.update_camera_setting(setting, value)
        logger.info(f"Camera {setting} changed to {value}")
    
    def on_flip_changed(self):
        """Handle flip camera checkbox change"""
        if self.camera_manager is None:
            return
        is_flipped = self.flip_checkbox.get()
        self.camera_manager.update_camera_setting('flip_horizontal', 1 if is_flipped else 0)
        logger.info(f"Camera flip: {is_flipped}")
    
    def get_current_user_id(self) -> Optional[str]:
        """Get current selected user ID"""
        choice = self.user_combobox.get()
        if choice in self.staff_data:
            return str(self.staff_data[choice]['id'])
        return None
    
    def get_current_username(self) -> Optional[str]:
        """Get current selected username"""
        choice = self.user_combobox.get()
        if choice in self.staff_data:
            return self.staff_data[choice]['username']
        return None
    
    def play_sound(self, sound_file: str):
        """Play sound notification"""
        if self.voice_dir is None:
            return
        
        try:
            sound_path = self.voice_dir / sound_file
            if sound_path.exists():
                threading.Thread(
                    target=lambda: pygame.mixer.music.load(str(sound_path)) or pygame.mixer.music.play(),
                    daemon=True
                ).start()
                logger.info(f"Playing sound: {sound_file}")
            else:
                logger.warning(f"Sound file not found: {sound_path}")
        except Exception as e:
            logger.error(f"Error playing sound: {e}")
    
    def check_duplicate_order_on_b2(self, order_id: str) -> bool:
        """Check if order_id already exists in B2 json folder (lightweight check)"""
        if self.b2_uploader is None:
            return False
        
        try:
            # List files in json/ folder with order_id prefix
            if not self.b2_uploader.is_authenticated:
                self.b2_uploader.authenticate()
            
            if self.b2_uploader.bucket:
                # Search for JSON files matching order_id pattern
                file_versions = self.b2_uploader.bucket.ls(
                    folder_to_list='json/',
                    recursive=False
                )
                
                for file_info, _ in file_versions:
                    # Check if filename starts with order_id
                    filename = file_info.file_name.split('/')[-1]
                    if filename.startswith(f"{order_id}_"):
                        logger.info(f"Duplicate order found on B2: {order_id}")
                        return True
            
            return False
        except Exception as e:
            logger.error(f"Error checking duplicate on B2: {e}")
            return False  # On error, allow recording (fail-safe)
    
    def start_camera_preview(self):
        """Start camera preview loop"""
        if self.camera_manager is None:
            return
            
        if self.camera_manager.start_camera(0):
            self.update_preview_running = True
            self.update_preview()
        else:
            self.status_label.configure(text="Không thể mở camera", text_color="red")
    
    def update_preview(self):
        """Update camera preview frame"""
        if not self.update_preview_running or self.camera_manager is None:
            return
        
        # Get frame for recording (unflipped) if recording
        if self.is_recording:
            recording_frame = self.camera_manager.get_frame()
            if recording_frame is not None:
                self.camera_manager.write_frame(recording_frame)
        
        # Get frame for preview (with flip if enabled)
        preview_frame = self.camera_manager.get_frame_for_preview()
        
        if preview_frame is not None:
            # Convert to PhotoImage for display
            frame_rgb = cv2.cvtColor(preview_frame, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(frame_rgb)
            
            # Resize to fit canvas
            img.thumbnail((640, 480), Image.Resampling.LANCZOS)
            
            # Use CTkImage instead of PhotoImage to avoid warning
            ctk_image = ctk.CTkImage(light_image=img, dark_image=img, size=(img.width, img.height))
            self.preview_canvas.configure(image=ctk_image, text="")
        
        # Schedule next update
        self.after(30, self.update_preview)  # ~30 FPS
    
    def toggle_recording(self):
        """Toggle recording on/off"""
        if not self.is_recording:
            self.start_recording()
        else:
            self.stop_recording(auto_mode=False)
    
    def start_recording(self):
        """Start video recording"""
        if self.camera_manager is None:
            self.status_label.configure(text="Camera chưa sẵn sàng", text_color="red")
            return
            
        order_id = self.order_entry.get().strip()
        user_id = self.get_current_user_id()
        
        if not order_id:
            logger.warning("Cannot start recording: No order ID")
            self.status_label.configure(text="Thiếu mã đơn", text_color="red")
            return
        
        if not user_id:
            logger.warning("Cannot start recording: No user selected")
            self.status_label.configure(text="Thiếu người sử dụng", text_color="red")
            return
        
        success, video_path = self.camera_manager.start_recording(order_id)
        
        if success:
            self.is_recording = True
            self.current_video_path = video_path
            self.current_recording_order = order_id
            self.record_button.configure(
                text="⏹ Dừng ghi hình",
                fg_color="#16A34A",
                hover_color="#15803D"
            )
            self.status_label.configure(text=f"Đang ghi: {order_id}", text_color="red")
            
            # Start recording timer
            import time
            self.recording_start_time = time.time()
            self.timer_running = True
            self.update_recording_timer()
            
            # Play start sound immediately
            self.play_sound("1_start_record.mp3")
            logger.info(f"Recording started for order: {order_id}")
            
            # Check for duplicate in background and play warning sound if needed
            def check_dup():
                is_duplicate = self.check_duplicate_order_on_b2(order_id)
                if is_duplicate:
                    self.play_sound("3_dupcode_continue.mp3")
                    logger.warning(f"Duplicate order detected: {order_id} - continuing recording")
            
            threading.Thread(target=check_dup, daemon=True).start()
        else:
            logger.error("Failed to start recording")
            self.status_label.configure(text="Lỗi bắt đầu ghi", text_color="red")
    
    def update_recording_timer(self):
        """Update the recording timer display"""
        if self.timer_running and self.recording_start_time:
            import time
            elapsed = int(time.time() - self.recording_start_time)
            minutes = elapsed // 60
            seconds = elapsed % 60
            self.timer_label.configure(
                text=f"{minutes:02d}:{seconds:02d}",
                text_color="#DC2626"
            )
            # Schedule next update
            self.after(1000, self.update_recording_timer)
    
    def stop_recording(self, auto_mode: bool = False):
        """Stop video recording and upload
        
        Args:
            auto_mode: If True, recording was stopped automatically (for switching)
        """
        if self.camera_manager is None or self.b2_uploader is None:
            return
        
        # Calculate recording duration before stopping
        import time
        recording_duration = 0
        if self.recording_start_time:
            recording_duration = int(time.time() - self.recording_start_time)
        
        # Stop timer
        self.timer_running = False
        self.recording_start_time = None
        self.timer_label.configure(text="00:00", text_color="#666666")
            
        video_path = self.camera_manager.stop_recording()
        
        if video_path:
            self.is_recording = False
            recording_order = self.current_recording_order
            self.current_recording_order = None
            
            self.record_button.configure(
                text="⏺ Bắt đầu ghi hình",
                fg_color="#DC2626",
                hover_color="#991B1B"
            )
            
            if auto_mode:
                self.status_label.configure(text="Đang xử lý...", text_color="orange")
            else:
                self.status_label.configure(text="Đang upload...", text_color="orange")
            
            self.progress_bar.pack(pady=10, padx=20, fill="x")
            self.progress_bar.set(0)
            
            # Upload in background
            order_id = recording_order if recording_order else self.order_entry.get().strip()
            user_id = self.get_current_user_id()
            username = self.get_current_username()
            
            def upload():
                if self.b2_uploader is None or self.api_client is None:
                    return
                
                # Play end sound before upload
                self.play_sound("2_end_record.mp3")
                    
                def progress_callback(bytes_sent, total_bytes):
                    progress = bytes_sent / total_bytes
                    self.after(0, lambda: self.progress_bar.set(progress))
                
                url = self.b2_uploader.upload_with_cleanup(
                    video_path,
                    order_id,
                    progress_callback
                )
                
                if url:
                    # Save metadata JSON locally first
                    json_b2_url = None
                    if username and self.metadata_manager is not None:
                        # Save JSON locally
                        json_saved = self.metadata_manager.save_metadata(
                            order_id=order_id,
                            username=username,
                            video_url=url,
                            user_id=user_id,
                            duration=recording_duration
                        )
                        
                        if json_saved:
                            logger.info(f"Metadata JSON saved locally for order {order_id}")
                            
                            # Find the JSON file that was just created
                            metadata_dir = Path(self.metadata_manager.metadata_dir)
                            json_files = sorted(
                                metadata_dir.glob(f"{order_id}_*.json"),
                                key=lambda x: x.stat().st_mtime,
                                reverse=True
                            )
                            
                            if json_files:
                                latest_json = json_files[0]
                                # Upload JSON to B2
                                json_b2_url = self.b2_uploader.upload_json_metadata(
                                    str(latest_json),
                                    order_id
                                )
                                
                                if json_b2_url:
                                    logger.info(f"Metadata JSON uploaded to B2: {json_b2_url}")
                                    
                                    # Update local JSON with B2 URL (same file)
                                    self.metadata_manager.update_metadata(
                                        order_id=order_id,
                                        json_b2_url=json_b2_url
                                    )
                    
                    # Upload metadata to API (disabled - endpoint not available)
                    # if user_id:
                    #     self.api_client.upload_recording_metadata(
                    #         order_id=order_id,
                    #         user_id=user_id,
                    #         video_url=url
                    #     )
                    
                    self.after(0, lambda: self.status_label.configure(
                        text=f"✓ Hoàn tất: {order_id}",
                        text_color="green"
                    ))
                    
                    # Auto-delete local video if enabled
                    if self.auto_delete_var.get():
                        try:
                            if os.path.exists(video_path):
                                os.remove(video_path)
                                logger.info(f"Deleted local video: {video_path}")
                        except Exception as e:
                            logger.error(f"Failed to delete local video: {e}")
                else:
                    self.after(0, lambda: self.status_label.configure(
                        text=f"✗ Lỗi upload: {order_id}",
                        text_color="red"
                    ))
                    
                    # Only show error popup if not auto mode
                    if not auto_mode:
                        self.after(0, lambda: messagebox.showerror(
                            "Lỗi",
                            "Không thể upload video"
                        ))
                
                self.after(0, lambda: self.progress_bar.pack_forget())
            
            threading.Thread(target=upload, daemon=True).start()
    
    def _check_for_updates_background(self):
        """Check for updates in background thread"""
        def check_updates():
            try:
                update_info = self.updater.check_for_updates()
                if update_info:
                    # Show update notification in main thread
                    self.after(0, lambda: self._show_update_dialog(update_info))
            except Exception as e:
                logger.error(f"Update check failed: {e}")
        
        threading.Thread(target=check_updates, daemon=True).start()
    
    def _show_update_dialog(self, update_info: dict):
        """Show update available dialog"""
        version = update_info['version']
        size_mb = update_info.get('size_bytes', 0) / 1024 / 1024
        
        message = f"""Phiên bản mới có sẵn: v{version}

Kích thước: {size_mb:.1f} MB

Bạn có muốn tải về phiên bản mới không?

Lưu ý: Ứng dụng sẽ tải file .exe mới vào thư mục Temp và mở Explorer để bạn thay thế file cũ."""
        
        result = messagebox.askyesno(
            "Cập nhật có sẵn",
            message,
            icon='info'
        )
        
        if result:
            self._download_and_apply_update(update_info)
    
    def _download_and_apply_update(self, update_info: dict):
        """Download and apply update with progress"""
        download_url = update_info['download_url']
        
        # Create progress dialog
        progress_window = ctk.CTkToplevel(self)
        progress_window.title("Đang tải cập nhật...")
        progress_window.geometry("400x150")
        progress_window.transient(self)
        progress_window.grab_set()
        
        # Center window
        progress_window.update_idletasks()
        x = (progress_window.winfo_screenwidth() // 2) - (400 // 2)
        y = (progress_window.winfo_screenheight() // 2) - (150 // 2)
        progress_window.geometry(f"400x150+{x}+{y}")
        
        label = ctk.CTkLabel(
            progress_window,
            text="Đang tải phiên bản mới...",
            font=ctk.CTkFont(size=14)
        )
        label.pack(pady=20)
        
        progress_bar = ctk.CTkProgressBar(progress_window, width=350)
        progress_bar.pack(pady=10)
        progress_bar.set(0)
        
        status_label = ctk.CTkLabel(
            progress_window,
            text="0%",
            font=ctk.CTkFont(size=12)
        )
        status_label.pack(pady=5)
        
        def progress_callback(downloaded, total):
            if total > 0:
                progress = downloaded / total
                progress_bar.set(progress)
                status_label.configure(text=f"{int(progress * 100)}% ({downloaded / 1024 / 1024:.1f} / {total / 1024 / 1024:.1f} MB)")
        
        def download_thread():
            try:
                update_file = self.updater.download_update(download_url, progress_callback)
                
                if update_file:
                    # Apply update (opens Explorer)
                    self.updater.apply_update(update_file)
                    
                    # Close progress window and show success
                    self.after(0, lambda: progress_window.destroy())
                    self.after(0, lambda: messagebox.showinfo(
                        "Tải về thành công",
                        f"File cập nhật đã được tải về:\n{update_file}\n\nVui lòng:\n1. Đóng ứng dụng hiện tại\n2. Thay thế file LemiexRecordApp.exe cũ bằng file mới\n3. Khởi động lại ứng dụng"
                    ))
                else:
                    self.after(0, lambda: progress_window.destroy())
                    self.after(0, lambda: messagebox.showerror(
                        "Lỗi",
                        "Không thể tải về bản cập nhật. Vui lòng thử lại sau."
                    ))
                    
            except Exception as e:
                logger.error(f"Download failed: {e}")
                self.after(0, lambda: progress_window.destroy())
                self.after(0, lambda: messagebox.showerror(
                    "Lỗi",
                    f"Không thể tải về bản cập nhật:\n{str(e)}"
                ))
        
        threading.Thread(target=download_thread, daemon=True).start()
    
    def on_closing(self):
        """Cleanup on window close"""
        logger.info("Application closing")
        self.update_preview_running = False
        if self.camera_manager is not None:
            self.camera_manager.stop_camera()
        if self.scanner_manager is not None:
            self.scanner_manager.disconnect()
        self.destroy()


def run_app():
    """Run the application"""
    app = MainWindow()
    app.protocol("WM_DELETE_WINDOW", app.on_closing)
    app.mainloop()


if __name__ == "__main__":
    run_app()
