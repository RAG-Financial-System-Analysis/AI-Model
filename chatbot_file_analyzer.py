import gradio as gr
from openai import OpenAI
import easyocr
import os
from PIL import Image

# Khởi tạo OpenAI client với OpenRouter
client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key="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",
)

# Khởi tạo EasyOCR reader
ocr_reader = None

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

def analyze_with_ai(content, user_question):
    """
    Gửi nội dung đến AI để phân tích
    
    Args:
        content: Nội dung text cần phân tích
        user_question: Câu hỏi của người dùng
        
    Returns:
        Câu trả lời từ AI
    """
    try:
        # Tạo prompt
        if user_question and user_question.strip():
            prompt = f"""Nội dung tài liệu:
{content}

Câu hỏi của người dùng: {user_question}

Hãy trả lời câu hỏi dựa trên nội dung tài liệu trên."""
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
            model="qwen/qwen3-vl-235b-a22b-thinking",
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
        return f"❌ Lỗi khi gọi API: {str(e)}"

def process_file(file, user_question, chat_history):
    """
    Xử lý file upload và trả lời người dùng
    
    Args:
        file: File object từ Gradio
        user_question: Câu hỏi của người dùng
        chat_history: Lịch sử chat
        
    Returns:
        Tuple (chat_history, output_text)
    """
    if file is None:
        error_msg = "⚠️ Vui lòng upload file TXT hoặc PNG!"
        chat_history.append({"role": "user", "content": user_question if user_question else "Upload file"})
        chat_history.append({"role": "assistant", "content": error_msg})
        return chat_history, ""
    
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
        else:
            error_msg = f"❌ Không hỗ trợ định dạng file {file_ext}. Chỉ hỗ trợ TXT hoặc PNG/JPG!"
            chat_history.append({"role": "user", "content": user_question if user_question else f"Upload file {file_ext}"})
            chat_history.append({"role": "assistant", "content": error_msg})
            return chat_history, ""
        
        # Kiểm tra nội dung
        if not content or content.startswith("❌"):
            chat_history.append({"role": "user", "content": user_question if user_question else "Upload file"})
            chat_history.append({"role": "assistant", "content": content})
            return chat_history, ""
        
        # Hiển thị nội dung đã trích xuất
        preview = content[:500] + "..." if len(content) > 500 else content
        
        # Phân tích với AI
        ai_response = analyze_with_ai(content, user_question)
        
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
        
        return chat_history, content
    
    except Exception as e:
        error_msg = f"❌ Lỗi xử lý file: {str(e)}"
        chat_history.append({"role": "user", "content": user_question if user_question else "Upload file"})
        chat_history.append({"role": "assistant", "content": error_msg})
        return chat_history, ""

def clear_chat():
    """Xóa lịch sử chat"""
    return [], "", None

# Tạo giao diện Gradio
with gr.Blocks(title="🤖 AI File Analyzer Chatbot") as demo:
    gr.Markdown("""
    # 🤖 AI File Analyzer Chatbot
    
    ### 📤 Upload file TXT hoặc PNG để AI phân tích
    
    **Hỗ trợ:**
    - 📄 **File TXT**: Đọc trực tiếp nội dung
    - 🖼️ **File PNG/JPG**: Dùng OCR nhận diện text (tiếng Việt + tiếng Anh)
    
    **Model AI:** `qwen/qwen3-vl-235b-a22b-thinking`
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
                    label="📁 Upload file (TXT hoặc PNG/JPG)",
                    file_types=[".txt", ".png", ".jpg", ".jpeg", ".bmp"],
                    type="filepath"
                )
            
            with gr.Row():
                submit_btn = gr.Button("🚀 Gửi & Phân tích", variant="primary", scale=2)
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
    - Hoặc để trống để AI tự động phân tích toàn diện
    """)
    
    # Event handlers
    submit_btn.click(
        fn=process_file,
        inputs=[file_input, user_question, chatbot],
        outputs=[chatbot, extracted_content]
    )
    
    clear_btn.click(
        fn=clear_chat,
        inputs=[],
        outputs=[chatbot, user_question, file_input]
    )
    
    # Enter key to submit
    user_question.submit(
        fn=process_file,
        inputs=[file_input, user_question, chatbot],
        outputs=[chatbot, extracted_content]
    )

# Khởi chạy ứng dụng
if __name__ == "__main__":
    print("\n" + "="*50)
    print("🚀 Đang khởi động AI File Analyzer Chatbot...")
    print("="*50 + "\n")
    
    demo.launch(
        server_name="0.0.0.0",  # Cho phép truy cập từ mạng LAN
        server_port=7860,
        share=False,  # Đặt True nếu muốn tạo link public
        inbrowser=True,  # Tự động mở trình duyệt
        theme=gr.themes.Soft()  # Theme được chuyển sang launch() trong Gradio 6.0
    )
