# Metadata & B2 Upload System

## 📋 Tổng quan

Hệ thống tự động lưu metadata dạng JSON cho mỗi video được ghi và upload lên Backblaze B2.

## 🔑 Cấu hình B2

### Thông tin đã cấu hình:

```
Application Key ID: 005fa7d122849800000000001
Application Key: K005lJSJmC2V+mpLJNySz4S9540gnsM
Key Name: LemiexEmbroidery
Bucket Name: LemiexEmbroidery
```

### File cấu hình:

**`.env`**:
```env
B2_APPLICATION_KEY_ID=005fa7d122849800000000001
B2_APPLICATION_KEY=K005lJSJmC2V+mpLJNySz4S9540gnsM
```

**`config/config.yaml`**:
```yaml
backblaze:
  bucket_name: "LemiexEmbroidery"
  folder_prefix: "recordings/{date}"
  metadata_folder: "metadata"

storage:
  metadata_dir: "metadata"
  save_metadata_json: true
```

## 📝 Cấu trúc JSON Metadata

Mỗi lần ghi video, file JSON tự động được tạo trong thư mục `metadata/`:

**Filename format**: `{order_id}_{timestamp}.json`

**Ví dụ**: `12345_20251125_143052.json`

```json
{
  "id": "12345",
  "date": "2025-11-25",
  "time": "14:30:52",
  "user": "john_doe",
  "url_upload": "https://f005.backblazeb2.com/file/LemiexEmbroidery/recordings/2025/11/25/12345_20251125_143052.mp4"
}
```

### Các trường trong JSON:

| Trường | Mô tả | Ví dụ |
|--------|-------|-------|
| `id` | Mã đơn hàng | "12345" |
| `date` | Ngày ghi (YYYY-MM-DD) | "2025-11-25" |
| `time` | Giờ ghi (HH:MM:SS) | "14:30:52" |
| `user` | Username người ghi | "john_doe" |
| `url_upload` | URL video trên B2 | "https://f005.backblazeb2.com/..." |

## 🚀 Cách sử dụng

### 1. Ghi video như bình thường

- Chọn camera
- Nhập hoặc scan mã đơn
- Chọn người sử dụng
- Bấm "Bắt đầu ghi hình"

### 2. Hệ thống tự động:

1. ✅ Ghi video với timestamp overlay
2. ✅ Upload video lên B2
3. ✅ Tạo file JSON metadata trong `metadata/`
4. ✅ Upload metadata lên API
5. ✅ Xóa video local (nếu bật `auto_delete_after_upload`)

### 3. Truy cập metadata

**Lấy metadata cho 1 đơn**:
```python
from src.metadata_manager import MetadataManager

manager = MetadataManager()
metadata = manager.get_metadata("12345")
print(metadata)
```

**Lấy tất cả metadata của 1 đơn**:
```python
all_metadata = manager.get_all_metadata("12345")
for meta in all_metadata:
    print(f"{meta['date']} {meta['time']} - {meta['user']}")
```

**List tất cả metadata**:
```python
all_records = manager.list_all_metadata()
print(f"Tổng cộng {len(all_records)} recordings")
```

## 📂 Cấu trúc thư mục

```
Lemiex-record-app/
├── metadata/                    # JSON metadata files
│   ├── 12345_20251125_143052.json
│   ├── 12346_20251125_150030.json
│   └── ...
├── temp_videos/                 # Temporary video files
│   └── (được xóa sau khi upload)
├── logs/                        # Application logs
└── config/
    └── config.yaml             # Main configuration
```

## 🔍 B2 URL Structure

Videos được lưu trên B2 theo cấu trúc:

```
https://f005.backblazeb2.com/file/LemiexEmbroidery/recordings/{YYYY}/{MM}/{DD}/{order_id}_{timestamp}.mp4
```

**Ví dụ**:
```
https://f005.backblazeb2.com/file/LemiexEmbroidery/recordings/2025/11/25/12345_20251125_143052.mp4
```

## ✅ Test hệ thống

### Test Metadata Manager:
```bash
python -m src.metadata_manager
```

### Test B2 Connection:
```bash
python -c "from src.b2_uploader import B2Uploader; u = B2Uploader(); print('✓ Success' if u.authenticate() else '✗ Failed')"
```

### Kiểm tra metadata files:
```bash
ls metadata/
```

## 🔧 Troubleshooting

### Lỗi B2 Authentication Failed

1. Kiểm tra `.env` file có đúng credentials
2. Kiểm tra bucket name trong `config.yaml`
3. Kiểm tra internet connection

### Metadata không được tạo

1. Kiểm tra `save_metadata_json: true` trong config.yaml
2. Kiểm tra folder `metadata/` có tồn tại
3. Kiểm tra logs trong `logs/app.log`

### Video không upload

1. Kiểm tra B2 authentication
2. Kiểm tra bucket permissions
3. Kiểm tra network connection
4. Xem logs để biết lỗi chi tiết

## 💡 Lợi ích

✅ **JSON đẹp, dễ đọc** - Pretty format với indent 2 spaces
✅ **Tự động backup local** - Có metadata ngay cả khi API lỗi  
✅ **Dễ tích hợp** - Hệ thống khác đọc JSON để biết video
✅ **Lịch sử đầy đủ** - Track được tất cả recordings
✅ **UTF-8 encoding** - Hỗ trợ tiếng Việt đầy đủ
✅ **Timestamp chính xác** - Date, time riêng biệt

## 📊 API Integration

JSON metadata có thể được sử dụng bởi:
- Web dashboard để hiển thị recordings
- Mobile app để xem lịch sử
- Reporting system để thống kê
- Backup/restore tools
- Video management systems

## 🎯 Next Steps

Sau khi hoàn thiện:
1. Test ghi video thực tế
2. Kiểm tra JSON được tạo đúng format
3. Verify video upload lên B2 thành công
4. Tích hợp với hệ thống khác (nếu cần)
