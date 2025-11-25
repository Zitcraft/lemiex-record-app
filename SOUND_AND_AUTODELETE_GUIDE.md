# Hướng dẫn Sound và Auto-Delete

## 🔊 Hệ thống Sound Notification

### Cài đặt pygame
```bash
pip install pygame
```

### Sound files cần thiết
Copy 3 file MP3 vào thư mục `voice/`:
- `1_start_record.mp3` - Phát khi bắt đầu ghi hình
- `2_end_record.mp3` - Phát trước khi upload
- `3_dupcode_continue.mp3` - Phát khi phát hiện mã trùng trên B2

### Luồng hoạt động
1. **Bắt đầu ghi** → Phát `1_start_record.mp3` ngay lập tức
2. **Check duplicate** → Nếu trùng, phát `3_dupcode_continue.mp3` (background)
3. **Dừng ghi** → Phát `2_end_record.mp3` → Bắt đầu upload

## 🗑️ Tự động xóa Video Local

### Tính năng
- **Tự động xóa** video local sau khi upload thành công lên B2
- **Không xóa** nếu upload thất bại
- **Có thể bật/tắt** bằng checkbox trong giao diện

### Cấu hình

**config/config.yaml:**
```yaml
storage:
  auto_delete_after_upload: true  # Mặc định bật
```

### Giao diện
Checkbox: **"Tự động xóa video local sau khi upload"**
- ✅ Bật: Xóa video sau upload thành công
- ⬜ Tắt: Giữ video trong folder `temp_videos/`

### Lưu ý
- Video chỉ bị xóa khi upload **thành công**
- Nếu upload lỗi, video vẫn được giữ lại
- Log ghi lại chi tiết việc xóa file

## 📝 Thay đổi giao diện

### Đã loại bỏ
- ❌ Popup thông báo "Upload thành công" (chỉ hiển thị status)

### Trạng thái hiển thị
- ✓ **Hoàn tất: {order_id}** (màu xanh) - Upload thành công
- ✗ **Lỗi upload: {order_id}** (màu đỏ) - Upload thất bại

## 🔧 Troubleshooting

### Sound không phát
1. Kiểm tra pygame đã cài: `pip show pygame`
2. Kiểm tra file MP3 có trong thư mục `voice/`
3. Xem log: `logs/app.log` để biết lỗi

### Video không tự xóa
1. Kiểm tra checkbox đã bật chưa
2. Kiểm tra upload có thành công không (xem status)
3. Kiểm tra quyền ghi file trong folder `temp_videos/`
