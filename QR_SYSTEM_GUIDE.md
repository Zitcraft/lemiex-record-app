# QR Code System - Lemiex Record App

## 📱 Tổng quan

Hệ thống QR code giúp quản lý và nhận dạng ứng dụng Record trên các máy khác nhau.

## 🎯 Các QR Code

### 1. USB-COM Setup
- **Mã QR**: `USB-COM-SETUP`
- **Chức năng**: Hướng dẫn cấu hình cổng COM USB
- **Vị trí hiển thị**: Bên trái, dưới Camera Preview
- **Khi scan**: Hiển thị thông báo "USB-COM Setup" màu cyan

### 2. Factory Default
- **Mã QR**: `FACTORY-DEFAULT`
- **Chức năng**: Reset cài đặt về mặc định
- **Vị trí hiển thị**: Giữa, dưới Camera Preview
- **Khi scan**: Hiển thị thông báo "Factory Default" màu cyan

### 3. App Identifier (This App)
- **Mã QR**: `LEMIEX-RECORD-APP-IDENTIFIER-COM3`
- **Chức năng**: Nhận dạng ứng dụng đang sử dụng COM3
- **Vị trí hiển thị**: Bên phải, dưới Camera Preview
- **Khi scan**: 
  - ✅ QR nháy sáng (flash gold color)
  - ✅ Phát âm thanh thông báo
  - ✅ Hiển thị "✓ App QR nhận dạng - COM3 Active" màu vàng gold

## 🎨 Giao diện

```
┌────────────────────────────────┐
│      Camera Preview            │
│                                │
│      (Video Feed)              │
│                                │
└────────────────────────────────┘
┌────────────────────────────────┐
│        Quick Access            │
├──────────┬──────────┬──────────┤
│   [QR]   │   [QR]   │   [QR]   │
│ USB-COM  │ Factory  │ This App │
│          │ Default  │          │
└──────────┴──────────┴──────────┘
```

## 💡 Cách sử dụng

### Nhận dạng ứng dụng trên nhiều máy

**Kịch bản**: Bạn có 3 máy sử dụng app Record, mỗi máy kết nối scanner khác nhau (COM3, COM4, COM5)

**Giải pháp**:
1. Tạo QR riêng cho mỗi app:
   - Máy 1: `LEMIEX-RECORD-APP-IDENTIFIER-COM3`
   - Máy 2: `LEMIEX-RECORD-APP-IDENTIFIER-COM4`
   - Máy 3: `LEMIEX-RECORD-APP-IDENTIFIER-COM5`

2. Khi cần biết máy nào đang dùng:
   - Scan QR "This App" trên màn hình
   - App sẽ nháy sáng + phát âm thanh
   - Trạng thái hiển thị: "COM3 Active" (hoặc COM4, COM5)

3. Lợi ích:
   - Xác định nhanh app nào đang hoạt động
   - Không cần kiểm tra cổng COM thủ công
   - Tiện lợi khi có nhiều máy giống nhau

## 🔧 Tùy chỉnh

### Tạo QR cho cổng COM khác

**Bước 1**: Chỉnh sửa `generate_qr_codes.py`

```python
# Thay COM3 thành COM4 (hoặc cổng bạn muốn)
generate_qr_code(
    data="LEMIEX-RECORD-APP-IDENTIFIER-COM4",  # ← Đổi số
    filename="app-identifier",
    output_dir=output_dir
)
```

**Bước 2**: Generate lại QR

```powershell
python generate_qr_codes.py
python convert_qr_to_png.py
```

**Bước 3**: Cập nhật code kiểm tra trong `main_window.py`

```python
# Tìm dòng này trong on_barcode_scanned():
if order_id.upper() == "LEMIEX-RECORD-APP-IDENTIFIER-COM3":

# Đổi thành:
if order_id.upper() == "LEMIEX-RECORD-APP-IDENTIFIER-COM4":
```

**Bước 4**: Update status message

```python
self.status_label.configure(
    text="✓ App QR nhận dạng - COM4 Active",  # ← Đổi số
    text_color="#FFD700"
)
```

### Thay đổi màu flash

Trong `flash_app_qr()` method:

```python
# Màu hiện tại: #FFD700 (Gold)
flash_colors = ["#FFD700", original_color, "#FFD700", ...]

# Đổi sang màu khác:
flash_colors = ["#00FF00", original_color, "#00FF00", ...]  # Green
flash_colors = ["#FF0000", original_color, "#FF0000", ...]  # Red
flash_colors = ["#00FFFF", original_color, "#00FFFF", ...]  # Cyan
```

### Thay đổi thời gian flash

```python
# Thời gian mỗi flash (milliseconds)
flash_delays = [100, 200, 300, 400, 500, 600]  # Hiện tại: 100ms mỗi lần

# Flash nhanh hơn:
flash_delays = [50, 100, 150, 200, 250, 300]   # 50ms mỗi lần

# Flash chậm hơn:
flash_delays = [200, 400, 600, 800, 1000, 1200]  # 200ms mỗi lần
```

## 📄 Files liên quan

- **QR Images**: `qr_codes/` folder
  - `USB-COM.png` - USB-COM setup QR
  - `Factory-Default.png` - Factory default QR
  - `app-identifier.png` - App identifier QR

- **Generator Scripts**:
  - `generate_qr_codes.py` - Generate SVG QR codes
  - `convert_qr_to_png.py` - Convert SVG to PNG

- **Main Code**:
  - `src/main_window.py` - QR display & flash logic
  - `Lemiex-record-app.spec` - Bundle QR images in build

## 🚀 Build với QR Codes

QR codes sẽ tự động được bundle vào executable:

```powershell
.\build.bat
```

Executable sẽ chứa:
- 3 QR code PNG files
- Flash effect code
- Sound notification

## 🧪 Testing

### Test flash effect:

1. Chạy app: `python main.py`
2. Kết nối scanner
3. Scan QR "app-identifier" 
4. Kiểm tra:
   - ✅ QR có nháy sáng màu vàng?
   - ✅ Có phát âm thanh?
   - ✅ Status hiển thị "COM3 Active"?

### Test các QR khác:

1. Scan "USB-COM" QR → Status: "USB-COM Setup" (cyan)
2. Scan "Factory-Default" QR → Status: "Factory Default" (cyan)
3. Scan order ID bình thường → Ghi hình như thường

## 📝 Log Messages

Khi scan QR, log sẽ ghi:

```
INFO - Barcode scanned: LEMIEX-RECORD-APP-IDENTIFIER-COM3
INFO - App identifier QR scanned - triggering flash
INFO - App QR flash triggered
```

Nếu lỗi:

```
ERROR - Failed to load QR USB-COM.png: [error details]
ERROR - Flash error: [error details]
```

## 🎁 Tính năng nổi bật

✅ **Visual Feedback**: QR nháy sáng khi scan
✅ **Audio Feedback**: Phát âm thanh thông báo
✅ **Status Display**: Hiển thị rõ ràng COM port
✅ **Multi-machine Support**: Dễ dàng nhận dạng nhiều máy
✅ **No Collision**: Không ảnh hưởng đến scan order ID
✅ **Embedded**: QR được bundle sẵn trong executable

---

**Version**: 1.0.0  
**Last Updated**: December 1, 2025
