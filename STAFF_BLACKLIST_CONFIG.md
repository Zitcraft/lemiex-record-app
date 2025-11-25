# Hướng dẫn cấu hình Staff Blacklist

## Mục đích

Staff blacklist cho phép ẩn một số nhân viên nhất định khỏi dropdown list trong ứng dụng, giúp giảm danh sách hiển thị và chỉ cho phép một số người dùng cụ thể.

## Cách cấu hình

### 1. Mở file cấu hình

Mở file `config/config.yaml` bằng text editor (Notepad, VSCode, etc.)

### 2. Tìm phần API configuration

```yaml
api:
  base_url: "https://lemiex.us"
  timeout: 10
  endpoints:
    user_info: "/users/{user_id}"
    order_validate: "/orders/{order_id}"
    upload_metadata: "/recordings/metadata"
    staff_list: "/api/staff"
  staff_blacklist: [95, 99, 100]  # Staff IDs to hide from dropdown
```

### 3. Chỉnh sửa danh sách blacklist

Thêm hoặc bỏ staff ID trong `staff_blacklist`:

```yaml
# Ví dụ 1: Ẩn staff ID 95, 99, 100
staff_blacklist: [95, 99, 100]

# Ví dụ 2: Không ẩn ai (để trống)
staff_blacklist: []

# Ví dụ 3: Chỉ ẩn staff ID 95
staff_blacklist: [95]

# Ví dụ 4: Ẩn nhiều staff
staff_blacklist: [95, 99, 100, 102, 103]
```

### 4. Lưu file và restart ứng dụng

Sau khi chỉnh sửa, lưu file và khởi động lại ứng dụng để áp dụng thay đổi.

## Cách xác định Staff ID

### Option 1: Xem response từ API

Truy cập trực tiếp: https://lemiex.us/api/staff

Bạn sẽ thấy danh sách như:
```json
[
  {
    "id": 95,
    "username": "staff",
    "full_name": null
  },
  {
    "id": 102,
    "username": "anhmachineop",
    "full_name": "Anh Machine OP"
  }
]
```

Staff ID là giá trị của field `id`.

### Option 2: Kiểm tra trong log file

Mở `logs/app.log` và tìm dòng:
```
Retrieved X staff member(s)
```

Log sẽ có thông tin chi tiết về staff được load.

## Quy tắc lọc

Ứng dụng tự động áp dụng các quy tắc sau:

1. **Lọc null full_name**: Chỉ hiển thị staff có `full_name` không phải `null`
   - ✅ Hiển thị: `"full_name": "Anh Machine OP"`
   - ❌ Không hiển thị: `"full_name": null`

2. **Áp dụng blacklist**: Loại bỏ các staff ID có trong `staff_blacklist`
   - Nếu ID 95 trong blacklist → Ẩn staff có `id: 95`

3. **Kết quả cuối cùng**: Dropdown chỉ hiển thị staff thỏa mãn cả 2 điều kiện trên

## Ví dụ thực tế

### Scenario 1: Chỉ cho phép Machine Operators

```yaml
# Ẩn tất cả staff test accounts
staff_blacklist: [95, 99, 100]
```

Kết quả dropdown:
- ✅ Anh Machine OP (anhmachineop)
- ✅ Thành Machine OP (dthanhmachineop)
- ✅ Thanh MOP/STOCK (kthanhstock)
- ✅ Thông Machine OP (thongmachineop)
- ✅ Huy Machine OP (huymachineop)

### Scenario 2: Chỉ cho phép một số người cụ thể

```yaml
# Chỉ cho phép ID 102, 103, 104 (ẩn tất cả còn lại)
staff_blacklist: [95, 99, 100, 105, 106]
```

Kết quả dropdown:
- ✅ Anh Machine OP (anhmachineop)
- ✅ Thành Machine OP (dthanhmachineop)
- ✅ Thanh MOP/STOCK (kthanhstock)

### Scenario 3: Cho phép tất cả

```yaml
# Không ẩn ai
staff_blacklist: []
```

Kết quả dropdown: Tất cả staff có full_name

## Troubleshooting

### Q: Dropdown vẫn hiển thị staff đã blacklist?

A: Đảm bảo:
1. Đã lưu file `config.yaml`
2. Đã restart ứng dụng
3. Syntax YAML đúng (có dấu `[]` và dấu phẩy)
4. Staff ID chính xác

### Q: Dropdown trống hoàn toàn?

A: Kiểm tra:
1. Kết nối Internet (API cần truy cập online)
2. `staff_blacklist` không ẩn tất cả staff
3. API endpoint đúng: `https://lemiex.us/api/staff`
4. Log file để xem lỗi chi tiết

### Q: Làm sao biết blacklist đã áp dụng?

A: Kiểm tra log file:
```
Retrieved X staff member(s)
```

Số lượng X sẽ là tổng staff có full_name trừ đi số staff trong blacklist.

## Best Practices

1. **Backup trước khi sửa**: Copy `config.yaml` trước khi chỉnh sửa
2. **Comment rõ ràng**: Thêm comment giải thích tại sao ẩn staff nào
   ```yaml
   staff_blacklist: [95, 99, 100]  # Test accounts không dùng production
   ```
3. **Test sau khi thay đổi**: Restart app và kiểm tra dropdown
4. **Document**: Ghi lại danh sách staff được phép trong tài liệu nội bộ

## Tóm tắt

| Cấu hình | Kết quả |
|----------|---------|
| `staff_blacklist: []` | Hiển thị tất cả staff có full_name |
| `staff_blacklist: [95]` | Ẩn staff ID 95 |
| `staff_blacklist: [95, 99, 100]` | Ẩn 3 staff có ID này |

**Lưu ý**: Staff có `full_name: null` sẽ **luôn bị ẩn**, không phụ thuộc vào blacklist.
