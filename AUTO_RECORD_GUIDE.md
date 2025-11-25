# Hướng dẫn sử dụng tính năng Auto-Record

## Tính năng mới

### 1. Tự động kết nối Scanner
- **Khi khởi động**: Ứng dụng tự động tìm và kết nối COM3 (nếu có)
- **Status**: Hiển thị "Scanner kết nối: COM3" khi thành công
- **Background listening**: Scanner luôn lắng nghe sẵn sàng

### 2. Auto-Record khi Scan
Ứng dụng tự động bắt đầu/dừng ghi hình khi scan mã QR, không cần click nút "Bắt đầu ghi hình".

## Quy trình sử dụng

### Chuẩn bị
1. Khởi động ứng dụng
2. Chọn nhân viên từ dropdown
3. Scanner tự động kết nối COM3
4. Camera preview đã sẵn sàng

### Workflow 1: Ghi hình đơn giản
```
Bước 1: Scan mã QR đơn hàng (ví dụ: 6079)
   → Ứng dụng tự động:
      - Điền mã đơn: "6079"
      - Bắt đầu ghi hình ngay lập tức
      - Hiển thị: "Đang ghi: 6079" (màu đỏ)

Bước 2: Scan lại cùng mã QR (6079)
   → Ứng dụng tự động:
      - Dừng ghi hình
      - Upload video lên Backblaze B2
      - Hiển thị: "✓ Hoàn tất: 6079" (màu xanh)
      - Popup thông báo URL video
```

### Workflow 2: Chuyển đổi nhanh giữa các đơn
```
Bước 1: Scan mã QR đơn 1 (6079)
   → Bắt đầu ghi: 6079

Bước 2: Scan mã QR đơn 2 (6080) TRƯỚC KHI dừng đơn 1
   → Ứng dụng tự động:
      - Dừng ghi đơn 6079 (không có popup)
      - Upload đơn 6079 trong background
      - Bắt đầu ghi đơn 6080 ngay lập tức
      - Hiển thị: "Chuyển sang mã 6080"

Bước 3: Scan mã QR đơn 3 (6081)
   → Tương tự, chuyển từ 6080 → 6081
   
Bước 4: Scan lại mã 6081 để dừng
   → Dừng và hiển thị popup hoàn tất
```

## So sánh với chế độ thủ công

### Chế độ cũ (Manual):
1. Scan/nhập mã đơn
2. **Click nút "Bắt đầu ghi hình"**
3. Ghi hình...
4. **Click nút "Dừng ghi hình"**
5. Upload và popup kết quả

### Chế độ mới (Auto):
1. Scan mã đơn → **Tự động bắt đầu**
2. Ghi hình...
3. Scan lại mã đơn → **Tự động dừng** và upload

**Tiết kiệm: 2 thao tác click cho mỗi video!**

## Các trường hợp sử dụng

### Case 1: Ghi 1 đơn hàng
```
Scan 6079 → Ghi hình 2 phút → Scan 6079 lại → Hoàn tất
```

### Case 2: Ghi nhiều đơn liên tiếp (riêng biệt)
```
Scan 6079 → Ghi → Scan 6079 → Hoàn tất
Scan 6080 → Ghi → Scan 6080 → Hoàn tất
Scan 6081 → Ghi → Scan 6081 → Hoàn tất
```

### Case 3: Chuyển đổi nhanh (không chờ dừng)
```
Scan 6079 → Ghi đơn 1...
Scan 6080 → Tự động dừng đơn 1, bắt đầu đơn 2
Scan 6081 → Tự động dừng đơn 2, bắt đầu đơn 3
Scan 6081 → Dừng đơn 3
```

### Case 4: Sửa lỗi scan nhầm
```
Đang ghi đơn 6079...
Scan nhầm 6080 → Tự động chuyển sang 6080
(Nếu muốn quay lại 6079: Scan 6080 để dừng, rồi scan 6079 lại)
```

## Trạng thái màu sắc

| Màu | Ý nghĩa | Ví dụ |
|-----|---------|-------|
| 🔵 Xanh dương | Đã scan mã mới | "Đã scan: 6079" |
| 🔴 Đỏ | Đang ghi hình | "Đang ghi: 6079" |
| 🟠 Cam | Đang xử lý/chuyển | "Chuyển sang mã 6080" |
| 🟢 Xanh lá | Hoàn tất thành công | "✓ Hoàn tất: 6079" |
| 🔴 Đỏ | Lỗi | "✗ Lỗi upload: 6079" |

## Nút "Bắt đầu/Dừng ghi hình"

Nút vẫn hoạt động bình thường:
- **Click khi không ghi**: Bắt đầu ghi thủ công (nếu đã có mã đơn)
- **Click khi đang ghi**: Dừng ghi thủ công và hiển thị popup

Dùng khi:
- Muốn kiểm soát thủ công
- Không có scanner
- Scanner bị lỗi

## Thông báo Popup

### Có popup:
- ✅ Dừng bằng scan lại cùng mã
- ✅ Dừng bằng click nút
- ✅ Lỗi upload

### Không có popup:
- ❌ Chuyển đổi tự động giữa các đơn (để không gián đoạn)
- Upload chạy background, status hiển thị trên thanh trạng thái

## Tips & Tricks

### 1. Ghi nhanh nhiều đơn
Scan liên tục: 6079 → 6080 → 6081 → 6082 → scan 6082 lại
→ Có 4 video riêng biệt

### 2. Ghi dài cho 1 đơn
Scan 6079 → Ghi 10 phút → Scan 6079 lại
→ 1 video dài 10 phút

### 3. Chia nhỏ 1 đơn thành nhiều video
Scan 6079 → Ghi 2 phút → Scan 6079 → Hoàn tất
Scan 6079 → Ghi 2 phút → Scan 6079 → Hoàn tất
→ Cùng mã đơn nhưng có 2 video (timestamp khác nhau)

### 4. Kiểm tra status
Luôn xem thanh status để biết:
- Đang ghi mã nào
- Đã upload xong chưa
- Có lỗi không

## Troubleshooting

### Q: Scanner không tự động kết nối?
A: 
- Kiểm tra COM3 có tồn tại không (Device Manager)
- Click nút "🔄 Làm mới" ở phần Scanner
- Chọn thủ công từ dropdown

### Q: Scan mà không bắt đầu ghi?
A: Kiểm tra:
- Đã chọn người sử dụng chưa?
- Status có hiển thị "Thiếu người sử dụng"?
- Scanner có kết nối không? (xem status)

### Q: Muốn dừng ngay mà không scan lại?
A: Click nút "⏹ Dừng ghi hình" màu xanh

### Q: Upload bị lỗi?
A: 
- Kiểm tra Internet
- Kiểm tra credentials B2 trong .env
- Xem log chi tiết: `logs/app.log`

### Q: Video bị ngắt khi chuyển đơn?
A: Đúng rồi! Mỗi đơn = 1 video riêng:
- Đơn 6079: video1.mp4
- Đơn 6080: video2.mp4

### Q: Muốn tắt auto-record?
A: Hiện tại chưa có cài đặt. Bạn có thể:
- Không scan (nhập thủ công + click nút)
- Hoặc disconnect scanner

## Lưu ý quan trọng

⚠️ **Không scan nhầm mã khác đơn khi đang ghi!**
- Nếu scan nhầm → Tự động chuyển đơn
- Video đơn trước sẽ bị cắt ngay

⚠️ **Đợi upload xong trước khi tắt app**
- Xem progress bar và status
- Đợi hiển thị "✓ Hoàn tất"

✅ **Nên chọn người sử dụng trước**
- Không thể ghi nếu chưa chọn
- Chỉ cần chọn 1 lần cho cả session

## Keyboard Shortcuts

Hiện tại: Không có
Tương lai: Có thể thêm phím tắt như:
- Space: Bắt đầu/Dừng
- Esc: Dừng ngay
- Ctrl+R: Refresh camera

---

**Tóm tắt**: Scan để bắt đầu, scan lại để dừng, scan mã khác để chuyển! 🚀
