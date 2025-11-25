# Installation and Setup Guide

## Cài đặt chi tiết

### Bước 1: Cài đặt Python

1. Download Python 3.8 hoặc mới hơn từ: https://www.python.org/downloads/
2. Khi cài đặt, **nhớ check** "Add Python to PATH"
3. Kiểm tra cài đặt:
   ```bash
   python --version
   ```

### Bước 2: Clone hoặc Download Project

```bash
cd "d:\#1 SCRIPT"
git clone <repository-url> Lemiex-record-app
cd Lemiex-record-app
```

### Bước 3: Tạo Virtual Environment

```bash
python -m venv venv
```

### Bước 4: Kích hoạt Virtual Environment

**Windows PowerShell:**
```powershell
.\venv\Scripts\Activate.ps1
```

**Windows Command Prompt:**
```cmd
venv\Scripts\activate.bat
```

Sau khi kích hoạt, bạn sẽ thấy `(venv)` xuất hiện trước dòng lệnh.

### Bước 5: Cài đặt Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### Bước 6: Cấu hình Backblaze B2

1. Đăng nhập vào Backblaze B2: https://www.backblaze.com/b2/cloud-storage.html
2. Tạo Bucket mới (ví dụ: `lemiex-recordings`)
3. Tạo Application Key:
   - Vào "App Keys"
   - Click "Add a New Application Key"
   - Copy **keyID** và **applicationKey**

### Bước 7: Cấu hình Environment Variables

1. Copy file `.env.example` thành `.env`:
   ```bash
   copy .env.example .env
   ```

2. Mở file `.env` và điền thông tin:
   ```
   B2_APPLICATION_KEY_ID=your_actual_key_id
   B2_APPLICATION_KEY=your_actual_application_key
   
   API_KEY=your_api_key_here
   API_SECRET=your_api_secret_here
   ```

### Bước 8: Cấu hình Application

Mở `config/config.yaml` và điều chỉnh:

```yaml
camera:
  fps: 30  # Điều chỉnh FPS nếu cần
  recording_width: 1920  # Độ phân giải ghi hình
  recording_height: 1080

scanner:
  default_port: "COM3"  # Đổi thành cổng COM của scanner

backblaze:
  bucket_name: "lemiex-recordings"  # Tên bucket bạn đã tạo

api:
  base_url: "https://api.lemiex.us"  # URL API của bạn
```

### Bước 9: Kiểm tra Setup

Test các module:

```bash
# Test logger
python -c "from src.logger import logger; logger.info('Test OK')"

# Test camera
python src/camera_manager.py

# Test scanner
python src/scanner_manager.py

# Test B2 uploader
python src/b2_uploader.py
```

### Bước 10: Chạy Application

```bash
python main.py
```

## Xử lý lỗi thường gặp

### Lỗi: "No module named 'cv2'"

```bash
pip install opencv-python
```

### Lỗi: "No module named 'customtkinter'"

```bash
pip install customtkinter
```

### Lỗi: Camera không mở được

- Kiểm tra camera có đang được sử dụng bởi app khác không
- Thử index camera khác (0, 1, 2...)
- Kiểm tra driver camera

### Lỗi: Scanner không kết nối được

- Kiểm tra cổng COM trong Device Manager (Windows)
- Thử các baud rate khác (9600, 115200)
- Kiểm tra driver USB-Serial

### Lỗi: B2 Authentication failed

- Kiểm tra lại `B2_APPLICATION_KEY_ID` và `B2_APPLICATION_KEY`
- Đảm bảo không có khoảng trắng thừa trong `.env`
- Kiểm tra bucket name chính xác

## Build Executable (Optional)

Để tạo file `.exe` độc lập:

```bash
pip install pyinstaller

pyinstaller --name "LemiexRecordApp" ^
            --windowed ^
            --onefile ^
            --icon=icon.ico ^
            --add-data "config;config" ^
            main.py
```

File `.exe` sẽ ở trong thư mục `dist/`

## Cập nhật Application

```bash
git pull origin main
pip install -r requirements.txt --upgrade
```

## Liên hệ hỗ trợ

Nếu gặp vấn đề, vui lòng:
1. Kiểm tra file log tại `logs/app.log`
2. Mở issue trên GitHub repository
3. Liên hệ team support
