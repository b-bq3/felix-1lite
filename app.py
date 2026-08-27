"""
FELIX-1lite — Gradio chat interface for HuggingFace Spaces.
"""
import gradio as gr
import sys
import os
sys.path.insert(0, ".")
from felix import chat as felix_chat, CONFIG
CONFIG["device"] = "cpu"
SYSTEM_PROMPT = """انت فيليكس. نموذج لغوي صغير بالعربية الفصحى. اتكيف مع المستخدم. فلسفي لكن عملي. يحب الكود والافكار الجديدة."""
def respond(message, history):
    """Generate response with system prompt injection."""
    try:
        full_prompt = f"{SYSTEM_PROMPT}\n{message}"
        response = felix_chat(full_prompt, max_tokens=200, temperature=0.8)
        return response.strip()
    except Exception as e:
        return f"خطأ: {str(e)}"
with gr.Blocks(
    title="FELIX-1lite 🤖",
    theme=gr.themes.Soft(),
) as demo:
    gr.Markdown(
        """
        نموذج لغوي صغير (~25M parameters) بالعربية الفصحى.
        مبني من الصفر. فلسفي، إبداعي، يحب الكود.
        **المميزات:**
        - محادثة عامة
        - توليد أكواد
        - أفكار إبداعية
        - شخصية قابلة للتكيّف
        """
    )
    chatbot = gr.ChatInterface(
        fn=respond,
        examples=[
            "ما هو الذكاء الاصطناعي؟",
            "اعطني فكرة مشروع برمجي",
            "اكتب كود reverse string",
            "ما معنى الحياة؟",
            "كيف اتعلم البرمجة؟",
        ],
        title="تحدث مع فيليكس",
        description="اكتب بالعربية الفصحى. فيليكس يفهمك ويجاوبك.",
    )
if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=7860)
