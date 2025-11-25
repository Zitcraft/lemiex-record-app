# Lemiex Record App - User Manual
# Hướng dẫn sử dụng

## Khởi động ứng dụng

1. Mở Command Prompt hoặc PowerShell
2. Chuyển đến thư mục project:
   ```bash
   cd "d:\#1 SCRIPT\Lemiex-record-app"
   ```
3. Kích hoạt virtual environment:
   ```bash
   .\venv\Scripts\Activate.ps1
   ```
4. Chạy ứng dụng:
   ```bash
   python main.py
   ```

## Giao diện chính

### Bên trái: Camera Preview
- Hiển thị hình ảnh từ webcam thời gian thực
- Có timestamp overlay (ngày giờ)
- Kích thước preview: 640x480

### Bên phải: Bảng điều khiển

#### 1. Chọn Camera
- **Dropdown**: Hiển thị danh sách tất cả camera có sẵn
- **Nút "🔄 Làm mới"**: Quét lại danh sách camera
- Chọn camera muốn sử dụng từ dropdown

#### 2. Chọn Scanner
- **Dropdown**: Hiển thị danh sách cổng COM có sẵn
- **Nút "🔄 Làm mới"**: Quét lại danh sách cổng
- Ứng dụng tự động chọn cổng scanner nếu phát hiện được
- Sau khi chọn, scanner sẽ tự động kết nối

#### 3. Mã đơn
- **Textbox**: Nhập mã đơn thủ công hoặc scan bằng gun scanner
- Khi scan QR code dạng `https://lemiex.us/qr/6079`, ứng dụng tự động parse thành `6079`
- Mã đơn là **bắt buộc** để bắt đầu ghi hình

#### 4. Người sử dụng
- **Dropdown**: Chọn nhân viên từ danh sách
- **Nút "🔄 Làm mới"**: Tải lại danh sách nhân viên từ server
- Danh sách hiển thị định dạng: "Tên đầy đủ (username)"
- Chỉ hiển thị nhân viên có tên (bỏ qua null)
- Người sử dụng là **bắt buộc** để bắt đầu ghi hình

#### 5. Nút Ghi hình
- **⏺ Bắt đầu ghi hình** (màu đỏ): Click để bắt đầu ghi
- **⏹ Dừng ghi hình** (màu xanh): Click để dừng và upload

#### 6. Thanh trạng thái
- Hiển thị trạng thái hiện tại của ứng dụng
- Màu xanh: Hoạt động bình thường
- Màu đỏ: Đang ghi hình
- Màu cam: Đang xử lý (upload, tải dữ liệu)

#### 7. Progress Bar
- Chỉ hiển thị khi đang upload video
- Cho biết tiến độ upload từ 0% đến 100%

## Quy trình ghi hình

### Chuẩn bị
1. Chọn camera muốn sử dụng
2. Kết nối scanner (chọn cổng COM)
3. Kiểm tra preview camera hoạt động

### Bắt đầu ghi hình
1. Nhập hoặc scan **Mã đơn**
2. Chọn **Người sử dụng** từ dropdown (hoặc làm mới nếu chưa tải)
3. Click nút **"⏺ Bắt đầu ghi hình"**
4. Trạng thái chuyển sang "Đang ghi hình..."
5. Nút chuyển thành **"⏹ Dừng ghi hình"** màu xanh

### Trong khi ghi hình
- Camera ghi với resolution cao (1920x1080 mặc định)
- Timestamp được thêm vào video
- Có thể scan mã đơn mới cho lần ghi tiếp theo

### Dừng ghi hình
1. Click nút **"⏹ Dừng ghi hình"**
2. Video được lưu vào thư mục `temp_videos/`
3. Tự động bắt đầu upload lên Backblaze B2
4. Progress bar hiển thị tiến độ upload
5. Khi hoàn tất, hiển thị link video

### Sau khi upload
- Video được lưu trên Backblaze B2
- Metadata được gửi lên API
- File local có thể tự động xóa (tùy config)
- Link video được hiển thị trong popup

## Sử dụng Barcode Scanner

### Cách 1: Scan tự động
1. Kết nối scanner qua dropdown
2. Scan QR code
3. Mã đơn tự động điền vào textbox

### Cách 2: Nhập thủ công
1. Click vào textbox "Mã đơn"
2. Gõ mã đơn bằng bàn phím
3. Enter để xác nhận

### Format QR Code hỗ trợ
- `https://lemiex.us/qr/6079` → `6079`
- `6079` → `6079` (trực tiếp)
- Regex pattern có thể tùy chỉnh trong `config.yaml`

## Tips và Lưu ý

### Camera
- Nếu camera không hiển thị, thử "Làm mới" và chọn lại
- Đóng các ứng dụng khác đang dùng camera (Skype, Teams, etc.)
- Có thể điều chỉnh resolution trong `config.yaml`

### Scanner
- Thường sử dụng cổng COM3, COM4
- Nếu không tự động phát hiện, chọn thủ công từ dropdown
- Kiểm tra Device Manager để xác định cổng đúng

### Recording
- Mỗi video được đặt tên: `{order_id}_{timestamp}.mp4`
- Video được upload vào thư mục theo ngày: `recordings/2025/11/22/`
- Đảm bảo có kết nối Internet trước khi dừng ghi

### Upload
- Upload có thể mất vài phút tùy kích thước video
- Không tắt ứng dụng khi đang upload
- Nếu upload thất bại, video vẫn lưu trong `temp_videos/`

### Cấu hình nâng cao
Chỉnh sửa `config/config.yaml` để:
- Thay đổi FPS, resolution
- Tùy chỉnh timestamp format
- Cấu hình scanner baud rate
- Điều chỉnh retry logic cho upload

## Phím tắt (Keyboard Shortcuts)

*Hiện tại chưa có - có thể thêm trong phiên bản sau*

## Troubleshooting

### Camera preview bị lag
- Giảm FPS trong config (30 → 15)
- Giảm preview resolution

### Scanner không đọc được
- Kiểm tra cổng COM trong Device Manager
- Thử baud rate khác (9600, 115200)
- Test scanner bằng Notepad

### Upload thất bại
- Kiểm tra kết nối Internet
- Kiểm tra credentials B2 trong `.env`
- Xem log chi tiết tại `logs/app.log`

### Lỗi "Không tìm thấy camera"
- Cắm lại camera
- Cài đặt driver camera
- Thử camera khác

## File Logs

Tất cả hoạt động được ghi log tại:
```
logs/app.log
logs/app.log.1  (backup cũ)
logs/app.log.2  (backup cũ)
...
```

Log bao gồm:
- Thời gian khởi động/tắt
- Camera operations
- Scanner events
- Upload progress
- Errors và exceptions

## Hỗ trợ

Nếu gặp vấn đề:
1. Kiểm tra `logs/app.log`
2. Đọc `INSTALL.md` để kiểm tra setup
3. Liên hệ technical support
4. Mở issue trên GitHub
