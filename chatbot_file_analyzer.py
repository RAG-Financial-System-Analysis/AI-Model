import gradio as gr
from openai import OpenAI
import easyocr
import os
from PIL import Image
import pandas as pd

# Khởi tạo OpenAI client với OpenRouter
client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key="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",
)

# Khởi tạo EasyOCR reader
ocr_reader = None

# Token limit constants
MAX_TOTAL_TOKENS = 131000  # Giới hạn tổng cộng
MAX_OUTPUT_TOKENS = 4000   # Token cho output
MAX_INPUT_TOKENS = MAX_TOTAL_TOKENS - MAX_OUTPUT_TOKENS  # 127,000 tokens cho input
MAX_INPUT_CHARS = MAX_INPUT_TOKENS * 4  # Ước lượng 4 ký tự/token = 508,000 ký tự

def estimate_tokens(text):
    """Uớc lượng số token từ text"""
    return len(text) // 4  # 1 token ≈ 4 ký tự

def init_ocr_reader():
    """Khởi tạo OCR reader một lần duy nhất"""
    global ocr_reader
    if ocr_reader is None:
        print("🔄 Đang tải model OCR (lần đầu có thể mất vài phút)...")
        ocr_reader = easyocr.Reader(['vi', 'en'], gpu=False)
        print("✅ Đã tải xong model OCR!")
    return ocr_reader

def extract_text_from_image(image_path):
    """
    Đọc text từ ảnh bằng OCR
    
    Args:
        image_path: Đường dẫn đến file ảnh
        
    Returns:
        String chứa text đã nhận diện
    """
    try:
        # Khởi tạo OCR reader
        reader = init_ocr_reader()
        
        # Mở và kiểm tra ảnh
        img = Image.open(image_path)
        print(f"📷 Đang đọc ảnh: {img.size[0]}x{img.size[1]} pixels")
        
        # Nhận diện text
        print("🔍 Đang nhận diện text trong ảnh...")
        results = reader.readtext(image_path)
        
        # Trích xuất text
        text_content = ""
        for (bbox, text, confidence) in results:
            if confidence > 0.3:  # Chỉ lấy text có độ tin cậy > 0.3
                text_content += text + "\n"
        
        print(f"✅ Đã nhận diện được {len(results)} đoạn text")
        return text_content.strip()
    
    except Exception as e:
        return f"❌ Lỗi khi đọc ảnh: {str(e)}"

def extract_text_from_txt(txt_path):
    """
    Đọc nội dung file TXT
    
    Args:
        txt_path: Đường dẫn đến file TXT
        
    Returns:
        String chứa nội dung file
    """
    try:
        with open(txt_path, 'r', encoding='utf-8') as f:
            content = f.read()
        print(f"📄 Đã đọc file TXT: {len(content)} ký tự")
        return content
    except UnicodeDecodeError:
        # Thử encoding khác nếu utf-8 không được
        try:
            with open(txt_path, 'r', encoding='latin-1') as f:
                content = f.read()
            print(f"📄 Đã đọc file TXT (latin-1): {len(content)} ký tự")
            return content
        except Exception as e:
            return f"❌ Lỗi khi đọc file TXT: {str(e)}"
    except Exception as e:
        return f"❌ Lỗi khi đọc file TXT: {str(e)}"

def extract_text_from_csv(csv_path):
    """
    Đọc nội dung file CSV và chuyển thành text
    
    Args:
        csv_path: Đường dẫn đến file CSV
        
    Returns:
        String chứa nội dung file dạng markdown table và thống kê
    """
    try:
        # Đọc CSV
        df = pd.read_csv(csv_path)
        print(f"📊 Đã đọc file CSV: {df.shape[0]} hàng, {df.shape[1]} cột")
        
        # Chuyển datetime columns sang string để tránh lỗi
        for col in df.columns:
            if df[col].dtype == 'datetime64[ns]' or pd.api.types.is_datetime64_any_dtype(df[col]):
                df[col] = df[col].astype(str)
        
        # Tạo header
        header = f"""## 📊 Thông tin File CSV:
- **Số dòng:** {df.shape[0]:,}
- **Số cột:** {df.shape[1]}
- **Tên các cột:** {', '.join(df.columns.tolist())}

"""
        
        # Tính toán số dòng tối đa có thể gửi
        # Dự trú khoảng 50,000 ký tự cho header, thống kê, markdown formatting
        available_chars = MAX_INPUT_CHARS - len(header) - 50000
        
        # Thử xuất toàn bộ dữ liệu trước
        full_csv = df.to_csv(index=False)
        
        if len(full_csv) <= available_chars:
            # Nếu toàn bộ dữ liệu vừa đủ, gửi hết
            print(f"   ✅ Gửi toàn bộ {df.shape[0]} dòng")
            content = header + f"""## 📋 Dữ liệu mẫu (20 dòng đầu):
{df.head(20).to_markdown(index=False)}

## 📈 Thống kê cơ bản:
{df.describe(include='all').to_markdown()}

## 📦 Dữ liệu đầy đủ:
{full_csv}
"""
        else:
            # Nếu quá lớn, tính toán số dòng có thể gửi
            avg_row_size = len(full_csv) // len(df)
            max_rows = min(len(df), available_chars // avg_row_size)
            
            print(f"   ⚠️ File quá lớn, chỉ gửi {max_rows}/{df.shape[0]} dòng")
            df_sample = df.head(max_rows)
            
            content = header + f"""## 📋 Dữ liệu mẫu (20 dòng đầu):
{df.head(20).to_markdown(index=False)}

## 📈 Thống kê cơ bản:
{df.describe(include='all').to_markdown()}

## 📦 Dữ liệu (tối đa {max_rows} dòng):
{df_sample.to_csv(index=False)}

⚠️ **Lưu ý:** File có {df.shape[0]:,} dòng. Đã gửi {max_rows:,} dòng để tối ưu hoá token.
"""
        
        return content
    
    except Exception as e:
        return f"❌ Lỗi khi đọc file CSV: {str(e)}"

def extract_text_from_excel(excel_path):
    """
    Đọc nội dung file Excel và chuyển thành text
    
    Args:
        excel_path: Đường dẫn đến file Excel
        
    Returns:
        String chứa nội dung tất cả các sheet trong file
    """
    try:
        # Đọc tất cả sheets
        excel_file = pd.ExcelFile(excel_path)
        sheet_names = excel_file.sheet_names
        print(f"📊 Đã đọc file Excel: {len(sheet_names)} sheet")
        
        # Tạo header
        header = f"""## 📊 Thông tin File Excel:
- **Số sheet:** {len(sheet_names)}
- **Tên các sheet:** {', '.join(sheet_names)}
- **Đây là báo cáo tài chính** với các bảng: Bảng cân đối kế toán, Kết quả kinh doanh, Lưu chuyển tiền tệ, Thuyết minh...

---

"""
        
        content = header
        available_chars = MAX_INPUT_CHARS - len(header) - 50000  # Dự trú cho formatting
        current_size = 0
        
        # Đọc từng sheet
        for idx, sheet_name in enumerate(sheet_names, 1):
            df = pd.read_excel(excel_path, sheet_name=sheet_name)
            print(f"   Sheet '{sheet_name}': {df.shape[0]} hàng, {df.shape[1]} cột")
            
            # Chuyển datetime columns sang string để tránh lỗi
            for col in df.columns:
                if df[col].dtype == 'datetime64[ns]' or pd.api.types.is_datetime64_any_dtype(df[col]):
                    df[col] = df[col].astype(str)
            
            # Chuyển column names sang string để tránh lỗi
            df.columns = df.columns.astype(str)
            
            # Tính toán số dòng có thể gửi cho sheet này
            full_csv = df.to_csv(index=False)
            remaining_chars = available_chars - current_size
            
            sheet_header = f"""### 📄 Sheet {idx}/{len(sheet_names)}: {sheet_name}
- **Số dòng:** {df.shape[0]:,}
- **Số cột:** {df.shape[1]}
- **Tên các cột:** {', '.join(df.columns.tolist())}

"""
            
            if len(full_csv) + len(sheet_header) + 5000 <= remaining_chars:
                # Gửi toàn bộ sheet này
                print(f"      ✅ Gửi toàn bộ {df.shape[0]} dòng")
                sheet_content = sheet_header + f"""#### 📋 Dữ liệu mẫu (10 dòng đầu):
{df.head(10).to_markdown(index=False)}

#### 📈 Thống kê cơ bản:
{df.describe(include='all').to_markdown()}

#### 📦 Dữ liệu đầy đủ sheet này:
{full_csv}

{'='*80}

"""
            else:
                # Tính toán số dòng tối đa
                avg_row_size = len(full_csv) // max(len(df), 1)
                max_rows = min(len(df), (remaining_chars - len(sheet_header) - 5000) // max(avg_row_size, 1))
                max_rows = max(10, max_rows)  # Ít nhất 10 dòng
                
                print(f"      ⚠️ Sheet quá lớn, chỉ gửi {max_rows}/{df.shape[0]} dòng")
                df_sample = df.head(max_rows)
                
                sheet_content = sheet_header + f"""#### 📋 Dữ liệu mẫu (10 dòng đầu):
{df.head(10).to_markdown(index=False)}

#### 📈 Thống kê cơ bản:
{df.describe(include='all').to_markdown()}

#### 📦 Dữ liệu sheet này (tối đa {max_rows} dòng):
{df_sample.to_csv(index=False)}

⚠️ **Lưu ý:** Sheet này có {df.shape[0]:,} dòng. Đã gửi {max_rows:,} dòng để tối ưu token.

{'='*80}

"""
            
            # Kiểm tra xem còn chỗ không
            if current_size + len(sheet_content) > available_chars:
                content += f"\n\n⚠️ **Đã đạt giới hạn token. Không thể hiển thị thêm {len(sheet_names) - idx + 1} sheet.**\n"
                break
            
            content += sheet_content
            current_size += len(sheet_content)
        
        return content
    
    except Exception as e:
        return f"❌ Lỗi khi đọc file Excel: {str(e)}"

def analyze_with_ai(content, user_question, file_type=""):
    """
    Gửi nội dung đến AI để phân tích
    
    Args:
        content: Nội dung text cần phân tích
        user_question: Câu hỏi của người dùng
        file_type: Loại file (TXT, Image, CSV, Excel)
        
    Returns:
        Câu trả lời từ AI
    """
    try:
        # Tạo prompt dựa trên loại file
        if user_question and user_question.strip():
            prompt = f"""Nội dung tài liệu (Loại: {file_type}):
{content}

Câu hỏi của người dùng: {user_question}

Hãy trả lời câu hỏi dựa trên nội dung tài liệu trên. Nếu là báo cáo tài chính, hãy phân tích chi tiết các chỉ số và xu hướng."""
        else:
            if "Excel" in file_type or "CSV" in file_type:
                prompt = f"""Đây là dữ liệu từ file {file_type}. Hãy phân tích chi tiết:

1. **Tổng quan:** Mô tả loại dữ liệu, cấu trúc các sheet/bảng
2. **Phân tích số liệu:** 
   - Các chỉ số tài chính quan trọng
   - So sánh giữa các kỳ (nếu có)
   - Xu hướng tăng/giảm
3. **Điểm nổi bật:** Các con số đặc biệt, bất thường
4. **Kết luận:** Đánh giá tổng thể

Nội dung dữ liệu:
{content}"""
            else:
                prompt = f"""Hãy phân tích nội dung tài liệu sau và cung cấp:
1. Tóm tắt nội dung chính
2. Các thông tin quan trọng (số liệu, ngày tháng, tên công ty, địa chỉ, v.v.)
3. Các điểm đặc biệt cần chú ý

Nội dung tài liệu:
{content}"""
        
        # Gửi request đến AI
        print("🤖 Đang phân tích với AI...")
        completion = client.chat.completions.create(
            extra_headers={
                "HTTP-Referer": "https://your-site.com",
                "X-OpenRouter-Title": "File Analyzer Chatbot",
            },
            model="arcee-ai/trinity-large-preview:free",
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.7,
            max_tokens=4000
        )
        
        result = completion.choices[0].message.content
        print("✅ Đã nhận được phản hồi từ AI")
        return result
    
    except Exception as e:
        error_msg = str(e)
        # Kiểm tra nếu là lỗi context length
        if "maximum context length" in error_msg.lower() or "400" in error_msg:
            return """❌ **Dữ liệu người dùng lớn đối với model hiện tại của chúng tôi.**

📊 **Giới hạn:** Tối đa 400,000 từ (hoặc khoảng 130,000 tokens)

💡 **Giải pháp:**
1. **Giảm kích thước file:** Chỉ upload một phần dữ liệu (ví dụ: 1000-2000 dòng thay vì toàn bộ)
2. **Đặt câu hỏi cụ thể:** Thay vì để trống, hãy hỏi câu hỏi cụ thể để AI chỉ trích xuất thông tin cần thiết
3. **Chia nhỏ file:** Tách file lớn thành nhiều file nhỏ hơn

Bạn vui lòng thử lại với file nhỏ hơn nhé! 🙏"""
        else:
            return f"❌ Lỗi khi gọi API: {error_msg}"

def process_file(file, user_question, chat_history):
    """
    Xử lý file upload và trả lời người dùng
    
    Args:
        file: File object từ Gradio
        user_question: Câu hỏi của người dùng
        chat_history: Lịch sử chat
        
    Returns:
        Tuple (chat_history, output_text, cleared_question)
    """
    if file is None:
        error_msg = "⚠️ Vui lòng upload file TXT hoặc PNG!"
        chat_history.append({"role": "user", "content": user_question if user_question else "Upload file"})
        chat_history.append({"role": "assistant", "content": error_msg})
        return chat_history, "", ""
    
    try:
        # Lấy đường dẫn và extension file
        file_path = file.name
        file_ext = os.path.splitext(file_path)[1].lower()
        
        print(f"\n{'='*50}")
        print(f"📁 Nhận được file: {os.path.basename(file_path)}")
        print(f"📋 Định dạng: {file_ext}")
        
        # Đọc nội dung file dựa vào loại file
        if file_ext == '.txt':
            # Đọc file TXT
            content = extract_text_from_txt(file_path)
            file_type = "TXT"
        elif file_ext in ['.png', '.jpg', '.jpeg', '.bmp', '.tiff', '.gif']:
            # Đọc file ảnh bằng OCR
            content = extract_text_from_image(file_path)
            file_type = "Image (OCR)"
        elif file_ext == '.csv':
            # Đọc file CSV
            content = extract_text_from_csv(file_path)
            file_type = "CSV"
        elif file_ext in ['.xlsx', '.xls']:
            # Đọc file Excel
            content = extract_text_from_excel(file_path)
            file_type = "Excel"
        else:
            error_msg = f"❌ Không hỗ trợ định dạng file {file_ext}. Chỉ hỗ trợ TXT, PNG/JPG, CSV, hoặc Excel!"
            chat_history.append({"role": "user", "content": user_question if user_question else f"Upload file {file_ext}"})
            chat_history.append({"role": "assistant", "content": error_msg})
            return chat_history, "", ""
        
        # Kiểm tra nội dung
        if not content or content.startswith("❌"):
            chat_history.append({"role": "user", "content": user_question if user_question else "Upload file"})
            chat_history.append({"role": "assistant", "content": content})
            return chat_history, "", ""
        
        # Hiển thị nội dung đã trích xuất
        preview = content[:500] + "..." if len(content) > 500 else content
        
        # Phân tích với AI
        ai_response = analyze_with_ai(content, user_question, file_type)
        
        # Tạo response cho user
        user_msg = user_question if user_question else f"Phân tích file {os.path.basename(file_path)}"
        
        bot_response = f"""### 📄 File: {os.path.basename(file_path)} ({file_type})

**Nội dung đã trích xuất:**
```
{preview}
```

**📊 Phân tích từ AI:**

{ai_response}
"""
        
        # Thêm vào chat history
        chat_history.append({"role": "user", "content": user_msg})
        chat_history.append({"role": "assistant", "content": bot_response})
        
        print(f"✅ Hoàn thành xử lý file!")
        print(f"{'='*50}\n")
        
        return chat_history, content, ""  # Clear question input
    
    except Exception as e:
        error_msg = f"❌ Lỗi xử lý file: {str(e)}"
        chat_history.append({"role": "user", "content": user_question if user_question else "Upload file"})
        chat_history.append({"role": "assistant", "content": error_msg})
        return chat_history, "", ""

def clear_chat():
    """Xóa lịch sử chat"""
    return [], "", None, ""

def stop_processing(chatbot, extracted, question):
    """Dừng xử lý - trả về state hiện tại để xóa loading"""
    return chatbot, extracted, question

# Tạo giao diện Gradio
with gr.Blocks(title="🤖 AI File Analyzer Chatbot") as demo:
    gr.Markdown("""
    # 🤖 AI File Analyzer Chatbot
    
    ### 📤 Upload file để AI phân tích và học dữ liệu
    
    **Hỗ trợ:**
    - 📄 **File TXT**: Đọc trực tiếp nội dung
    - 🖼️ **File PNG/JPG**: Dùng OCR nhận diện text (tiếng Việt + tiếng Anh)
    - 📊 **File CSV**: Phân tích dữ liệu bảng biểu, thống kê
    - 📈 **File Excel**: Đọc tất cả sheet, phân tích chi tiết
    
    **Model AI:** `arcee-ai/trinity-large-preview:free`
    """)
    
    with gr.Row():
        with gr.Column(scale=2):
            # Chatbot interface
            chatbot = gr.Chatbot(
                label="💬 Trò chuyện với AI",
                height=500,
                show_label=True
            )
            
            with gr.Row():
                user_question = gr.Textbox(
                    label="❓ Câu hỏi của bạn (tùy chọn)",
                    placeholder="Ví dụ: Trích xuất tất cả số liệu tài chính, Tóm tắt nội dung,...",
                    scale=4
                )
                
            with gr.Row():
                file_input = gr.File(
                    label="📁 Upload file (TXT, PNG/JPG, CSV, Excel)",
                    file_types=[".txt", ".png", ".jpg", ".jpeg", ".bmp", ".csv", ".xlsx", ".xls"],
                    type="filepath"
                )
            
            with gr.Row():
                submit_btn = gr.Button("🚀 Gửi & Phân tích", variant="primary", scale=2)
                stop_btn = gr.Button("⏹️ Dừng", variant="stop", scale=1)
                clear_btn = gr.Button("🗑️ Xóa chat", scale=1)
        
        with gr.Column(scale=1):
            gr.Markdown("### 📝 Nội dung đã trích xuất")
            extracted_content = gr.Textbox(
                label="",
                placeholder="Nội dung text sẽ hiển thị ở đây...",
                lines=20,
                max_lines=20,
                show_label=False
            )
    
    # Examples
    gr.Markdown("""
    ### 💡 Gợi ý câu hỏi:
    - "Trích xuất tất cả các số liệu tài chính"
    - "Tóm tắt nội dung chính"
    - "Liệt kê tất cả ngày tháng và số điện thoại"
    - "Phân tích báo cáo này"
    - "Tìm giá trị lớn nhất và nhỏ nhất trong dữ liệu"
    - "So sánh các cột dữ liệu"
    - "Tìm xu hướng trong dữ liệu"
    - Hoặc để trống để AI tự động phân tích toàn diện
    """)
    
    # Event handlers
    submit_event = submit_btn.click(
        fn=process_file,
        inputs=[file_input, user_question, chatbot],
        outputs=[chatbot, extracted_content, user_question]
    )
    
    # Enter key to submit
    submit_event_enter = user_question.submit(
        fn=process_file,
        inputs=[file_input, user_question, chatbot],
        outputs=[chatbot, extracted_content, user_question]
    )
    
    # Stop button - cancel và clear loading state
    stop_btn.click(
        fn=stop_processing,
        inputs=[chatbot, extracted_content, user_question],
        outputs=[chatbot, extracted_content, user_question],
        cancels=[submit_event, submit_event_enter],
        queue=False  # Không queue để xử lý ngay lập tức
    )
    
    clear_btn.click(
        fn=clear_chat,
        inputs=[],
        outputs=[chatbot, user_question, file_input, extracted_content]
    )

# Khởi chạy ứng dụng
if __name__ == "__main__":
    print("\n" + "="*50)
    print("🚀 Đang khởi động AI File Analyzer Chatbot...")
    print("="*50 + "\n")
    
    demo.launch(
        server_name="0.0.0.0",  # Cho phép truy cập từ mạng LAN
        server_port=None,  # Tự động tìm port trống (7860-7870)
        share=False,  # Đặt True nếu muốn tạo link public
        inbrowser=True,  # Tự động mở trình duyệt
        theme=gr.themes.Soft()  # Theme được chuyển sang launch() trong Gradio 6.0
    )