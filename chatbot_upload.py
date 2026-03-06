"""
chatbot_upload.py
Chatbot hỗ trợ upload .txt và .png, phân tích bằng qwen/qwen3-vl-235b-a22b-thinking
Tương thích Gradio 6.x
"""

import base64, os
import gradio as gr
from openai import OpenAI

# ─── Cấu hình ─────────────────────────────────────────────────────────────────
API_KEY = "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"
MODEL   = "qwen/qwen3-vl-235b-a22b-thinking"

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=API_KEY,
)

SYSTEM_PROMPT = (
    "Bạn là trợ lý AI thông minh, có thể đọc hiểu văn bản và phân tích hình ảnh. "
    "Hãy trả lời bằng tiếng Việt, rõ ràng, chi tiết và dễ hiểu. "
    "Sử dụng markdown để định dạng câu trả lời khi cần thiết."
)

# ─── Tiện ích file ────────────────────────────────────────────────────────────

def read_txt(path: str) -> str:
    with open(path, "r", encoding="utf-8", errors="replace") as f:
        return f.read()

def to_b64(path: str) -> str:
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode()

def ext(path: str) -> str:
    return os.path.splitext(path)[1].lower()

def mime(path: str) -> str:
    e = ext(path)
    return {"png":"image/png","jpg":"image/jpeg","jpeg":"image/jpeg",
            "webp":"image/webp","gif":"image/gif"}.get(e.lstrip("."), "image/png")

# ─── Xây dựng message ────────────────────────────────────────────────────────

def build_user_content(text: str, file_path: str | None) -> list[dict]:
    """Tạo nội dung message cho API."""
    parts: list[dict] = []

    if file_path:
        e = ext(file_path)
        fname = os.path.basename(file_path)

        if e == ".txt":
            body = read_txt(file_path)
            full = (f"{text}\n\n--- NỘI DUNG FILE: {fname} ---\n{body}\n---"
                    if text.strip() else
                    f"--- NỘI DUNG FILE: {fname} ---\n{body}\n---")
            parts.append({"type": "text", "text": full})

        elif e in (".png", ".jpg", ".jpeg", ".webp", ".gif"):
            prompt = text.strip() or "Hãy phân tích và mô tả chi tiết hình ảnh này."
            parts.append({"type": "text", "text": prompt})
            data_url = f"data:{mime(file_path)};base64,{to_b64(file_path)}"
            parts.append({"type": "image_url", "image_url": {"url": data_url}})

        else:
            parts.append({"type": "text",
                          "text": f"⚠️ File '{fname}' không được hỗ trợ. Chỉ nhận .txt và .png."})
    else:
        if not text.strip():
            return []
        parts.append({"type": "text", "text": text})

    return parts

# ─── Chat handler ─────────────────────────────────────────────────────────────

def respond(message: dict, history: list[dict]):
    """
    Gradio 6 MultimodalTextbox trả về:
      message = {"text": "...", "files": ["path1", ...]}
    history = list of {"role": "user"/"assistant", "content": "..."}
    """
    text = (message.get("text") or "").strip()
    files = message.get("files") or []
    file_path = files[0] if files else None

    # Nhãn hiển thị trong chat
    if file_path:
        fname = os.path.basename(file_path)
        display = f"📎 **{fname}**\n{text}" if text else f"📎 **{fname}**"
    else:
        display = text

    if not text and not file_path:
        return

    # Xây messages gửi API
    api_messages: list[dict] = [{"role": "system", "content": SYSTEM_PROMPT}]

    # Lịch sử
    for m in history:
        api_messages.append({"role": m["role"], "content": m["content"]})

    # Tin nhắn hiện tại
    user_content = build_user_content(text, file_path)
    if not user_content:
        return

    api_messages.append({"role": "user", "content": user_content})

    # Thêm tin nhắn user vào history để hiển thị
    history.append({"role": "user", "content": display})
    history.append({"role": "assistant", "content": ""})
    yield history

    # Gọi API streaming
    try:
        stream = client.chat.completions.create(
            model=MODEL,
            messages=api_messages,
            stream=True,
            extra_headers={
                "HTTP-Referer": "https://localhost",
                "X-Title": "AI-File-Chatbot",
            },
        )
        response = ""
        for chunk in stream:
            delta = chunk.choices[0].delta.content
            if delta:
                response += delta
                history[-1]["content"] = response
                yield history

    except Exception as e:
        history[-1]["content"] = f"⚠️ **Lỗi kết nối:** {e}"
        yield history

# ─── Gradio UI ────────────────────────────────────────────────────────────────

css = """
#chatbot { height: 540px; }
footer { display: none !important; }
.tip-box { background: #f0f4ff; border-radius: 10px; padding: 12px 16px; margin-top: 8px; font-size: 0.9rem; }
"""

with gr.Blocks(
    title="🤖 AI File Analyzer",
    theme=gr.themes.Soft(primary_hue="indigo", secondary_hue="violet"),
    css=css,
) as demo:

    gr.Markdown(
        """
        # 🤖 AI File Analyzer Chatbot
        Upload file **`.txt`** hoặc **`.png`** · AI sẽ phân tích và trả lời câu hỏi của bạn.

        > **Model:** `qwen/qwen3-vl-235b-a22b-thinking` &nbsp;·&nbsp; **Provider:** OpenRouter
        """
    )

    with gr.Row():
        # ── Sidebar ──────────────────────────────────────────────────────────
        with gr.Column(scale=1, min_width=240):
            gr.Markdown("### 💡 Hướng dẫn")
            gr.Markdown(
                """
                <div class="tip-box">
                1. Nhấn biểu tượng 📎 để upload file<br>
                2. Gõ câu hỏi (hoặc để trống)<br>
                3. Nhấn <b>Enter</b> hoặc nút <b>Gửi</b>
                </div>
                """
            )
            gr.Markdown("### 💬 Câu hỏi gợi ý")
            gr.Markdown(
                """
                - *"Tóm tắt nội dung file này"*
                - *"Những điểm quan trọng là gì?"*
                - *"Mô tả chi tiết hình ảnh"*
                - *"Nhận xét về nội dung trên"*
                - *"Dịch nội dung sang tiếng Anh"*
                """
            )
            gr.Markdown("---")
            gr.Markdown("**Định dạng hỗ trợ:**\n- 📄 `.txt` — văn bản\n- 🖼️ `.png` / `.jpg` — hình ảnh")

        # ── Chat area ────────────────────────────────────────────────────────
        with gr.Column(scale=3):
            chatbot = gr.Chatbot(
                label="Hội thoại",
                elem_id="chatbot",
                type="messages",           # Gradio 6: dùng list[dict]
                show_copy_button=True,
                bubble_full_width=False,
                avatar_images=(None, "https://api.dicebear.com/7.x/bottts/svg?seed=qwen"),
            )

            chat_input = gr.MultimodalTextbox(
                placeholder="Nhập câu hỏi... hoặc upload file rồi nhấn Enter",
                show_label=False,
                file_types=[".txt", ".png", ".jpg", ".jpeg"],
                file_count="single",
                submit_btn=True,
            )

            clear_btn = gr.Button("🗑️ Xóa lịch sử", size="sm", variant="secondary")

    gr.Markdown(
        "---\n*Powered by [OpenRouter](https://openrouter.ai) · "
        "Model Qwen3 VL 235B Thinking · Hỗ trợ văn bản & hình ảnh*"
    )

    # ── Events ────────────────────────────────────────────────────────────────
    chat_input.submit(
        fn=respond,
        inputs=[chat_input, chatbot],
        outputs=chatbot,
    ).then(fn=lambda: {"text": "", "files": []}, outputs=chat_input)

    clear_btn.click(fn=lambda: [], outputs=chatbot)


# ─── Entry point ──────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("=" * 60)
    print("🚀  AI File Analyzer Chatbot  (Gradio 6)")
    print(f"    Model : {MODEL}")
    print("    URL   : http://localhost:7861")
    print("=" * 60)

    demo.launch(
        server_name="0.0.0.0",
        server_port=7861,
        share=False,
        show_error=True,
        inbrowser=True,
    )
