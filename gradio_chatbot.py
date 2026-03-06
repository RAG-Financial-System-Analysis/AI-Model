import gradio as gr
import pandas as pd
import os
from openai import OpenAI

# Khởi tạo OpenAI client với OpenRouter
client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key="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",
)

class FinancialChatbot:
    def __init__(self):
        self.excel_data = {}
        self.data_context = ""
        self.load_excel_files()
        
    def load_excel_files(self):
        """Đọc tất cả các file Excel trong thư mục"""
        excel_files = {
            'Bang_Can_Doi_Ke_Toan.xlsx': 'Bảng cân đối kế toán',
            'Bao_Cao_Ket_Qua_Hoat_Dong.xlsx': 'Báo cáo kết quả hoạt động kinh doanh',
            'Bang_So_Sanh_KQKD.xlsx': 'Bảng so sánh kết quả kinh doanh'
        }
        
        status_messages = []
        for filename, description in excel_files.items():
            if os.path.exists(filename):
                try:
                    excel_file = pd.ExcelFile(filename)
                    self.excel_data[description] = {}
                    
                    for sheet_name in excel_file.sheet_names:
                        df = pd.read_excel(filename, sheet_name=sheet_name)
                        self.excel_data[description][sheet_name] = df
                    
                    status_messages.append(f"✓ {description}")
                except Exception as e:
                    status_messages.append(f"✗ {description}: {e}")
        
        self.data_context = self.format_data_for_ai()
        return "\n".join(status_messages)
    
    def format_data_for_ai(self):
        """Chuyển đổi dữ liệu Excel thành text để gửi cho AI"""
        context = "Dưới đây là dữ liệu báo cáo tài chính:\n\n"
        
        for report_name, sheets in self.excel_data.items():
            context += f"### {report_name}\n"
            for sheet_name, df in sheets.items():
                context += f"\n**{sheet_name}:**\n"
                context += df.to_string(index=False, max_rows=100)
                context += "\n\n"
        
        return context
    
    def chat(self, message, history):
        """Xử lý tin nhắn và trả về phản hồi"""
        if not message.strip():
            return history
        
        # Tạo messages cho API
        messages = [
            {
                "role": "system",
                "content": f"""Bạn là trợ lý AI chuyên về phân tích báo cáo tài chính. 
Nhiệm vụ của bạn là trả lời các câu hỏi dựa trên dữ liệu báo cáo tài chính được cung cấp.

{self.data_context}

Hãy trả lời bằng tiếng Việt, chính xác, chi tiết và dễ hiểu. 
Khi trích dẫn số liệu, hãy nêu rõ nguồn gốc (từ báo cáo nào, kỳ nào).
Nếu câu hỏi không liên quan đến dữ liệu có sẵn, hãy thông báo lịch sự.
Format câu trả lời với markdown để dễ đọc."""
            }
        ]
        
        # Thêm lịch sử hội thoại
        for user_msg, assistant_msg in history:
            messages.append({"role": "user", "content": user_msg})
            if assistant_msg:
                messages.append({"role": "assistant", "content": assistant_msg})
        
        # Thêm tin nhắn hiện tại
        messages.append({"role": "user", "content": message})
        
        try:
            # Gọi API
            completion = client.chat.completions.create(
                model="qwen/qwen-2.5-72b-instruct",
                messages=messages,
                temperature=0.3,
                max_tokens=2000,
                stream=True  # Enable streaming
            )
            
            # Stream response
            response = ""
            for chunk in completion:
                if chunk.choices[0].delta.content:
                    response += chunk.choices[0].delta.content
                    # Update history với response hiện tại
                    history_copy = history + [[message, response]]
                    yield history_copy
            
        except Exception as e:
            error_msg = f"⚠️ Lỗi: {str(e)}"
            yield history + [[message, error_msg]]

# Khởi tạo chatbot
bot = FinancialChatbot()
load_status = bot.load_excel_files()

# Tạo giao diện Gradio
with gr.Blocks(title="Chatbot Phân Tích Báo Cáo Tài Chính") as demo:
    
    gr.Markdown(
        """
        # 🤖 Chatbot Phân Tích Báo Cáo Tài Chính
        
        Trợ lý AI giúp bạn phân tích và trả lời câu hỏi về báo cáo tài chính.
        """
    )
    
    with gr.Accordion("📊 Trạng thái dữ liệu", open=False):
        gr.Markdown(f"```\n{load_status}\n```")
        gr.Markdown(
            """
            **Dữ liệu đã tải:**
            - Bảng cân đối kế toán (30/9/2025 và 31/12/2024)
            - Báo cáo kết quả hoạt động kinh doanh (Quý 3/2025)
            - Bảng so sánh kết quả kinh doanh
            """
        )
    
    with gr.Accordion("💡 Gợi ý câu hỏi", open=False):
        gr.Markdown(
            """
            ### Về Doanh thu & Lợi nhuận:
            - "Doanh thu quý 3 năm 2025 là bao nhiêu?"
            - "Lợi nhuận sau thuế quý 3/2025 tăng bao nhiêu % so với cùng kỳ?"
            - "Phân tích biên lợi nhuận gộp của công ty"
            
            ### Về Tài sản:
            - "Tổng tài sản tại ngày 30/9/2025 là bao nhiêu?"
            - "Tài sản ngắn hạn và dài hạn chiếm bao nhiêu %?"
            - "Các khoản đầu tư tài chính có thay đổi gì?"
            
            ### Về Nợ & Vốn:
            - "Tổng nợ phải trả là bao nhiêu?"
            - "Tỷ lệ nợ/vốn chủ sở hữu như thế nào?"
            - "Vốn chủ sở hữu có tăng không?"
            
            ### Phân tích tổng hợp:
            - "So sánh tình hình tài chính giữa quý 3/2025 và quý 3/2024"
            - "Những điểm nổi bật trong báo cáo tài chính"
            - "Đánh giá khả năng thanh toán của công ty"
            """
        )
    
    # Chatbot interface
    chatbot = gr.Chatbot(
        height=500,
        show_label=False
    )
    
    with gr.Row():
        msg = gr.Textbox(
            placeholder="Nhập câu hỏi của bạn về báo cáo tài chính...",
            show_label=False,
            scale=9,
            container=False
        )
        submit = gr.Button("Gửi", variant="primary", scale=1)
    
    with gr.Row():
        clear = gr.Button("🗑️ Xóa lịch sử", size="sm")
        
    # Examples
    gr.Examples(
        examples=[
            "Doanh thu quý 3 năm 2025 là bao nhiêu?",
            "Lợi nhuận sau thuế quý 3/2025 so với cùng kỳ thay đổi như thế nào?",
            "Tổng tài sản tại ngày 30/9/2025 là bao nhiêu?",
            "Phân tích tình hình tài chính của công ty",
            "Tỷ lệ nợ/vốn chủ sở hữu là bao nhiêu?",
        ],
        inputs=msg,
    )
    
    gr.Markdown(
        """
        ---
        **Model:** Qwen 2.5 72B Instruct | **Provider:** OpenRouter | **Ngôn ngữ:** Tiếng Việt
        """
    )
    
    # Event handlers
    msg.submit(bot.chat, [msg, chatbot], chatbot).then(
        lambda: "", None, msg
    )
    submit.click(bot.chat, [msg, chatbot], chatbot).then(
        lambda: "", None, msg
    )
    clear.click(lambda: None, None, chatbot)

if __name__ == "__main__":
    print("="*70)
    print("🚀 Khởi động Chatbot Phân Tích Báo Cáo Tài Chính")
    print("="*70)
    print(f"\n{load_status}\n")
    print("="*70)
    print("📱 Mở trình duyệt để sử dụng chatbot...")
    print("="*70)
    
    demo.launch(
        server_name="0.0.0.0",  # Cho phép truy cập từ mạng local
        server_port=7860,
        share=False,  # Đặt True nếu muốn share link public
        show_error=True,
        inbrowser=True  # Tự động mở trình duyệt
    )
