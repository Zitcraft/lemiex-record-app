# ✅ Dynamic QR System - Nhận dạng nhiều thiết bị

## 🎯 Cập nhật mới

### Tính năng Dynamic QR Code
Mỗi lần khởi động app sẽ tạo **QR code duy nhất** cho máy đó, giúp nhận dạng và phân biệt nhiều thiết bị khác nhau.

## 🔄 Cách hoạt động

### 1. Mỗi lần khởi động app:
```
┌─────────────────────────────────┐
│  App Start                      │
│  ↓                              │
│  Generate Random Session ID      │
│  (Ví dụ: c890b340)              │
│  ↓                              │
│  Create QR: LEMIEX-APP-c890b340 │
│  ↓                              │
│  Display QR on screen            │
└─────────────────────────────────┘
```

### 2. Khi scan QR:
- Scanner scan QR trên màn hình
- App kiểm tra: "Đây có phải QR của tôi không?"
- Nếu **ĐÚNG** → Nháy sáng + phát âm thanh
- Nếu **SAI** → Không phản ứng

## 📱 Ví dụ thực tế

### Scenario: 3 máy cùng chạy app

**Máy 1** (COM3):
- Khởi động lúc 8:00 AM
- Session ID: `a1b2c3d4`
- QR Code: `LEMIEX-APP-a1b2c3d4`

**Máy 2** (COM4):
- Khởi động lúc 8:05 AM
- Session ID: `e5f6g7h8`
- QR Code: `LEMIEX-APP-e5f6g7h8`

**Máy 3** (COM5):
- Khởi động lúc 8:10 AM
- Session ID: `i9j0k1l2`
- QR Code: `LEMIEX-APP-i9j0k1l2`

### Test nhận dạng:

1. **Scan QR của Máy 1** (`a1b2c3d4`):
   - Máy 1: ✅ Nháy sáng + âm thanh
   - Máy 2: ❌ Không phản ứng
   - Máy 3: ❌ Không phản ứng

2. **Scan QR của Máy 2** (`e5f6g7h8`):
   - Máy 1: ❌ Không phản ứng
   - Máy 2: ✅ Nháy sáng + âm thanh
   - Máy 3: ❌ Không phản ứng

## 🖥️ Giao diện hiển thị

QR Code "This App" sẽ hiển thị:
```
┌──────────────┐
│              │
│   [QR Code]  │
│              │
├──────────────┤
│  This App    │
│    COM3      │
│  ID: a1b2    │
└──────────────┘
```

Thông tin hiển thị:
- **This App**: Tên QR
- **COM3**: Cổng scanner đang dùng
- **ID: a1b2**: 4 ký tự đầu của session ID

## 📝 Session Information

Mỗi session được lưu trong file `session.json`:

```json
{
  "session_id": "a1b2c3d4",
  "com_port": "COM3",
  "timestamp": "2025-12-01T18:40:12",
  "qr_code": "LEMIEX-APP-a1b2c3d4"
}
```

Location: `<app_directory>/session.json`

## 🎨 Khi scan QR nhận dạng

### Visual Feedback:
- QR nháy sáng màu vàng gold 3 lần
- Flash duration: 100ms mỗi lần

### Audio Feedback:
- Phát file: `3_dupcode_continue.mp3`

### Status Display:
```
✓ App nhận dạng - COM3 - ID: a1b2c3d4
```
Màu vàng gold (#FFD700)

## 🔧 Technical Details

### Session ID Generation:
```python
import uuid

# Generate unique 8-character ID
session_id = str(uuid.uuid4())[:8]
# Example output: "a1b2c3d4"
```

### QR Code Format:
```
LEMIEX-APP-{session_id}
```

Example: `LEMIEX-APP-a1b2c3d4`

### QR Code Storage:
- File: `qr_codes/app-identifier.png`
- Size: 150x150 pixels
- Format: PNG
- Regenerated: Every app startup

## ✅ Lợi ích

### 1. Nhận dạng chính xác
- Mỗi máy có QR riêng biệt
- Không nhầm lẫn giữa các thiết bị
- Scan đúng máy → Phản hồi ngay

### 2. Không cần cấu hình
- Tự động tạo QR khi khởi động
- Không cần setup thủ công
- Không cần edit code

### 3. Dễ dàng kiểm tra
- In QR ra giấy
- Dán lên màn hình
- Scan để test từng máy

### 4. Multi-device support
- Hỗ trợ không giới hạn số máy
- Mỗi máy độc lập
- Không conflict

## 🖨️ In QR Code để test

### Option 1: Screenshot
1. Chạy app
2. Screenshot QR code
3. In ra giấy
4. Test bằng gun scanner

### Option 2: Lấy từ file
1. Mở `qr_codes/app-identifier.png`
2. In file PNG
3. Dán lên bàn làm việc

### Option 3: Sử dụng session.json
1. Mở `session.json`
2. Copy QR code data
3. Tạo QR mới bằng online tool
4. In và test

## 🧪 Testing

### Test 1: Single Machine
```
1. Khởi động app
2. Xem session ID trong log
3. Scan QR trên màn hình
4. Check: App có nháy sáng?
```

### Test 2: Multiple Machines
```
1. Khởi động app trên Máy A và Máy B
2. Screenshot QR của cả 2 máy
3. Scan QR của Máy A trên Máy A → Nháy sáng?
4. Scan QR của Máy A trên Máy B → Không phản ứng?
5. Scan QR của Máy B trên Máy B → Nháy sáng?
```

### Test 3: Restart
```
1. Khởi động app lần 1 → Ghi nhận session ID
2. Tắt app
3. Khởi động app lần 2 → Session ID mới?
4. QR code khác với lần 1?
```

## 📊 Logs

Khi khởi động app:
```
MainWindow - INFO - Dynamic QR generated: LEMIEX-APP-a1b2c3d4
```

Khi scan đúng QR:
```
MainWindow - INFO - This app's QR scanned - Session: a1b2c3d4, COM: COM3
```

Khi scan sai QR:
```
MainWindow - INFO - Barcode scanned: LEMIEX-APP-xxxxxxxx
(Không có reaction log)
```

## 🔄 Workflow hoàn chỉnh

```
1. Khởi động App
   ↓
2. Tạo Session ID mới
   ↓
3. Generate QR Code
   ↓
4. Hiển thị QR trên UI
   ↓
5. Scanner quét QR
   ↓
6. App check: My QR?
   ├─ YES → Flash + Sound + Status
   └─ NO → Ignore
```

## 💡 Use Cases

### Case 1: Workshop với 5 máy
- 5 máy cùng chạy app Record
- Mỗi máy có QR riêng
- Kỹ thuật viên scan từng QR để test
- Máy nào lỗi → Không phản hồi

### Case 2: Shift handover
- Ca sáng tắt app
- Ca chiều khởi động lại
- Session mới tự động tạo
- QR mới hiển thị

### Case 3: Debug remote
- User chụp QR gửi qua chat
- Dev biết session ID
- Check log theo session
- Troubleshoot dễ dàng

---

**Version**: 1.0.0  
**Feature**: Dynamic QR Code System  
**Last Updated**: December 1, 2025  
**Status**: ✅ Implemented & Tested
