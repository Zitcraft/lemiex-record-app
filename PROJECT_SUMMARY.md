# 🎥 Lemiex Record App - Project Summary

## ✅ Implementation Complete

Ứng dụng ghi hình webcam với tích hợp barcode scanner và upload tự động lên Backblaze B2 đã được xây dựng hoàn chỉnh.

---

## 📁 Project Structure

```
Lemiex-record-app/
│
├── 📄 main.py                      # Entry point của ứng dụng
├── 📄 requirements.txt             # Python dependencies (13 packages)
├── 📄 setup.bat                    # Script cài đặt tự động (Windows)
├── 📄 run.bat                      # Script chạy ứng dụng nhanh
│
├── 📁 config/
│   └── config.yaml                 # Cấu hình đầy đủ (camera, scanner, API, B2)
│
├── 📁 src/                         # Source code chính
│   ├── logger.py                   # (217 lines) Logging system với rotation
│   ├── camera_manager.py           # (368 lines) Quản lý camera & recording
│   ├── scanner_manager.py          # (312 lines) Quản lý barcode scanner
│   ├── b2_uploader.py              # (233 lines) Upload lên Backblaze B2
│   ├── api_client.py               # (251 lines) Kết nối API backend
│   ├── main_window.py              # (502 lines) GUI với CustomTkinter
│   └── __init__.py                 # Package marker
│
├── 📁 logs/                        # Log files
│   └── app.log                     # Logs được tạo tự động
│
├── 📁 temp_videos/                 # Video tạm thời trước khi upload
│
├── 📄 .env.example                 # Template cho credentials
├── 📄 .gitignore                   # Git ignore rules
│
└── 📚 Documentation/
    ├── README.md                   # Tổng quan dự án
    ├── INSTALL.md                  # Hướng dẫn cài đặt chi tiết
    ├── USER_MANUAL.md              # Hướng dẫn sử dụng
    └── TECHNICAL_DOCS.md           # Tài liệu kỹ thuật

Total: 1,883+ lines of code
```

---

## 🎯 Core Features Implemented

### ✅ 1. Camera Management
- **Tự động quét** và liệt kê tất cả cameras có sẵn
- **Preview thời gian thực** với resolution 640x480
- **Recording chất lượng cao** (1920x1080 @ 30fps)
- **Timestamp overlay** tự động trên video
- **Chuyển đổi camera** mượt mà không cần restart

### ✅ 2. Barcode Scanner Integration
- **Tự động phát hiện** cổng COM của scanner
- **Background listening** không block UI
- **Parse QR code** từ URL `https://lemiex.us/qr/6079` → `6079`
- **Hỗ trợ nhiều format**: URL hoặc số trực tiếp
- **Regex pattern** có thể tùy chỉnh trong config

### ✅ 3. Video Recording
- **Codec MP4V** (H264 nếu có sẵn)
- **Filename format**: `{order_id}_{timestamp}.mp4`
- **Lưu tạm local** trong `temp_videos/`
- **Auto delete** sau khi upload (optional)

### ✅ 4. Backblaze B2 Upload
- **Tự động authenticate** với application key
- **Upload chunked** (10MB chunks) hiệu quả
- **Progress tracking** real-time với progress bar
- **Retry logic** khi upload thất bại
- **Folder organization** theo ngày: `recordings/2025/11/22/`
- **Public URL** được trả về sau upload

### ✅ 5. API Integration
- **Get user info** từ backend API
- **Validate order ID** trước khi recording
- **Upload metadata** sau khi hoàn tất
- **Timeout protection** (10s default)
- **Error handling** graceful

### ✅ 6. Modern GUI
- **CustomTkinter** - Modern, clean interface
- **Dark theme** mặc định
- **Vietnamese UI** hoàn chỉnh
- **Responsive layout** với grid system
- **Status indicators** với màu sắc rõ ràng
- **Progress bar** cho upload

### ✅ 7. Logging System
- **Rotating file handler** (10MB, 5 backups)
- **Multi-level logging** (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- **Centralized logger** cho tất cả modules
- **Formatted logs** với timestamp
- **Console + File** output

### ✅ 8. Configuration Management
- **YAML config** dễ đọc và chỉnh sửa
- **Environment variables** cho credentials
- **Modular settings** cho từng component
- **.env.example** template có sẵn

---

## 🛠️ Technologies Used

### Core Libraries
| Library | Version | Purpose |
|---------|---------|---------|
| customtkinter | 5.2.2 | Modern GUI framework |
| opencv-python | 4.9.0.80 | Camera & video processing |
| pyserial | 3.5 | Scanner communication |
| b2sdk | 2.2.0 | Backblaze B2 integration |
| requests | 2.31.0 | API communication |
| PyYAML | 6.0.1 | Configuration parsing |
| python-dotenv | 1.0.1 | Environment variables |
| Pillow | 10.3.0 | Image processing |
| numpy | 1.26.4 | Array operations |

### Python Version
- **Minimum**: Python 3.8+
- **Recommended**: Python 3.10+

---

## 📋 Quick Start Guide

### 1. Cài đặt (Windows)
```bash
# Option A: Tự động
setup.bat

# Option B: Thủ công
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
```

### 2. Cấu hình
```bash
# Edit .env với credentials
B2_APPLICATION_KEY_ID=your_key_id
B2_APPLICATION_KEY=your_app_key

# Edit config/config.yaml nếu cần
```

### 3. Chạy ứng dụng
```bash
# Option A
run.bat

# Option B
venv\Scripts\activate
python main.py
```

---

## 🎮 User Workflow

```
1. Khởi động app
   ↓
2. Chọn camera từ dropdown
   ↓
3. Kết nối scanner (auto-detect hoặc chọn cổng COM)
   ↓
4. Nhập User ID → Click "Lấy thông tin"
   ↓
5. Scan QR code hoặc nhập mã đơn thủ công
   ↓
6. Click "⏺ Bắt đầu ghi hình"
   ↓
7. Recording với timestamp overlay
   ↓
8. Click "⏹ Dừng ghi hình"
   ↓
9. Auto upload lên B2 với progress bar
   ↓
10. Metadata được gửi lên API
    ↓
11. Hiển thị public URL video
```

---

## 🏗️ Architecture Highlights

### Modular Design
- **6 independent modules** dễ maintain và extend
- **Single Responsibility Principle** cho mỗi module
- **Loose coupling** giữa các components
- **Centralized configuration** và logging

### Threading Model
- **Main thread**: GUI event loop
- **Scanner thread**: Background listening
- **Upload thread**: Non-blocking upload
- **API thread**: Async data fetching

### Error Handling
- **Try-catch blocks** ở mọi critical operations
- **Graceful degradation** khi có lỗi
- **User-friendly error messages**
- **Detailed logging** cho debugging

### Performance
- **30 FPS** camera preview
- **Efficient frame processing** với NumPy
- **Chunked upload** giảm memory usage
- **Lazy loading** của resources

---

## 📊 Code Statistics

```
Total Lines of Code:     1,883+
Total Files:             17
Core Modules:            6
Documentation Pages:     4
Configuration Files:     2
Helper Scripts:          2
```

### Module Breakdown
```
main_window.py      502 lines   (GUI logic)
camera_manager.py   368 lines   (Camera operations)
scanner_manager.py  312 lines   (Scanner operations)
api_client.py       251 lines   (API communication)
b2_uploader.py      233 lines   (B2 upload)
logger.py           217 lines   (Logging system)
```

---

## 🔒 Security Features

- ✅ Credentials stored in `.env` (not in git)
- ✅ `.env.example` template provided
- ✅ HTTPS required for API endpoints
- ✅ API key authentication
- ✅ Timeout protection on all network calls
- ✅ Input validation before recording
- ✅ Safe file path handling

---

## 📱 System Requirements

### Minimum
- Windows 10/11
- Python 3.8+
- 2GB RAM
- Webcam
- USB Barcode Scanner
- Internet connection

### Recommended
- Windows 11
- Python 3.10+
- 4GB RAM
- HD Webcam (1080p)
- USB-Serial Scanner (9600 baud)
- Stable internet (5+ Mbps upload)

---

## 🚀 Deployment Options

### Option 1: Python Script
```bash
python main.py
```
**Pros**: Easy to modify, debug
**Cons**: Requires Python installed

### Option 2: Standalone Executable
```bash
pyinstaller --windowed --onefile main.py
```
**Pros**: No Python needed, single .exe
**Cons**: Large file size (~150MB)

### Option 3: Installer Package
Use NSIS or Inno Setup to create installer
**Pros**: Professional, easy distribution
**Cons**: Extra setup required

---

## 📚 Documentation Provided

### 1. README.md
- Project overview
- Features list
- Quick installation
- Basic usage
- License info

### 2. INSTALL.md
- Detailed installation steps
- Troubleshooting guide
- Configuration instructions
- Testing procedures

### 3. USER_MANUAL.md
- Complete user guide
- UI walkthrough
- Step-by-step workflows
- Tips & tricks
- FAQ

### 4. TECHNICAL_DOCS.md
- Architecture overview
- Module descriptions
- Data flow diagrams
- API specifications
- Extension points
- Performance tuning

---

## 🔄 Workflow Examples

### Example 1: Normal Recording
```
User opens app
→ Camera preview starts automatically
→ Scanner auto-connects to COM3
→ User scans QR: "https://lemiex.us/qr/6079"
→ Order ID "6079" fills textbox
→ User enters User ID: "12345"
→ Clicks "Lấy thông tin" → Name appears
→ Clicks "Bắt đầu ghi hình"
→ Records for 2 minutes
→ Clicks "Dừng ghi hình"
→ Progress bar shows upload: 0% → 100%
→ Success popup with video URL
```

### Example 2: Multiple Recordings
```
Recording #1 complete
→ User scans next QR code immediately
→ Order ID auto-updates
→ Clicks record again
→ No need to reload app
```

### Example 3: Error Recovery
```
Upload fails (no internet)
→ Video remains in temp_videos/
→ User fixes internet
→ Can manually upload later
→ Or app retries automatically
```

---

## 🎨 UI Components

### Left Panel - Camera Preview
- Large video preview (640x480)
- Real-time timestamp overlay
- Smooth 30 FPS updates

### Right Panel - Controls
1. **Camera Section**
   - Dropdown với danh sách cameras
   - Refresh button

2. **Scanner Section**
   - Dropdown với danh sách COM ports
   - Refresh button
   - Auto-detect indicator

3. **Order Input**
   - Textbox tự động fill khi scan
   - Supports manual input

4. **User Section**
   - User ID textbox
   - "Lấy thông tin" button
   - User name display

5. **Recording Control**
   - Large record/stop button
   - Color-coded (red/green)
   - Status label
   - Progress bar (when uploading)

---

## 📈 Future Enhancement Ideas

### Phase 2 Features
- [ ] Multi-language support (EN/VI toggle)
- [ ] Recording history viewer
- [ ] Video playback before upload
- [ ] Batch queue for multiple orders
- [ ] Export logs to CSV
- [ ] Email notifications
- [ ] Webhook integration

### Phase 3 Features
- [ ] Cloud config sync
- [ ] Auto-update mechanism
- [ ] Hardware acceleration (NVENC)
- [ ] Mobile companion app
- [ ] Analytics dashboard
- [ ] Offline mode with queue

---

## 🐛 Known Limitations

1. **Windows Only** - Currently optimized for Windows
2. **Single Camera** - One camera at a time
3. **MP4V Codec** - H264 requires additional codecs
4. **Manual Setup** - Requires initial configuration
5. **No Pause** - Recording can't be paused, only stop

---

## 🆘 Support & Troubleshooting

### Common Issues

**Q: Camera không hiển thị?**
A: Kiểm tra Device Manager, đóng app khác đang dùng camera

**Q: Scanner không kết nối?**
A: Xác định đúng cổng COM trong Device Manager

**Q: Upload thất bại?**
A: Kiểm tra internet, B2 credentials trong .env

**Q: Video bị lag?**
A: Giảm FPS hoặc resolution trong config.yaml

### Getting Help
1. Check logs: `logs/app.log`
2. Read documentation: `INSTALL.md`, `USER_MANUAL.md`
3. Test modules individually
4. Open GitHub issue with logs

---

## 🎓 Learning Resources

### For Developers
- **OpenCV Tutorial**: https://docs.opencv.org/
- **CustomTkinter Docs**: https://customtkinter.tomschimansky.com/
- **B2 API Guide**: https://www.backblaze.com/b2/docs/
- **PySerial Manual**: https://pythonhosted.org/pyserial/

### For Users
- `USER_MANUAL.md` - Complete guide
- `INSTALL.md` - Setup help
- Video tutorials (TBD)

---

## 📝 License

MIT License (recommended)

---

## 👥 Credits

**Developed for**: Lemiex Company
**Purpose**: Warehouse order recording system
**Technology Stack**: Python + CustomTkinter + OpenCV
**Cloud Storage**: Backblaze B2

---

## 📞 Contact & Support

For technical support:
- Email: support@lemiex.us
- GitHub Issues: [repository-url]/issues
- Documentation: See `docs/` folder

---

## ✨ Final Notes

This is a **production-ready application** with:
- ✅ Complete functionality
- ✅ Comprehensive documentation
- ✅ Error handling
- ✅ Logging system
- ✅ Modular architecture
- ✅ Easy configuration
- ✅ User-friendly GUI
- ✅ Automated workflows

**Ready to deploy and use!** 🚀

---

Generated: November 22, 2025
Version: 1.0.0
