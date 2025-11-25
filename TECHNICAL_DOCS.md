# Lemiex Record App - Technical Documentation

## Architecture Overview

### Technology Stack

**Frontend/GUI:**
- CustomTkinter (Modern Tkinter framework)
- PIL/Pillow (Image processing)

**Video Processing:**
- OpenCV (Camera capture, video encoding)
- NumPy (Array operations)

**Hardware Integration:**
- PySerial (Barcode scanner communication)

**Cloud Storage:**
- B2SDK (Backblaze B2 integration)

**API Communication:**
- Requests (HTTP client)

**Configuration:**
- PyYAML (Config file parsing)
- python-dotenv (Environment variables)

### Module Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Main Window (GUI)                     │
│                  (main_window.py)                        │
│  ┌─────────────┐ ┌──────────────┐ ┌─────────────────┐  │
│  │   Camera    │ │   Scanner    │ │   User Input    │  │
│  │   Preview   │ │  Dropdown    │ │   & Controls    │  │
│  └─────────────┘ └──────────────┘ └─────────────────┘  │
└────────────┬──────────────┬──────────────┬──────────────┘
             │              │              │
    ┌────────▼────────┐ ┌──▼────────────┐ │
    │ CameraManager   │ │ ScannerManager│ │
    │  - list cameras │ │  - list ports │ │
    │  - preview      │ │  - read data  │ │
    │  - record       │ │  - parse QR   │ │
    │  - timestamp    │ │  - listen     │ │
    └────────┬────────┘ └───────────────┘ │
             │                             │
             │ video file              ┌───▼──────────┐
             └─────────────────────────► B2Uploader   │
                                       │  - auth      │
                                       │  - upload    │
                                       │  - progress  │
                                       └───┬──────────┘
                                           │
                                           │ metadata
                                       ┌───▼──────────┐
                                       │ APIClient    │
                                       │  - user info │
                                       │  - validate  │
                                       │  - metadata  │
                                       └──────────────┘

┌──────────────────────────────────────────────────────────┐
│                    Logger Module                         │
│         (Logs all operations to files)                   │
└──────────────────────────────────────────────────────────┘
```

## File Structure

```
Lemiex-record-app/
│
├── main.py                    # Entry point
├── requirements.txt           # Python dependencies
├── setup.bat                  # Windows setup script
├── run.bat                    # Windows run script
├── .env.example              # Environment template
├── .env                      # Credentials (not in git)
├── .gitignore               # Git ignore rules
├── README.md                # Project overview
├── INSTALL.md              # Installation guide
├── USER_MANUAL.md          # User guide
│
├── config/
│   └── config.yaml          # Application configuration
│
├── src/
│   ├── __init__.py         # Package marker
│   ├── logger.py           # Logging system
│   ├── camera_manager.py  # Camera operations
│   ├── scanner_manager.py # Scanner operations
│   ├── b2_uploader.py     # Backblaze upload
│   ├── api_client.py      # API communication
│   └── main_window.py     # GUI application
│
├── logs/
│   └── app.log             # Application logs
│
└── temp_videos/            # Temporary video storage
    └── {order_id}_{timestamp}.mp4
```

## Data Flow

### 1. Application Startup
```
main.py → MainWindow.__init__()
    ├── Load config.yaml
    ├── Initialize CameraManager
    ├── Initialize ScannerManager
    ├── Initialize B2Uploader
    ├── Initialize APIClient
    └── Setup GUI
```

### 2. Camera Selection Flow
```
User selects camera
    → MainWindow.on_camera_changed()
        → CameraManager.stop_camera()
        → CameraManager.start_camera(index)
            → OpenCV VideoCapture init
            → Set resolution & FPS
            → Start preview loop
```

### 3. Scanner Connection Flow
```
User selects COM port
    → MainWindow.on_scanner_changed()
        → ScannerManager.connect(port)
            → PySerial Serial init
            → ScannerManager.start_listening()
                → Background thread reads data
                → Parse QR URL → Extract order ID
                → Callback: MainWindow.on_barcode_scanned()
                    → Fill order_entry textbox
```

### 4. Recording Flow
```
User clicks "Bắt đầu ghi hình"
    → MainWindow.start_recording()
        → Validate order_id & user_id
        → CameraManager.start_recording(order_id)
            → Generate filename
            → Create VideoWriter
            → Set recording resolution
            → is_recording = True
        → Preview loop writes frames
            → CameraManager.write_frame()

User clicks "Dừng ghi hình"
    → MainWindow.stop_recording()
        → CameraManager.stop_recording()
            → Close VideoWriter
            → Return video path
        → Background thread: Upload
            → B2Uploader.upload_with_cleanup()
                → B2Uploader.authenticate()
                → B2Uploader.upload_video()
                    → Progress callback updates UI
                    → Return public URL
                → APIClient.upload_recording_metadata()
                → Delete local file (optional)
            → Show success message
```

### 5. User Info Flow
```
User enters user_id
    → User clicks "Lấy thông tin"
        → MainWindow.get_user_info()
            → Background thread
                → APIClient.get_user_info(user_id)
                    → HTTP GET to /users/{user_id}
                    → Parse response
                → Update UI with user name
```

## Configuration System

### config.yaml
```yaml
app:          # Application settings
camera:       # Camera/video settings
scanner:      # Scanner/serial settings
api:          # API endpoints
backblaze:    # B2 storage settings
logging:      # Log configuration
storage:      # Local storage settings
```

### .env
```
B2_APPLICATION_KEY_ID=xxx    # Backblaze credentials
B2_APPLICATION_KEY=xxx
API_KEY=xxx                   # API credentials
API_SECRET=xxx
```

## Threading Model

### Main Thread (GUI)
- CustomTkinter event loop
- UI updates
- Preview frame rendering

### Background Threads

**1. Scanner Listen Thread**
- Continuously reads from serial port
- Parses incoming data
- Calls callback on main thread

**2. Upload Thread**
- Spawned after recording stops
- Uploads video to B2
- Updates progress bar via `after()`
- Shows completion dialog

**3. API Fetch Thread**
- Spawned for user info retrieval
- Prevents UI blocking
- Updates UI via `after()`

## Error Handling Strategy

### Logger Integration
All modules use centralized logger:
```python
from .logger import setup_logger
logger = setup_logger("ModuleName")
```

### Exception Handling Levels

**1. Critical (Application Level)**
- Logged with traceback
- User notified via messagebox
- Application may exit

**2. Error (Operation Level)**
- Logged with context
- User notified
- Operation cancelled, app continues

**3. Warning (Recoverable)**
- Logged
- May notify user
- Operation continues with fallback

**4. Info/Debug**
- Logged for troubleshooting
- Not shown to user

### Log Rotation
- Max file size: 10MB
- Keep 5 backup files
- Format: timestamp - module - level - message

## API Integration

### Expected Endpoints

**GET /users/{user_id}**
```json
{
  "user_id": "12345",
  "name": "John Doe",
  "email": "john@example.com"
}
```

**GET /orders/{order_id}**
```json
{
  "order_id": "6079",
  "status": "pending",
  "customer": "..."
}
```

**POST /recordings/metadata**
```json
{
  "order_id": "6079",
  "user_id": "12345",
  "video_url": "https://...",
  "recorded_at": "2025-11-22T10:30:00",
  "duration": 120.5,
  "file_size": 52428800
}
```

## Video Encoding Specifications

### Preview Mode
- Resolution: 640x480 (configurable)
- FPS: 30
- Format: Display only, not saved

### Recording Mode
- Resolution: 1920x1080 (configurable)
- FPS: 30
- Codec: MP4V (or H264 if available)
- Container: MP4
- Timestamp: Burned into video
- Naming: `{order_id}_{timestamp}.mp4`

## Backblaze B2 Integration

### Folder Structure
```
bucket: lemiex-recordings/
  └── recordings/
      └── 2025/
          └── 11/
              └── 22/
                  ├── 6079_20251122_103000.mp4
                  ├── 6080_20251122_104500.mp4
                  └── ...
```

### Upload Process
1. Authenticate with application key
2. Get bucket reference
3. Generate B2 file path with date prefix
4. Upload with progress listener
5. Get public download URL
6. Return URL to application

### File Metadata
```json
{
  "order_id": "6079",
  "upload_date": "2025-11-22T10:30:00"
}
```

## Security Considerations

### Credentials Storage
- ✅ Stored in `.env` (not in git)
- ✅ Loaded at runtime only
- ✅ Never logged or displayed

### API Communication
- ✅ HTTPS endpoints required
- ✅ API key in headers
- ✅ Timeout protection (10s default)

### Video Storage
- ✅ Temporary local storage
- ✅ Optional auto-delete after upload
- ✅ B2 bucket with access controls

## Performance Optimization

### Camera Preview
- 30ms update interval (~33 FPS)
- Frame resize for display
- Efficient PIL/ImageTk conversion

### Video Recording
- Native OpenCV encoding
- No frame buffering overhead
- Direct write to disk

### Upload
- Chunked upload (10MB chunks)
- Progress callback every chunk
- Retry logic for failures

## Extension Points

### Adding New Camera Source
Extend `CameraManager`:
```python
def add_custom_source(self, url):
    self.cap = cv2.VideoCapture(url)
```

### Custom QR Pattern
Edit `config.yaml`:
```yaml
scanner:
  qr_url_pattern: "your_regex_here"
```

### Additional API Endpoints
Extend `APIClient`:
```python
def custom_endpoint(self, data):
    return self._make_request('POST', '/custom', data)
```

### GUI Customization
Edit `main_window.py`:
- Colors: Change theme colors
- Layout: Modify grid/pack layout
- Widgets: Add new CTk widgets

## Testing Strategy

### Manual Testing Checklist
- [ ] Camera detection and switching
- [ ] Scanner connection and QR parsing
- [ ] Recording start/stop
- [ ] Video encoding quality
- [ ] Upload progress and completion
- [ ] API communication
- [ ] Error handling (no camera, no scanner, no internet)
- [ ] Log file generation

### Module Testing
Each module has `if __name__ == "__main__"` block:
```bash
python src/camera_manager.py    # Test camera listing
python src/scanner_manager.py   # Test scanner detection
python src/b2_uploader.py       # Test B2 auth
python src/api_client.py        # Test API ping
```

## Deployment

### Standalone Executable
```bash
pyinstaller --name "LemiexRecordApp" ^
            --windowed ^
            --onefile ^
            --add-data "config;config" ^
            main.py
```

### Distribution Package
```
dist/
  ├── LemiexRecordApp.exe
  ├── config/
  │   └── config.yaml
  ├── .env.example
  ├── README.md
  └── USER_MANUAL.md
```

### Requirements
- Windows 10/11
- Python runtime (embedded if using PyInstaller)
- Webcam drivers
- Serial port drivers (for scanner)

## Future Enhancements

### Planned Features
- [ ] Multi-language support (English/Vietnamese)
- [ ] Keyboard shortcuts
- [ ] Video preview playback before upload
- [ ] Batch recording queue
- [ ] Cloud backup of configuration
- [ ] Auto-update mechanism
- [ ] Recording history viewer
- [ ] Export logs to CSV
- [ ] Email notifications
- [ ] Webhook support

### Performance Improvements
- [ ] Hardware acceleration for encoding (NVENC, QSV)
- [ ] Parallel uploads for multiple videos
- [ ] Resume failed uploads
- [ ] Compress videos before upload

### UI Enhancements
- [ ] Dark/Light theme toggle
- [ ] Customizable layout
- [ ] Minimized system tray mode
- [ ] Status bar with system info

## Maintenance

### Regular Tasks
- Monitor log files size
- Clean up temp_videos folder
- Update dependencies
- Review B2 storage usage
- Check API rate limits

### Updating Dependencies
```bash
pip list --outdated
pip install --upgrade <package>
pip freeze > requirements.txt
```

### Backup Important Data
- `.env` file (credentials)
- `config/config.yaml` (custom settings)
- `logs/` (if needed for auditing)

## Support & Resources

### Documentation
- README.md: Overview
- INSTALL.md: Installation steps
- USER_MANUAL.md: User guide
- TECHNICAL_DOCS.md: This file

### External Resources
- OpenCV docs: https://docs.opencv.org/
- CustomTkinter: https://customtkinter.tomschimansky.com/
- Backblaze B2: https://www.backblaze.com/b2/docs/
- PySerial: https://pythonhosted.org/pyserial/

### Troubleshooting
1. Check logs: `logs/app.log`
2. Test modules individually
3. Verify configuration files
4. Check network connectivity
5. Review system requirements
