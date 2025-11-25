"""
Main Window Module - GUI application using CustomTkinter
Provides interface for camera preview, scanner input, and recording control
"""

import customtkinter as ctk
from tkinter import messagebox
import cv2
from PIL import Image, ImageTk
import threading
from pathlib import Path
from typing import Optional
import yaml

from .camera_manager import CameraManager
from .scanner_manager import ScannerManager
from .b2_uploader import B2Uploader
from .api_client import APIClient
from .metadata_manager import MetadataManager
from .logger import setup_logger

logger = setup_logger("MainWindow")


class MainWindow(ctk.CTk):
    """Main application window"""
    
    def __init__(self):
        super().__init__()
        
        # Load configuration
        config_path = Path(__file__).parent.parent / "config" / "config.yaml"
        with open(str(config_path), 'r', encoding='utf-8') as f:
            self.config = yaml.safe_load(f)
        
        app_config = self.config['app']
        
        # Configure window
        self.title(app_config['name'])
        self.geometry(f"{app_config['window_width']}x{app_config['window_height']}")
        
        # Set theme
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
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
        
        logger.info("All components initialized")
    
    def setup_ui(self):
        """Setup user interface"""
        
        # Configure grid
        self.grid_columnconfigure(0, weight=2)
        self.grid_columnconfigure(1, weight=1)
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
            height=480
        )
        self.preview_canvas.pack(pady=10, padx=10)
        
        # Right panel - Controls
        self.right_frame = ctk.CTkFrame(self, corner_radius=10)
        self.right_frame.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
        
        # Create scrollable frame for controls
        self.scrollable_frame = ctk.CTkScrollableFrame(
            self.right_frame,
            corner_radius=0
        )
        self.scrollable_frame.pack(fill="both", expand=True, padx=0, pady=0)
        
        # Title
        title_label = ctk.CTkLabel(
            self.scrollable_frame,
            text="Äiá»u khiá»ƒn",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        title_label.pack(pady=(20, 10))
        
        # Camera selection
        camera_label = ctk.CTkLabel(self.scrollable_frame, text="Chá»n Camera:", anchor="w")
        camera_label.pack(pady=(10, 5), padx=20, fill="x")
        
        self.camera_combobox = ctk.CTkComboBox(
            self.scrollable_frame,
            values=["Äang táº£i..."],
            command=self.on_camera_changed
        )
        self.camera_combobox.pack(pady=5, padx=20, fill="x")
        
        # Refresh camera button
        refresh_cam_btn = ctk.CTkButton(
            self.scrollable_frame,
            text="ðŸ”„ LÃ m má»›i",
            command=self.refresh_camera_list,
            width=100
        )
        refresh_cam_btn.pack(pady=5)

        # Camera Settings Section
        settings_label = ctk.CTkLabel(
            self.scrollable_frame,
            text="CÃ i Ä‘áº·t Camera:",
            font=ctk.CTkFont(size=14, weight="bold"),
            anchor="w"
        )
        settings_label.pack(pady=(20, 10), padx=20, fill="x")
        
        # Brightness
        brightness_label = ctk.CTkLabel(self.scrollable_frame, text="Äá»™ sÃ¡ng:", anchor="w")
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
            text="Láº­t camera (mirror)",
            command=self.on_flip_changed
        )
        self.flip_checkbox.pack(pady=(10, 5), padx=20, fill="x")
        # Flip state will be set when manager loads
        
        # Scanner selection
        scanner_label = ctk.CTkLabel(self.scrollable_frame, text="Chá»n Scanner:", anchor="w")
        scanner_label.pack(pady=(20, 5), padx=20, fill="x")
        
        self.scanner_combobox = ctk.CTkComboBox(
            self.scrollable_frame,
            values=["Äang táº£i..."],
            command=self.on_scanner_changed
        )
        self.scanner_combobox.pack(pady=5, padx=20, fill="x")
        
        # Refresh scanner button
        refresh_scanner_btn = ctk.CTkButton(
            self.scrollable_frame,
            text="ðŸ”„ LÃ m má»›i",
            command=self.refresh_scanner_list,
            width=100
        )
        refresh_scanner_btn.pack(pady=5)
        
        # Order ID input
        order_label = ctk.CTkLabel(self.scrollable_frame, text="MÃ£ Ä‘Æ¡n:", anchor="w")
        order_label.pack(pady=(20, 5), padx=20, fill="x")
        
        self.order_entry = ctk.CTkEntry(
            self.scrollable_frame,
            placeholder_text="Nháº­p hoáº·c scan mÃ£ Ä‘Æ¡n"
        )
        self.order_entry.pack(pady=5, padx=20, fill="x")
        
        # User selection
        user_label = ctk.CTkLabel(self.scrollable_frame, text="NgÆ°á»i sá»­ dá»¥ng:", anchor="w")
        user_label.pack(pady=(20, 5), padx=20, fill="x")
        
        self.user_combobox = ctk.CTkComboBox(
            self.scrollable_frame,
            values=["Äang táº£i..."],
            command=self.on_user_changed
        )
        self.user_combobox.pack(pady=5, padx=20, fill="x")
        
        # Refresh staff button
        refresh_staff_btn = ctk.CTkButton(
            self.scrollable_frame,
            text="ðŸ”„ LÃ m má»›i",
            command=self.refresh_staff_list,
            width=100
        )
        refresh_staff_btn.pack(pady=5)
        
        # Record button
        self.record_button = ctk.CTkButton(
            self.scrollable_frame,
            text="âº Báº¯t Ä‘áº§u ghi hÃ¬nh",
            command=self.toggle_recording,
            height=50,
            font=ctk.CTkFont(size=16, weight="bold"),
            fg_color="#DC2626",
            hover_color="#991B1B"
        )
        self.record_button.pack(pady=(30, 10), padx=20, fill="x")
        
        # Status label
        self.status_label = ctk.CTkLabel(
            self.scrollable_frame,
            text="Sáºµn sÃ ng",
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
            self.camera_combobox.configure(values=["KhÃ´ng tÃ¬m tháº¥y camera"])
            self.camera_combobox.set("KhÃ´ng tÃ¬m tháº¥y camera")
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
            self.scanner_combobox.configure(values=["KhÃ´ng tÃ¬m tháº¥y cá»•ng COM"])
            self.scanner_combobox.set("KhÃ´ng tÃ¬m tháº¥y cá»•ng COM")
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
            self.status_label.configure(text="Äang chuyá»ƒn camera...", text_color="orange")
            
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
                        self.status_label.configure(text=f"ÄÃ£ chuyá»ƒn: {choice}", text_color="green")
                    else:
                        self.status_label.configure(text="Lá»—i chuyá»ƒn camera", text_color="red")
                
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
                self.status_label.configure(text=f"Scanner káº¿t ná»‘i: {port}", text_color="green")
                # Start listening for scans
                self.scanner_manager.start_listening(self.on_barcode_scanned)
            else:
                self.status_label.configure(text="Lá»—i káº¿t ná»‘i scanner", text_color="red")
    
    def on_barcode_scanned(self, order_id: str):
        """Handle barcode scan event"""
        logger.info(f"Barcode scanned: {order_id}")
        
        current_order = self.order_entry.get().strip()
        
        # Case 1: Not recording - start recording with new order
        if not self.is_recording:
            self.order_entry.delete(0, 'end')
            self.order_entry.insert(0, order_id)
            self.status_label.configure(text=f"ÄÃ£ scan: {order_id}", text_color="blue")
            # Auto start recording
            self.after(100, self.start_recording)
        
        # Case 2: Recording same order - stop recording
        elif current_order == order_id:
            logger.info(f"Scanned same order {order_id} - stopping recording")
            self.status_label.configure(text=f"Scan láº¡i mÃ£ {order_id} - Dá»«ng ghi", text_color="orange")
            self.stop_recording(auto_mode=False)
        
        # Case 3: Recording different order - stop current, start new
        else:
            logger.info(f"Scanned different order {order_id} - switching recording")
            self.status_label.configure(text=f"Chuyá»ƒn sang mÃ£ {order_id}", text_color="orange")
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
                            text=f"ÄÃ£ táº£i {len(staff_names)} nhÃ¢n viÃªn",
                            text_color="green"
                        )
                
                self.after(0, update_ui)
            else:
                def update_ui_error():
                    self.user_combobox.configure(values=["KhÃ´ng táº£i Ä‘Æ°á»£c danh sÃ¡ch"])
                    self.user_combobox.set("KhÃ´ng táº£i Ä‘Æ°á»£c danh sÃ¡ch")
                    self.status_label.configure(
                        text="Lá»—i táº£i danh sÃ¡ch nhÃ¢n viÃªn",
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
                text=f"ÄÃ£ chá»n: {staff['full_name']}",
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
    
    def start_camera_preview(self):
        """Start camera preview loop"""
        if self.camera_manager is None:
            return
            
        if self.camera_manager.start_camera(0):
            self.update_preview_running = True
            self.update_preview()
        else:
            self.status_label.configure(text="KhÃ´ng thá»ƒ má»Ÿ camera", text_color="red")
    
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
            self.status_label.configure(text="Camera chÆ°a sáºµn sÃ ng", text_color="red")
            return
            
        order_id = self.order_entry.get().strip()
        user_id = self.get_current_user_id()
        
        if not order_id:
            logger.warning("Cannot start recording: No order ID")
            self.status_label.configure(text="Thiáº¿u mÃ£ Ä‘Æ¡n", text_color="red")
            return
        
        if not user_id:
            logger.warning("Cannot start recording: No user selected")
            self.status_label.configure(text="Thiáº¿u ngÆ°á»i sá»­ dá»¥ng", text_color="red")
            return
        
        success, video_path = self.camera_manager.start_recording(order_id)
        
        if success:
            self.is_recording = True
            self.current_video_path = video_path
            self.current_recording_order = order_id
            self.record_button.configure(
                text="â¹ Dá»«ng ghi hÃ¬nh",
                fg_color="#16A34A",
                hover_color="#15803D"
            )
            self.status_label.configure(text=f"Äang ghi: {order_id}", text_color="red")
            logger.info(f"Recording started for order: {order_id}")
        else:
            logger.error("Failed to start recording")
            self.status_label.configure(text="Lá»—i báº¯t Ä‘áº§u ghi", text_color="red")
    
    def stop_recording(self, auto_mode: bool = False):
        """Stop video recording and upload
        
        Args:
            auto_mode: If True, recording was stopped automatically (for switching)
        """
        if self.camera_manager is None or self.b2_uploader is None:
            return
            
        video_path = self.camera_manager.stop_recording()
        
        if video_path:
            self.is_recording = False
            recording_order = self.current_recording_order
            self.current_recording_order = None
            
            self.record_button.configure(
                text="âº Báº¯t Ä‘áº§u ghi hÃ¬nh",
                fg_color="#DC2626",
                hover_color="#991B1B"
            )
            
            if auto_mode:
                self.status_label.configure(text="Äang xá»­ lÃ½...", text_color="orange")
            else:
                self.status_label.configure(text="Äang upload...", text_color="orange")
            
            self.progress_bar.pack(pady=10, padx=20, fill="x")
            self.progress_bar.set(0)
            
            # Upload in background
            order_id = recording_order if recording_order else self.order_entry.get().strip()
            user_id = self.get_current_user_id()
            username = self.get_current_username()
            
            def upload():
                if self.b2_uploader is None or self.api_client is None:
                    return
                    
                def progress_callback(bytes_sent, total_bytes):
                    progress = bytes_sent / total_bytes
                    self.after(0, lambda: self.progress_bar.set(progress))
                
                url = self.b2_uploader.upload_with_cleanup(
                    video_path,
                    order_id,
                    progress_callback
                )
                
                if url:
                    # Upload metadata
                    if user_id:
                        self.api_client.upload_recording_metadata(
                            order_id=order_id,
                            user_id=user_id,
                            video_url=url
                        )
                    
                    self.after(0, lambda: self.status_label.configure(
                        text=f"âœ“ HoÃ n táº¥t: {order_id}",
                        text_color="green"
                    ))
                    
                    # Only show popup if not auto mode
                    if not auto_mode:
                        self.after(0, lambda: messagebox.showinfo(
                            "ThÃ nh cÃ´ng",
                            f"Video Ä‘Ã£ Ä‘Æ°á»£c upload:\n{url}"
                        ))
                else:
                    self.after(0, lambda: self.status_label.configure(
                        text=f"âœ— Lá»—i upload: {order_id}",
                        text_color="red"
                    ))
                    
                    # Only show error popup if not auto mode
                    if not auto_mode:
                        self.after(0, lambda: messagebox.showerror(
                            "Lá»—i",
                            "KhÃ´ng thá»ƒ upload video"
                        ))
                
                self.after(0, lambda: self.progress_bar.pack_forget())
            
            threading.Thread(target=upload, daemon=True).start()
    
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
