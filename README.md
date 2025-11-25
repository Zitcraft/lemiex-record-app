# Lemiex Record App

Ứng dụng ghi hình từ webcam với tích hợp barcode scanner và tự động upload lên Backblaze B2.

## Tính năng chính

- ✅ Hiển thị camera thời gian thực với timestamp
- ✅ Chọn thiết bị camera từ danh sách
- ✅ Tích hợp barcode scanner qua cổng COM/USB
- ✅ Tự động parse mã đơn từ QR code URL
- ✅ Nhập thông tin người sử dụng (kết nối API)
- ✅ Ghi video với timestamp overlay
- ✅ Upload tự động lên Backblaze B2
- ✅ Logging chi tiết và error handling

## Cài đặt

1. **Clone repository:**
   ```bash
   git clone https://github.com/yourusername/lemiex-record-app.git
   cd lemiex-record-app
   ```

2. **Tạo virtual environment:**
   ```bash
   python -m venv venv
   venv\Scripts\activate  # Windows
   ```

3. **Cài đặt dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Cấu hình environment variables:**
   - Copy `.env.example` thành `.env`
   - Điền thông tin Backblaze B2 credentials và API keys

5. **Cấu hình ứng dụng:**
   - Chỉnh sửa `config/config.yaml` theo nhu cầu

## Sử dụng

```bash
python main.py
```

## Cấu trúc dự án

```
Lemiex-record-app/
├── src/
│   ├── camera_manager.py      # Quản lý camera và ghi hình
│   ├── scanner_manager.py     # Quản lý barcode scanner
│   ├── b2_uploader.py         # Upload lên Backblaze B2
│   ├── api_client.py          # Kết nối API
│   ├── logger.py              # Logging system
│   └── main_window.py         # GUI chính
├── config/
│   └── config.yaml            # Cấu hình ứng dụng
├── logs/                      # Log files
├── temp_videos/               # Video tạm thời
├── .env                       # Environment variables (không commit)
├── requirements.txt           # Python dependencies
└── main.py                    # Entry point

```

## Yêu cầu hệ thống

- Python 3.8+
- Windows 10/11
- Webcam
- Barcode Scanner (USB/Serial)
- Internet connection (để upload)

## License

MIT License
