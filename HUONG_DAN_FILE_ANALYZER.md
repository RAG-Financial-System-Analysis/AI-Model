# 🤖 HƯỚNG DẪN SỬ DỤNG AI FILE ANALYZER CHATBOT

## 📋 Tổng quan

Chatbot có thể nhận và phân tích:
- 📄 **File TXT**: Đọc trực tiếp nội dung
- 🖼️ **File PNG/JPG**: Dùng OCR nhận diện text (hỗ trợ tiếng Việt + tiếng Anh)

**Model AI:** `qwen/qwen3-vl-235b-a22b-thinking` - Model AI mạnh mẽ từ Qwen

---

## 🚀 Cách chạy

### Cách 1: Double-click file BAT (Dễ nhất)
```
Double-click: run_file_analyzer.bat
```
- ✅ Tự động cài đặt thư viện nếu thiếu
- ✅ Tự động mở trình duyệt
- ✅ Đơn giản nhất

### Cách 2: Chạy bằng Python
```bash
# Bước 1: Cài đặt thư viện (chỉ lần đầu)
pip install gradio easyocr openai pillow

# Bước 2: Chạy chatbot
python chatbot_file_analyzer.py
```

---

## 💻 Giao diện Chatbot

### Truy cập chatbot tại:
```
http://localhost:7860
```

### Layout:
```
┌─────────────────────────────────────────────────────┐
│  🤖 AI File Analyzer Chatbot                        │
├──────────────────────────┬──────────────────────────┤
│  💬 Chat với AI          │  📝 Nội dung trích xuất  │
│  (Hiển thị kết quả)      │  (Text từ file)         │
├──────────────────────────┴──────────────────────────┤
│  ❓ Câu hỏi của bạn (tùy chọn)                      │
├─────────────────────────────────────────────────────┤
│  📁 Upload file TXT/PNG                             │
├─────────────────────────────────────────────────────┤
│  [🚀 Gửi & Phân tích]  [🗑️ Xóa chat]              │
└─────────────────────────────────────────────────────┘
```

---

## 📖 Cách sử dụng

### Bước 1: Upload file
- Click nút **"📁 Upload file"**
- Chọn file TXT hoặc PNG/JPG từ máy tính

### Bước 2: Đặt câu hỏi (Tùy chọn)
- Nhập câu hỏi cụ thể vào ô **"❓ Câu hỏi của bạn"**
- Hoặc để trống để AI tự động phân tích toàn diện

### Bước 3: Nhấn "🚀 Gửi & Phân tích"
- AI sẽ đọc file và trả lời câu hỏi
- Kết quả hiển thị trong khung chat bên trái
- Nội dung text gốc hiển thị bên phải

---

## 💡 Ví dụ sử dụng

### Ví dụ 1: Phân tích tổng quát (không đặt câu hỏi)
```
1. Upload: bao_cao_tai_chinh.png
2. Câu hỏi: [Để trống]
3. Nhấn: 🚀 Gửi & Phân tích

→ AI sẽ tự động:
  - Tóm tắt nội dung
  - Trích xuất thông tin quan trọng
  - Phân tích cấu trúc tài liệu
```

### Ví dụ 2: Trích xuất số liệu cụ thể
```
1. Upload: bao_cao_tai_chinh.png
2. Câu hỏi: "Trích xuất tất cả các số liệu tài chính"
3. Nhấn: 🚀 Gửi & Phân tích

→ AI sẽ tìm và liệt kê tất cả số liệu tài chính
```

### Ví dụ 3: Tìm thông tin cụ thể
```
1. Upload: hop_dong.txt
2. Câu hỏi: "Tìm tên công ty, địa chỉ, và số điện thoại"
3. Nhấn: 🚀 Gửi & Phân tích

→ AI sẽ tìm và trích xuất thông tin đó
```

### Ví dụ 4: So sánh và phân tích
```
1. Upload: bao_cao_quy_2.png
2. Câu hỏi: "So sánh doanh thu và lợi nhuận giữa các tháng"
3. Nhấn: 🚀 Gửi & Phân tích

→ AI sẽ phân tích và so sánh
```

---

## 🎯 Các câu hỏi gợi ý

### Phân tích tài chính
- "Trích xuất tất cả các số liệu tài chính"
- "Tính tổng doanh thu và lợi nhuận"
- "So sánh các chỉ số tài chính"
- "Phân tích xu hướng tăng/giảm"

### Trích xuất thông tin
- "Tìm tất cả ngày tháng trong tài liệu"
- "Liệt kê tất cả tên công ty và địa chỉ"
- "Trích xuất số điện thoại và email"
- "Tìm các số tài khoản ngân hàng"

### Tóm tắt
- "Tóm tắt nội dung chính"
- "Liệt kê các điểm quan trọng"
- "Phân tích ý chính của tài liệu"

### Chuyển đổi format
- "Chuyển nội dung thành bảng markdown"
- "Tạo danh sách từ nội dung"
- "Định dạng lại dữ liệu"

---

## ⚙️ Tính năng

### ✅ Hỗ trợ file
- TXT (UTF-8, Latin-1)
- PNG, JPG, JPEG, BMP, TIFF, GIF

### ✅ OCR (Nhận diện ảnh)
- Tiếng Việt ✓
- Tiếng Anh ✓
- Độ tin cậy: 80-95%
- Nhận diện: Chữ cái, số, ký tự đặc biệt

### ✅ AI Model
- Model: qwen/qwen3-vl-235b-a22b-thinking
- Max tokens: 4000
- Temperature: 0.7

### ✅ Giao diện
- Hiển thị chat history
- Preview nội dung file
- Xóa chat và làm mới
- Responsive design

---

## 📊 Workflow

```
┌──────────────┐
│ Upload File  │
└──────┬───────┘
       │
       ├─── TXT ───→ Đọc trực tiếp
       │
       └─── PNG ───→ OCR nhận diện
              │
              ↓
       ┌──────────────┐
       │ Trích xuất   │
       │ Text         │
       └──────┬───────┘
              │
              ↓
       ┌──────────────┐
       │ Gửi đến AI   │
       │ Model Qwen   │
       └──────┬───────┘
              │
              ↓
       ┌──────────────┐
       │ Phân tích &  │
       │ Trả lời     │
       └──────┬───────┘
              │
              ↓
       ┌──────────────┐
       │ Hiển thị kết │
       │ quả trong    │
       │ Chatbot      │
       └──────────────┘
```

---

## ⚠️ Lưu ý quan trọng

### 1. Lần đầu chạy
- ⏰ Tải model OCR (100-200MB), mất 3-5 phút
- 💾 Model sẽ được lưu cache, lần sau nhanh hơn

### 2. Chất lượng ảnh
- ✅ Ảnh rõ nét → Kết quả tốt
- ❌ Ảnh mờ, nhiễu → Kết quả kém
- 💡 Nên chụp ảnh có độ phân giải cao

### 3. Kích thước file
- Ảnh quá lớn (>10MB) có thể chậm
- Nên resize ảnh xuống 2000-3000px

### 4. Độ chính xác OCR
- Tiếng Việt có dấu: 80-90%
- Tiếng Anh: 90-95%
- Số liệu: 85-95%
- Chữ viết tay: 50-70% (không khuyến khích)

### 5. API Key
- Key trong code là ví dụ
- Nên thay bằng key thực của bạn tại [OpenRouter](https://openrouter.ai/)

---

## 🐛 Xử lý lỗi

### Lỗi: "Không thể tải model OCR"
```bash
pip uninstall easyocr
pip install easyocr --no-cache-dir
```

### Lỗi: "API key không hợp lệ"
- Kiểm tra API key trong file `chatbot_file_analyzer.py`
- Đảm bảo có internet để gọi API

### Lỗi: "Không đọc được file"
- Kiểm tra định dạng file (phải là TXT hoặc PNG/JPG)
- Kiểm tra file có bị hỏng không
- Thử với file khác

### Lỗi: "Port 7860 đã được sử dụng"
```python
# Sửa trong file chatbot_file_analyzer.py
demo.launch(server_port=7861)  # Đổi sang port khác
```

---

## 🔧 Cấu hình nâng cao

### Thay đổi model AI
```python
# Trong file chatbot_file_analyzer.py, dòng ~127
model="qwen/qwen3-vl-235b-a22b-thinking",

# Có thể thay bằng:
# model="openai/gpt-4"
# model="anthropic/claude-3-opus"
```

### Thay đổi ngôn ngữ OCR
```python
# Dòng ~21
ocr_reader = easyocr.Reader(['vi', 'en'], gpu=False)

# Thêm ngôn ngữ khác:
# ocr_reader = easyocr.Reader(['vi', 'en', 'ch_sim', 'ja'], gpu=False)
```

### Bật GPU cho OCR (nếu có GPU)
```python
# Dòng ~21
ocr_reader = easyocr.Reader(['vi', 'en'], gpu=True)  # Đổi False → True
```

### Tạo public link (share)
```python
# Dòng ~298
demo.launch(
    share=True,  # Đổi False → True
    ...
)
```

---

## 📁 Cấu trúc file

```
FPT-vinaMILF/
├── chatbot_file_analyzer.py      ← File chính (chatbot)
├── run_file_analyzer.bat          ← File chạy nhanh (Windows)
├── HUONG_DAN_FILE_ANALYZER.md     ← File này
├── image_ocr_reader.py            ← Module OCR (tham khảo)
└── pdf_reader.py                  ← Module PDF (tham khảo)
```

---

## 🎓 Ví dụ thực tế

### Kịch bản 1: Phân tích báo cáo tài chính FPT
```
File: 20250422 - FPT - BCTC cong ty me Quy 1 nam 2025.png

Câu hỏi: "Trích xuất doanh thu, lợi nhuận, tổng tài sản và nợ phải trả"

Kết quả AI:
- Doanh thu: XXX tỷ đồng
- Lợi nhuận: XXX tỷ đồng
- Tổng tài sản: XXX tỷ đồng
- Nợ phải trả: XXX tỷ đồng
```

### Kịch bản 2: Đọc hợp đồng
```
File: hop_dong_dich_vu.txt

Câu hỏi: "Tóm tắt các điều khoản quan trọng"

Kết quả AI:
1. Bên A: ...
2. Bên B: ...
3. Thời hạn: ...
4. Giá trị hợp đồng: ...
5. Các điều khoản: ...
```

### Kịch bản 3: Đọc hóa đơn
```
File: hoa_don.jpg

Câu hỏi: "Liệt kê sản phẩm, số lượng, đơn giá"

Kết quả AI:
Bảng sản phẩm:
| Sản phẩm | Số lượng | Đơn giá | Thành tiền |
|----------|----------|---------|------------|
| ...      | ...      | ...     | ...        |
```

---

## 💪 Công dụng thực tế

1. ✅ **Phân tích báo cáo tài chính** từ ảnh chụp
2. ✅ **Đọc và tóm tắt văn bản** dài
3. ✅ **Trích xuất dữ liệu** từ form, hóa đơn
4. ✅ **Chuyển ảnh thành text** có thể edit
5. ✅ **Phân tích tài liệu** hợp đồng, biên bản
6. ✅ **So sánh số liệu** giữa các kỳ
7. ✅ **Tìm kiếm thông tin** cụ thể trong tài liệu

---

## 📞 Hỗ trợ

Nếu gặp vấn đề:
1. Đọc lại phần "Xử lý lỗi"
2. Kiểm tra đã cài đủ thư viện chưa
3. Kiểm tra API key còn hoạt động không
4. Thử với file mẫu khác

---

## 🎉 Chúc bạn sử dụng thành công!
